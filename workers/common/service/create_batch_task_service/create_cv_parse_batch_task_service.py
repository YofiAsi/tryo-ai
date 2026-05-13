"""
CV parse task service - creates JSONL files for CV parsing tasks using MinIO.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import IO, TYPE_CHECKING, Any, List
from uuid import UUID

from common.entity.candidate_entity import ParsedCandidate, ProcessingCandidate
from common.prompts.parse_cv_prompt import ParseCvPrompt
from common.service.create_batch_task_service.base_create_batch_task_service import (
    BaseCreateBatchTaskService,
)
from common.utils.minio_directory_structure import MinioDirectoryStructure

if TYPE_CHECKING:
    from common.repository.minio_repository import MinioRepository
    from common.repository.processing_candidate_repository import ProcessingCandidateRepository
    from common.service.batch_manager_client_service import BatchManagerClientService


logger = logging.getLogger(__name__)

class CreateCvParseBatchTaskService(BaseCreateBatchTaskService):
    """Service for creating CV parse batch task JSONL files using MinIO."""
    
    def __init__(self, 
                 minio_repository: MinioRepository, 
                 batch_manager_client: BatchManagerClientService,
                 processing_candidate_repository: ProcessingCandidateRepository):
        """Initialize the service with repositories and batch manager client."""
        self.minio_repository = minio_repository
        self.batch_manager_client = batch_manager_client
        self.processing_candidate_repository = processing_candidate_repository
   
    @property
    def endpoint(self) -> str:
        return "/v1/responses"
    
    @property
    def ai_model(self) -> str:
        return "gpt-5-mini"

    async def create_tasks(self, 
        task_size: int,
        **kwargs: Any,
    ) -> List[str]:
        """
        Create multiple JSONL files for CV parsing tasks, split by task_size.
        Processes files incrementally, creating candidates, JSONL files, and sending batches as it goes.
        
        Args:
            minio_directory: Base directory path in MinIO bucket (e.g., "test")
            task_size: Maximum number of tasks per JSONL file
            
        Returns:
            List of batch task IDs created in batch manager
            
        Raises:
            Exception: If task creation fails
        """
        minio_directory = kwargs.get("minio_directory")
        if not minio_directory:
            raise ValueError("minio_directory is required in kwargs")
        
        logger.info(f"Creating CV parse JSONL files from MinIO directory: {minio_directory} (task_size: {task_size})")
        
        # Initialize and validate directory structure
        dir_structure = self._initialize_directory_structure(minio_directory)
        
        # Process files incrementally, creating batches as we go
        batch_task_ids = await self._process_files_incrementally(dir_structure, task_size, minio_directory)
        
        logger.info(f"Successfully created {len(batch_task_ids)} batch tasks: {batch_task_ids}")
        return batch_task_ids
    
    async def _process_files_incrementally(self, dir_structure: MinioDirectoryStructure, task_size: int, minio_directory: str) -> List[str]:
        """Process files incrementally, creating candidates and JSONL files, sending batches when task_size is reached."""
        batch_task_ids: List[str] = []
        current_batch_candidates = []
        current_file = None
        file_counter = 0
        total_processed = 0
        total_skipped = 0
        
        try:
            # Iterate over original files
            for file_info in self.minio_repository.iterate_files_in_import_directory(dir_structure.original_directory):
                try:
                    # Get file_id from original CV stem (filename without extension)
                    file_id: UUID = UUID(dir_structure.extract_candidate_id_from_filename(file_info.object_name))
                    
                    # Check if corresponding extracted txt file exists
                    extracted_file_path: str = dir_structure.get_extracted_file_path(f"{file_id}.txt")
                    original_file_path: str = file_info.object_name
                    
                    if not self.minio_repository.file_exists(extracted_file_path):
                        logger.debug(f"Skipping {file_id}: extracted file {extracted_file_path} does not exist")
                        total_skipped += 1
                        continue
                    
                    raw_cv_content = self._get_candidate_cv_content_from_path(extracted_file_path)

                    # Create and save ProcessingCandidate document
                    processing_candidate = self._create_processing_candidate_document(
                        file_id, extracted_file_path, original_file_path, raw_cv_content
                    )
                    
                    # Open new JSONL file if needed
                    if current_file is None:
                        current_file, file_path = self._open_new_jsonl_file(file_counter)
                    
                    # Write JSONL entry for this candidate
                    if self._write_jsonl_entry_for_candidate(
                        current_file,
                        raw_cv_content,
                        processing_candidate
                    ):
                        total_processed += 1
                        current_batch_candidates.append(processing_candidate)
                        
                        logger.debug(f"Added candidate {file_id} to batch {file_counter}")
                        
                    # Check if we've reached task_size
                    if len(current_batch_candidates) >= task_size:
                        # Close current file and send batch
                        current_file.close()
                        
                        await self._finalize_batch(
                            file_path, minio_directory, current_batch_candidates, batch_task_ids, file_counter
                        )
                        
                        # Reset for next batch
                        current_batch_candidates = []
                        current_file = None
                        file_counter += 1
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_info.object_name}: {e}")
                    total_skipped += 1
                    continue
            
            # Handle remaining candidates in the last batch
            if current_batch_candidates and current_file is not None:
                current_file.close()
                
                await self._finalize_batch(
                    file_path, minio_directory, current_batch_candidates, batch_task_ids, file_counter
                )
        
        finally:
            # Ensure any open file is closed
            if current_file is not None:
                current_file.close()
        
        logger.info(
            f"Processed {total_processed} candidates into {len(batch_task_ids)} batches, "
            f"skipped {total_skipped} files"
        )
        return batch_task_ids
    
    async def _finalize_batch(self,
        file_path: str,
        minio_directory: str,
        current_batch_candidates: List[ProcessingCandidate],
        batch_task_ids: List[str],
        file_counter: int
    ) -> None:
        # Send batch to batch manager
        batch_task_id = await self._send_single_jsonl_file_to_batch_manager(
            file_path, minio_directory
        )
        batch_task_ids.append(batch_task_id)
        
        await self.processing_candidate_repository.bulk_create_candidates(current_batch_candidates)

        # Update candidates with batch_task_id and status
        await self._update_candidates_batch_and_status(
            current_batch_candidates, batch_task_id
        )
        
        # Clean up temporary file
        self._cleanup_single_file(file_path)
        
        logger.info(
            f"Completed batch {file_counter} with {len(current_batch_candidates)} "
            f"candidates (batch_task_id: {batch_task_id})"
        )

    def _create_processing_candidate_document(self,
        file_id: UUID,
        extracted_file_path: str,
        original_file_path: str,
        raw_cv_content: str
    ) -> ProcessingCandidate:
        """Create a ProcessingCandidate document from file information."""
        
        return ProcessingCandidate(
            file_id=file_id,
            original_cv_minio_path=original_file_path,
            txt_cv_minio_path=extracted_file_path,
            parsed_data=None,
            parse_model=self.ai_model,
            status="pending_parse",
            raw_cv=raw_cv_content,
        )
    
    def _open_new_jsonl_file(self, file_counter: int) -> tuple[IO[Any], str]:
        """Open a new JSONL file for writing."""
        current_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'_batch_{file_counter}.jsonl', 
            delete=False
        )
        logger.debug(f"Opened new batch file {file_counter}: {current_file.name}")
        return current_file, current_file.name
    
    def _write_jsonl_entry_for_candidate(self, current_file: IO[Any], content: str, candidate: ProcessingCandidate) -> bool:
        """Write a JSONL entry for a candidate to the current file."""
        try:
            jsonl_entry = self._create_jsonl_entry(candidate, content)
            current_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')
            return True
            
        except Exception as e:
            logger.error(f"Failed to write JSONL entry for candidate {candidate.id}: {e}")
            return False
    
    def _get_candidate_cv_content(self, candidate: ProcessingCandidate) -> str:
        """Get CV content for a candidate from MinIO."""
        try:
            content = self.minio_repository.download_file(candidate.txt_cv_minio_path)
            return content.decode('utf-8').strip()
        except Exception as e:
            logger.error(f"Failed to download CV content for candidate {candidate.id}: {e}")
            return ""
    
    def _get_candidate_cv_content_from_path(self, txt_cv_minio_path: str) -> str:
        """Get CV content from MinIO using file path."""
        try:
            content = self.minio_repository.download_file(txt_cv_minio_path)
            return content.decode('utf-8').strip()
        except Exception as e:
            logger.error(f"Failed to download CV content from path {txt_cv_minio_path}: {e}")
            return ""
    
    def _create_jsonl_entry(self, candidate: ProcessingCandidate, content_str: str) -> dict[str, Any]:
        """Create a JSONL entry for a candidate."""
        request_body = {
            "model": self.ai_model,
            "input": [
                {"role": "system", "content": ParseCvPrompt.render_system()},
                {"role": "user", "content": ParseCvPrompt.render_user(cv_text=content_str)}
            ],
            "text": self.convert_model_to_json_schema(ParsedCandidate)
        }
        
        return {
            "custom_id": str(candidate.id),
            "method": "POST",
            "url": self.endpoint,
            "body": request_body
        }
    
    def _close_current_file(self, current_file: IO[Any], file_counter: int, entries_count: int) -> None:
        """Close the current JSONL file and log the closure."""
        current_file.close()
        logger.debug(f"Closed batch file {file_counter} with {entries_count} entries")
        return None
    
    def _initialize_directory_structure(self, minio_directory: str) -> MinioDirectoryStructure:
        """Initialize and validate MinIO directory structure."""
        dir_structure = MinioDirectoryStructure(base_directory=minio_directory)
        dir_structure.validate_structure_exists(self.minio_repository)
        logger.info(f"Validated directory structure: {dir_structure}")
        return dir_structure
    
    async def _send_single_jsonl_file_to_batch_manager(self, jsonl_file_path: str, minio_directory: str) -> str:
        """Send a single JSONL file to batch manager and return batch task ID."""
        try:
            logger.info(f"Sending JSONL file to batch manager: {jsonl_file_path}")
            batch_response = await self.batch_manager_client.create_batch_task(
                task_type="cv_parsing",
                jsonl_file_path=jsonl_file_path,
                metadata={"minio_directory": minio_directory}
            )
            logger.info(f"Successfully created batch task: {batch_response.id}")
            return batch_response.id
        except Exception as e:
            logger.error(f"Failed to create batch task for file {jsonl_file_path}: {e}")
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
        """Update ProcessingCandidate documents with batch_task_id and status to 'parsing'."""
        try:
            updated_count = await self.processing_candidate_repository.update_batch_task_id_and_status(
                processing_candidates, batch_task_id, "parsing"
            )
            logger.debug(f"Updated {updated_count} candidates with batch_task_id: {batch_task_id}")
            
        except Exception as e:
            logger.error(f"Error updating candidates with batch_task_id and status: {e}")
            raise
