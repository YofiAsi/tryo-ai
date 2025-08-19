import logging
import uuid
import tiktoken
import asyncio
import tempfile
import shutil
from typing import TextIO
from typing import List, Dict, Any, AsyncGenerator, Tuple
from fastapi import UploadFile
from datetime import datetime
from pathlib import Path
import os
import json

from app.consts.ai_models import AIModel
from app.schema.task_dto import CreateTaskDTO, CreateTaskResponseDTO, TaskDTO
from app.entity.task_entity import Task, TaskStatus, TaskType
from app.entity.batch_entity import Batch, BatchStatus
from app.repository.task_repository import TaskRepository
from app.repository.batch_repository import BatchRepository
from app.repository.file_storage_repository import FileStorageRepository, FileMetadata
from app.consts.rate_limits import MAX_REQUESTS_PER_BATCH, MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD, MAX_BATCH_INPUT_FILE_SIZE_BYTES
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)
ENCODER = tiktoken.get_encoding("cl100k_base")
TOKENS_RATE_LIMIT_THRESHOLD_MULTIPLIER = 0.2

class BatchFileHandler:
    def __init__(self, ai_model: AIModel, tmp_dir: Path):
        self.entity: Batch = Batch(
            ai_model=ai_model,
        )
        self.file_path: Path = tmp_dir / f"{self.entity.batch_id}.jsonl"
        self.file_handle: TextIO = open(self.file_path, "w", encoding="utf-8")

class TaskHandler:
    def __init__(self, task_dto: CreateTaskDTO):
        self.task_dto: CreateTaskDTO = task_dto
        self.tasks: list[Task] = []
    
    def add_prepared_batch(self, batch: Batch) -> None:
        task: Task = None
        if self.task_dto.multitask or len(self.tasks) == 0:
            task = Task(
                task_type=self.task_dto.type,
                metadata=self.task_dto.metadata,
            )
            self.tasks.append(task)
        else:
            task = self.tasks[0]
        task.add_batch(batch)

