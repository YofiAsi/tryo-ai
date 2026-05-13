"""
Embed task service - creates JSONL files for candidate embedding tasks.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import IO, TYPE_CHECKING, Any, List, Optional

from common.consts.enums import CandidateStatus
from common.entity.candidate_entity import CandidateDocument, CandidateMetadata
from common.service.create_batch_task_service.base_create_batch_task_service import (
    BaseCreateBatchTaskService,
)

if TYPE_CHECKING:
    from common.entity.candidate_entity import ProcessingCandidate
    from common.repository.processing_candidate_repository import ProcessingCandidateRepository
    from common.service.batch_manager_client_service import BatchManagerClientService

logger = logging.getLogger(__name__)

# Embedding components that need to be processed
EMBEDDING_COMPONENTS_TO_MODELS = {
    "general": "text-embedding-3-large",
    "skills": "text-embedding-3-small",
    "work_experience": "text-embedding-3-small"
}


class CreateEmbedTaskService(BaseCreateBatchTaskService):
    """Service for creating embedding batch task JSONL files."""
    
    def __init__(self, 
                 batch_manager_client: BatchManagerClientService,
                 processing_candidate_repository: ProcessingCandidateRepository):
        """Initialize the service with repositories and batch manager client."""
        self.batch_manager_client = batch_manager_client
        self.processing_candidate_repository = processing_candidate_repository
   
    @property
    def endpoint(self) -> str:
        return "/v1/embeddings"

    async def create_tasks(self, 
        task_size: int,
        **kwargs: Any,
    ) -> List[str]:
        """
        Create multiple JSONL files for embedding tasks, split by task_size.
        Each candidate will generate 4 embedding tasks (one for each component).
        
        Args:
            task_size: Maximum number of embedding tasks per JSONL file
            
        Returns:
            List of batch task IDs created in batch manager
            
        Raises:
            Exception: If task creation fails
        """
        logger.info(f"Creating embedding JSONL files for candidates ready for vectorization (task_size: {task_size})")
        
        # Process candidates incrementally using iterator, creating batches as we go
        batch_task_ids = await self._process_candidates_incrementally_with_iterator(task_size)
        
        logger.info(f"Successfully created {len(batch_task_ids)} embedding batch tasks: {batch_task_ids}")
        return batch_task_ids
    
    async def _process_candidates_incrementally_with_iterator(self, task_size: int) -> List[str]:
        """Process candidates using iterator, creating embedding tasks when task_size is reached."""
        batch_task_ids: List[str] = []
        current_batch_tasks = []
        current_batch_candidates = []
        current_file = None
        file_path: Optional[str] = None
        file_counter = 0
        total_processed = 0
        total_skipped = 0
        
        try:
            # Iterate over candidates ready for embedding using iterator
            async for candidate in self.processing_candidate_repository.find_by_status_iterator("pending_vectorization"):
                try:
                    if not candidate.parsed_data:
                        logger.debug(f"Skipping candidate {candidate.id}: no parsed data")
                        total_skipped += 1
                        continue
                    
                    # Create embedding tasks for each component
                    embedding_tasks = self._create_embedding_tasks_for_candidate(candidate)
                    
                    # Open new JSONL file if needed
                    if current_file is None:
                        current_file, file_path = self._open_new_jsonl_file(file_counter)
                    
                    # Write JSONL entries for all embedding components of this candidate
                    tasks_written = 0
                    for task in embedding_tasks:
                        if self._write_jsonl_entry(current_file, task):
                            tasks_written += 1
                            current_batch_tasks.append(task)
                    
                    if tasks_written > 0:
                        total_processed += 1
                        current_batch_candidates.append(candidate)
                        logger.debug(f"Added {tasks_written} embedding tasks for candidate {candidate.id} to batch {file_counter}")
                    
                    # Check if we've reached task_size (counting individual embedding tasks, not candidates)
                    if len(current_batch_tasks) >= task_size - len(EMBEDDING_COMPONENTS_TO_MODELS):
                        current_file.close()
                        
                        if file_path is not None:
                            await self._finalize_batch(file_path, current_batch_candidates, batch_task_ids)
                        
                        current_batch_tasks = []
                        current_batch_candidates = []
                        current_file = None
                        file_path = None
                        file_counter += 1
                    
                except Exception as e:
                    logger.error(f"Error processing candidate {candidate.id}: {e}")
                    total_skipped += 1
                    continue
            
            # Handle remaining tasks in the last batch
            if current_batch_tasks and current_file is not None and file_path is not None:
                current_file.close()
                
                await self._finalize_batch(file_path, current_batch_candidates, batch_task_ids)
        
        finally:
            if current_file is not None:
                current_file.close()
        
        logger.info(
            f"Processed {total_processed} candidates into {len(batch_task_ids)} batches, "
            f"skipped {total_skipped} candidates"
        )
        return batch_task_ids
    

    async def _finalize_batch(self, file_path: str, current_batch_candidates: List[ProcessingCandidate], batch_task_ids: List[str]) -> None:
        batch_task_id = await self._send_single_jsonl_file_to_batch_manager(file_path)
        batch_task_ids.append(batch_task_id)
        
        await self._update_candidates_batch_and_status(
            current_batch_candidates, batch_task_id
        )
        
        self._cleanup_single_file(file_path)
    
    def _create_embedding_tasks_for_candidate(self, candidate: ProcessingCandidate) -> List[dict[str, Any]]:
        """Create embedding tasks for all components of a candidate."""
        embedding_tasks: List[dict[str, Any]] = []
        
        if not candidate.parsed_data:
            return embedding_tasks

        metadata = CandidateMetadata(**candidate.model_dump())
        candidate_document = CandidateDocument(
            **candidate.parsed_data.model_dump(), 
            metadata=metadata,
            status = CandidateStatus.PROCESSING,
            raw_cv = candidate.raw_cv,
        )
        
        for component in EMBEDDING_COMPONENTS_TO_MODELS.keys():
            text_content = self._extract_text_for_component(candidate_document, component)
            if text_content.strip():  # Only create task if there's content
                task = {
                    'candidate_id': str(candidate.id),
                    'component': component,
                    'text_content': text_content
                }
                embedding_tasks.append(task)
            else:
                logger.debug(f"Skipping empty {component} component for candidate {candidate.id}")
        
        return embedding_tasks
    
    def _extract_text_for_component(self, candidate_document: CandidateDocument, component: str) -> str:
        """Extract text content for a specific embedding component."""        
        if component == "general":
            return candidate_document.general_text
        
        elif component == "skills":
            return candidate_document.skills_text
        
        elif component == "work_experience":
            return candidate_document.work_experience_text
        
        return ""
    
    def _open_new_jsonl_file(self, file_counter: int) -> tuple[IO[Any], str]:
        """Open a new JSONL file for writing."""
        current_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'_embed_batch_{file_counter}.jsonl', 
            delete=False
        )
        logger.debug(f"Opened new embedding batch file {file_counter}: {current_file.name}")
        return current_file, current_file.name
    
    def _write_jsonl_entry(self, current_file: IO[Any], task: dict[str, Any]) -> bool:
        """Write a JSONL entry for an embedding task to the current file."""
        try:
            jsonl_entry = self._create_jsonl_entry(task)
            current_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')
            return True
            
        except Exception as e:
            logger.error(f"Failed to write JSONL entry for embedding task: {e}")
            return False
    
    def _create_jsonl_entry(self, task: dict[str, Any]) -> dict[str, Any]:
        """Create a JSONL entry for an embedding task."""
        model = EMBEDDING_COMPONENTS_TO_MODELS[task['component']]
        
        request_body = {
            "model": model,
            "input": task['text_content'],
            "encoding_format": "float"
        }
        
        custom_id = f"embed_{task['candidate_id']}_{task['component']}"
        
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": self.endpoint,
            "body": request_body
        }
    
    def _get_model_for_component(self, component: str) -> str:
        """Get the appropriate model for each embedding component."""
        if component == "general":
            return "text-embedding-3-large"
        else:
            return "text-embedding-3-small"
    
    async def _send_single_jsonl_file_to_batch_manager(self, jsonl_file_path: str) -> str:
        """Send a single JSONL file to batch manager and return batch task ID."""
        try:
            logger.info(f"Sending embedding JSONL file to batch manager: {jsonl_file_path}")
            batch_response = await self.batch_manager_client.create_batch_task(
                task_type="embedding",
                jsonl_file_path=jsonl_file_path,
                metadata={"embedding_components": EMBEDDING_COMPONENTS_TO_MODELS}
            )
            logger.info(f"Successfully created embedding batch task: {batch_response.id}")
            return batch_response.id
        except Exception as e:
            logger.error(f"Failed to create embedding batch task for file {jsonl_file_path}: {e}")
            raise
    
    def _cleanup_single_file(self, file_path: str) -> None:
        """Clean up a single temporary JSONL file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {file_path}: {e}")
    
    async def _update_candidates_batch_and_status(self, processing_candidates: List[ProcessingCandidate], batch_task_id: str) -> None:
        """Update ProcessingCandidate documents with batch_task_id and status to 'vectorizing'."""
        try:
            # Update candidates to vectorizing status with embed_batch_task_id
            for candidate in processing_candidates:
                candidate.status = "vectorizing"
                candidate.embed_batch_task_id = batch_task_id
                await candidate.save()
            
            logger.debug(f"Updated {len(processing_candidates)} candidates with embed_batch_task_id: {batch_task_id}")
            
        except Exception as e:
            logger.error(f"Error updating candidates with embed_batch_task_id and status: {e}")
            raise
