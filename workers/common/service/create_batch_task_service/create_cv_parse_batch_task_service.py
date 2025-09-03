"""
CV parse task service - creates JSONL files for CV parsing tasks using MinIO.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import IO, TYPE_CHECKING, Any, List
from uuid import uuid4

from tqdm import tqdm

from common.entity.candidate_entity import ParsedCandidate, ProcessingCandidate
from common.prompts.parse_cv_prompt import ParseCvPrompt
from common.service.create_batch_task_service.base_create_batch_task_service import (
    BaseCreateBatchTaskService,
)
from common.utils.minio_directory_structure import MinioDirectoryStructure

if TYPE_CHECKING:
    from common.repository.minio_repository import FileInfo, MinioRepository
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
    def model(self) -> str:
        return "gpt-4.1-mini"

    async def create_tasks(self, 
        task_size: int,
        **kwargs: Any,
    ) -> List[str]:
        """
        Create multiple JSONL files for CV parsing tasks, split by task_size.
        Creates ProcessingCandidate documents and sends files to batch manager.
        
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
        
        # Create ProcessingCandidate documents
        processing_candidates = await self._create_processing_candidates(dir_structure)
        
        # Create and send JSONL files to batch manager
        jsonl_files = self._create_jsonl_files(processing_candidates, task_size)
        batch_task_ids = await self._send_jsonl_files_to_batch_manager(jsonl_files, minio_directory)
        
        # Clean up and update status
        self._cleanup_temporary_files(jsonl_files)
        await self._update_candidates_status_to_parsing(processing_candidates)
        
        logger.info(f"Successfully created {len(batch_task_ids)} batch tasks: {batch_task_ids}")
        return batch_task_ids
    
    async def _create_processing_candidates(self, dir_structure: MinioDirectoryStructure) -> List[ProcessingCandidate]:
        """Create ProcessingCandidate documents from extracted directory files."""
        files = self._get_extracted_files(dir_structure)
        processing_candidates = []
        
        for file_info in tqdm(files, desc="Creating ProcessingCandidate documents", unit="file"):
            if not self._is_valid_text_file(file_info.object_name):
                continue
                
            try:
                content_str = self._download_and_validate_file_content(file_info.object_name)
                if not content_str:
                    continue
                
                processing_candidate = self._create_processing_candidate_document(
                    file_info.object_name, dir_structure
                )
                
                saved_candidate = await self.processing_candidate_repository.create_candidate(processing_candidate)
                processing_candidates.append(saved_candidate)
                
                candidate_id = dir_structure.extract_candidate_id_from_filename(file_info.object_name)
                logger.debug(f"Created ProcessingCandidate for {candidate_id}: {saved_candidate.id}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_info.object_name}: {e}")
                continue
        
        logger.info(f"Created {len(processing_candidates)} ProcessingCandidate documents")
        return processing_candidates
    
    def _get_extracted_files(self, dir_structure: MinioDirectoryStructure) -> List[FileInfo]:
        """Get list of files from the extracted directory."""
        try:
            files = self.minio_repository.list_files_in_directory(dir_structure.extracted_directory)
            logger.info(f"Found {len(files)} files in MinIO extracted directory: {dir_structure.extracted_directory}")
            return files
        except Exception as e:
            logger.error(f"Error listing files from MinIO directory {dir_structure.extracted_directory}: {e}")
            raise
    
    def _is_valid_text_file(self, object_name: str) -> bool:
        """Check if the file is a valid text file."""
        if not object_name.endswith('.txt'):
            logger.debug(f"Skipping non-text file: {object_name}")
            return False
        return True
    
    def _download_and_validate_file_content(self, object_name: str) -> str:
        """Download file content and validate it's not empty."""
        content = self.minio_repository.download_file(object_name)
        content_str = content.decode('utf-8').strip()
        
        if not content_str:
            logger.warning(f"Empty file content for: {object_name}")
            return ""
        
        return content_str
    
    def _create_processing_candidate_document(self, object_name: str, dir_structure: MinioDirectoryStructure) -> ProcessingCandidate:
        """Create a ProcessingCandidate document from file information."""
        original_path = dir_structure.get_corresponding_original_path(object_name)
        
        return ProcessingCandidate(
            file_id=uuid4(),
            original_cv_minio_path=original_path,
            txt_cv_minio_path=object_name,
            parsed_data=None,  # Will be populated after parsing
            status="pending_parse",
        )
    
    def _create_jsonl_files(self, processing_candidates: List[ProcessingCandidate], task_size: int) -> List[str]:
        """Create multiple JSONL files for CV analysis from ProcessingCandidate documents, split by task_size."""
        created_files = []
        current_file = None
        file_counter = 0
        entries_in_current_file = 0
        total_entries = 0
        
        try:
            for candidate in tqdm(processing_candidates, desc="Creating JSONL entries", unit="candidate"):
                # Open new file if needed
                if current_file is None:
                    current_file, file_path = self._open_new_jsonl_file(file_counter)
                    created_files.append(file_path)
                    entries_in_current_file = 0
                
                # Create and write JSONL entry
                if self._write_jsonl_entry_for_candidate(current_file, candidate):
                    entries_in_current_file += 1
                    total_entries += 1
                
                # Close current file if we've reached task_size
                if entries_in_current_file >= task_size:
                    self._close_current_file(current_file, file_counter, entries_in_current_file)
                    file_counter += 1
                    entries_in_current_file = 0
        
        finally:
            # Close the last file if it's still open
            if current_file is not None:
                self._close_current_file(current_file, file_counter, entries_in_current_file)
        
        logger.info(f"Created {len(created_files)} JSONL files with {total_entries} total entries")
        return created_files
    
    def _open_new_jsonl_file(self, file_counter: int) -> tuple[IO[Any], str]:
        """Open a new JSONL file for writing."""
        current_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'_batch_{file_counter}.jsonl', 
            delete=False
        )
        logger.debug(f"Opened new batch file {file_counter}: {current_file.name}")
        return current_file, current_file.name
    
    def _write_jsonl_entry_for_candidate(self, current_file: IO[Any], candidate: ProcessingCandidate) -> bool:
        """Write a JSONL entry for a candidate to the current file."""
        try:
            content_str = self._get_candidate_cv_content(candidate)
            if not content_str:
                return False
            
            jsonl_entry = self._create_jsonl_entry(candidate, content_str)
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
    
    def _create_jsonl_entry(self, candidate: ProcessingCandidate, content_str: str) -> dict[str, Any]:
        """Create a JSONL entry for a candidate."""
        request_body = {
            "model": self.model,
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
    
    async def _send_jsonl_files_to_batch_manager(self, jsonl_files: List[str], minio_directory: str) -> List[str]:
        """Send JSONL files to batch manager and return batch task IDs."""
        batch_task_ids = []
        
        for jsonl_file_path in jsonl_files:
            try:
                logger.info(f"Sending JSONL file to batch manager: {jsonl_file_path}")
                batch_response = await self.batch_manager_client.create_batch_task(
                    task_type="cv_parsing",
                    jsonl_file_path=jsonl_file_path,
                    metadata={"minio_directory": minio_directory}
                )
                batch_task_ids.append(batch_response.id)
                logger.info(f"Successfully created batch task: {batch_response.id}")
            except Exception as e:
                logger.error(f"Failed to create batch task for file {jsonl_file_path}: {e}")
                raise
        
        return batch_task_ids
    
    def _cleanup_temporary_files(self, file_paths: List[str]) -> None:
        """Clean up temporary JSONL files."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {e}")
    
    async def _update_candidates_status_to_parsing(self, processing_candidates: List[ProcessingCandidate]) -> None:
        """Update all ProcessingCandidate documents status to 'parsing'."""
        try:
            updated_count = await self.processing_candidate_repository.update_status_to_parsing(processing_candidates)
            logger.info(f"Bulk updated {updated_count} candidates status to 'parsing'")
        except Exception as e:
            logger.error(f"Error bulk updating candidate statuses to parsing: {e}")
            raise