class TaskCreateService:
    """
    Task Service class
    
    This service handles task creation and management, including the logic for
    creating single or multiple tasks based on the multitask configuration.
    """
    
    def __init__(self, task_repository: TaskRepository, batch_repository: BatchRepository, file_storage_repository: FileStorageRepository):
        self.task_repository = task_repository
        self.batch_repository = batch_repository
        self.file_storage_repository = file_storage_repository
        self.model_to_batch_map: Dict[AIModel, List[BatchFileHandler]] = {}
        self.task_handler: TaskHandler = None
        self.tmp_dir: Path = None
        _log.debug("TaskCreateService initialized")

    async def create_tasks(self, create_task_dto: CreateTaskDTO, file: UploadFile) -> CreateTaskResponseDTO:
        """
        Create tasks based on the provided DTO and file.
        
        If multitask is True: Creates multiple tasks, each with a single batch
        If multitask is False: Creates a single task with multiple batches
        
        Args:
            create_task_dto: The task creation configuration
            file: The uploaded JSONL file containing requests
            
        Returns:
            CreateTaskResponseDTO containing the created tasks
        """
        _log.info(f"Creating tasks")
        
        self.task_handler = TaskHandler(create_task_dto)
        self.model_to_batch_map = {}
        self.tmp_dir = Path(tempfile.mkdtemp())

        try:
            await self._handle_line_batching_from_file(file)
            await self._upload_batch_files_parallel()
            await self._save_batches_to_db()
            await self._save_tasks_to_db()

            return CreateTaskResponseDTO(
                tasks=[TaskDTO.from_entity(task) for task in self.task_handler.tasks]
            )

        except Exception as e:
            _log.error(f"Error creating tasks: {str(e)}")
            if isinstance(e, BusinessException):
                raise
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, f"Failed to create tasks: {str(e)}")

        finally:
            self._delete_tmp_files()

    async def _handle_line_batching_from_file(self, file: UploadFile) -> None:
        if self.task_handler is None:
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, "Task handler not initialized")
        
        async for line, line_size in self._read_file_lines_with_size(file):
            json_line = self._get_json_line_from_line(line)
            model = self._get_model_from_json(json_line)
            estimated_tokens = self._count_tokens_from_json(json_line)

            if model not in self.model_to_batch_map:
                self.model_to_batch_map[model] = [BatchFileHandler(model, self.tmp_dir)]
            
            # Check if can proceed with the current batch, if not, add to task and create a new batch
            if self._check_limit_exceeded(
                estimated_tokens=estimated_tokens,
                batch_file_handler=self.model_to_batch_map[model][-1],
                line_size=line_size,
                line=line
            ):
                self._close_batch_file(self.model_to_batch_map[model][-1])
                self.model_to_batch_map[model].append(BatchFileHandler(model, self.tmp_dir))
            
            self._add_line_to_batch(
                line=line,
                estimated_tokens=estimated_tokens,
                batch_file_handler=self.model_to_batch_map[model][-1]
            )

        self._add_batches_to_task()
    
    def _close_batch_file(self, batch_file_handler: BatchFileHandler) -> None:
        batch_file_handler.file_handle.close()

    def _delete_tmp_files(self) -> None:
        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                if batch_file_handler.file_path.exists():
                    batch_file_handler.file_handle.close()
        
        # Clean up temporary directory
        if self.tmp_dir.exists():
            try:
                shutil.rmtree(self.tmp_dir)
            except OSError as e:
                _log.warning(f"Could not remove temporary directory {self.tmp_dir}: {e}")

    def _add_batches_to_task(self) -> None:
        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                self.task_handler.add_prepared_batch(batch_file_handler.entity)

    def _add_line_to_batch(self, line: str, estimated_tokens: int, batch_file_handler: BatchFileHandler) -> None:
        batch_file_handler.file_handle.write(line + "\n")
        batch_file_handler.entity.estimated_tokens += estimated_tokens
        batch_file_handler.entity.total_requests += 1

    def _check_limit_exceeded(self, estimated_tokens: int, batch_file_handler: BatchFileHandler, line_size: int) -> bool:
        if self._exceeds_token_limit(estimated_tokens, batch_file_handler):
            return True
        if self._exceeds_request_limit(batch_file_handler):
            return True
        if self._exceeds_file_size_limit(batch_file_handler, line_size):
            return True
        return False

    def _exceeds_token_limit(self, estimated_tokens: int, batch_file_handler: BatchFileHandler) -> bool:
        return batch_file_handler.entity.estimated_tokens + estimated_tokens > MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD[batch_file_handler.entity.ai_model] * TOKENS_RATE_LIMIT_THRESHOLD_MULTIPLIER

    def _exceeds_request_limit(self, batch_file_handler: BatchFileHandler) -> bool:
        return batch_file_handler.entity.total_requests + 1 > MAX_REQUESTS_PER_BATCH

    def _exceeds_file_size_limit(self, batch_file_handler: BatchFileHandler, line_size: int) -> bool:
        return batch_file_handler.file_handle.tell() + line_size > MAX_BATCH_INPUT_FILE_SIZE_BYTES

    def _get_json_line_from_line(self, line: str) -> Dict[str, Any]:
        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            _log.error(f"Error getting JSON line from line: {line}")
            raise

    def _get_model_from_json(self, json_line: Dict[str, Any]) -> AIModel:
        try:
            model = json_line["body"]["model"]
            return AIModel(model)
        except json.JSONDecodeError as e:
            _log.error(f"Error getting model from JSON line: {json_line}")
            raise
        except ValueError as e:
            _log.error(f"Invalid model: {model}")
            raise
    
    def _count_tokens_from_json(self, json_line: Dict[str, Any]) -> int:
        try:
            input_list: List[Dict[str, Any]] = json_line["body"]["input"]
            estimated_tokens = 0
            for input_item in input_list:
                estimated_tokens += len(ENCODER.encode(input_item["content"]))
            return estimated_tokens
        except json.JSONDecodeError as e:
            _log.error(f"Error counting tokens from JSON line: {json_line}")
            raise

    async def _read_file_lines_with_size(self, file: UploadFile) -> AsyncGenerator[Tuple[str, int], None]:
        async for line_bytes in file:
            line_size = len(line_bytes)
            line = line_bytes.decode('utf-8').strip()
            if not line:
                continue
            yield line, line_size

    async def _upload_batch_files_parallel(self) -> Dict[str, FileMetadata]:
        """
        Upload all batch files from model_to_batch_map in parallel to the file storage repository.
        
        Returns:
            Dict mapping batch_id to FileMetadata for successful uploads
            
        Raises:
            BusinessException: If any upload fails
        """
        _log.info("Starting parallel upload of batch files")
        
        if not self.model_to_batch_map:
            _log.warning("No batch files to upload")
            return {}
        
        # Collect all batch file handlers that need uploading
        upload_tasks = []
        batch_handlers = []
        
        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                # Close the file handle before uploading
                if not batch_file_handler.file_handle.closed:
                    batch_file_handler.file_handle.close()
                
                # Create upload task
                upload_task = self._upload_single_batch_file(batch_file_handler)
                upload_tasks.append(upload_task)
                batch_handlers.append(batch_file_handler)
        
        try:
            # Execute all uploads in parallel
            _log.info(f"Uploading {len(upload_tasks)} batch files")
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Process results
            successful_uploads = {}
            failed_uploads = []
            
            for i, result in enumerate(upload_results):
                batch_handler: BatchFileHandler = batch_handlers[i]
                batch_id = str(batch_handler.entity.batch_id)
                
                if isinstance(result, Exception):
                    _log.error(f"Failed to upload batch file {batch_id}: {str(result)}")
                    failed_uploads.append((batch_id, result))
                else:
                    _log.debug(f"Successfully uploaded batch file {batch_id}")
                    successful_uploads[batch_id] = result
                    # Update batch entity with file metadata
                    batch_handler.entity.db_input_file_name = result.minio_object_name
            
            # Check if any uploads failed
            if failed_uploads:
                failed_batch_ids = [batch_id for batch_id, _ in failed_uploads]
                error_msg = f"Failed to upload {len(failed_uploads)} batch files: {', '.join(failed_batch_ids)}"
                _log.error(error_msg)
                raise BusinessException(ErrorCodes.INTERNAL_ERROR, error_msg)
            
            _log.info(f"Successfully uploaded {len(successful_uploads)} batch files")
            return successful_uploads
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Unexpected error during parallel file upload: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, f"Failed to upload batch files: {str(e)}")

    async def _upload_single_batch_file(self, batch_file_handler: BatchFileHandler) -> FileMetadata:
        """
        Upload a single batch file to the storage repository.
        
        Args:
            batch_file_handler: The batch file handler containing file info
            
        Returns:
            FileMetadata for the uploaded file
            
        Raises:
            Exception: If upload fails
        """
        batch_id = str(batch_file_handler.entity.batch_id)
        file_path = str(batch_file_handler.file_path)
        
        try:
            _log.debug(f"Uploading batch file: {batch_id} from {file_path}")
            
            # Verify file exists
            if not batch_file_handler.file_path.exists():
                raise FileNotFoundError(f"Batch file not found: {file_path}")
            
            # Upload to file storage repository
            file_metadata = await self.file_storage_repository.upload_batch_input_file(
                batch_id=batch_id,
                file_data=file_path,
                content_type="application/jsonl"
            )
            
            _log.debug(f"Successfully uploaded batch file {batch_id}: {file_metadata.minio_object_name}")
            return file_metadata
            
        except Exception as e:
            _log.error(f"Failed to upload batch file {batch_id}: {str(e)}")
            raise
    
    async def _save_batches_to_db(self) -> None:
        """
        Save all batch entities to the database using bulk operations for efficiency.
        """
        if not self.model_to_batch_map:
            _log.warning("No batches to save to database")
            return
        
        # Collect all batch entities from the model_to_batch_map
        batches_to_save = []
        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                batches_to_save.append(batch_file_handler.entity)
        
        if not batches_to_save:
            _log.warning("No batch entities found to save")
            return
        
        _log.info(f"Saving {len(batches_to_save)} batches to database using bulk operation")
        
        try:
            # Use bulk create for efficient database insertion
            saved_batches = await self.batch_repository.bulk_create(batches_to_save)
            _log.info(f"Successfully saved {len(saved_batches)} batches to database")
        except Exception as e:
            _log.error(f"Failed to save batches to database: {str(e)}")
            raise

    async def _save_tasks_to_db(self) -> None:
        """
        Save all task entities to the database using bulk operations for efficiency.
        """
        if not self.task_handler or not self.task_handler.tasks:
            _log.warning("No tasks to save to database")
            return
        
        tasks_to_save = self.task_handler.tasks
        _log.info(f"Saving {len(tasks_to_save)} tasks to database using bulk operation")
        
        try:
            # Use bulk create for efficient database insertion
            saved_tasks = await self.task_repository.bulk_create(tasks_to_save)
            _log.info(f"Successfully saved {len(saved_tasks)} tasks to database")
        except Exception as e:
            _log.error(f"Failed to save tasks to database: {str(e)}")
            raise