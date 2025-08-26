from __future__ import annotations
import logging
import tiktoken
import asyncio
import tempfile
import shutil
import json
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    TextIO,
    Optional,
    Iterator,
    Union,
    List,
    Dict,
    Any,
    Tuple,
    BinaryIO,
)
from app.consts.ai_models import AIModel
from app.entity.batch_entity import Batch
from app.consts.rate_limits import (
    MAX_REQUESTS_PER_BATCH,
    MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD,
    MAX_BATCH_INPUT_FILE_SIZE_BYTES,
)
from app.errors.business_exception import BusinessException, ErrorCodes
from app.entity.batch_task_entity import BatchTask

from app.entity.batch_task_entity import BatchTaskType
from app.repository.batch_task_repository import BatchTaskRepository
from app.repository.batch_repository import BatchRepository
from app.repository.file_storage_repository import FileStorageRepository, FileMetadata

_log = logging.getLogger(__name__)
ENCODER = tiktoken.get_encoding("cl100k_base")
TOKENS_RATE_LIMIT_THRESHOLD_MULTIPLIER = 0.2


class BatchFileHandler:
    def __init__(self, ai_model: AIModel, endpoint: str, tmp_dir: Path):
        self.entity: Batch = Batch(
            ai_model=ai_model,
            endpoint=endpoint,
        )
        self.file_path: Path = tmp_dir / f"{self.entity.id}.jsonl"
        self.file_handle: TextIO = open(self.file_path, "w", encoding="utf-8")

    def add_line(self, line: str, estimated_tokens: int) -> None:
        self.file_handle.write(line + "\n")
        self.entity.estimated_tokens += estimated_tokens
        self.entity.total_requests += 1

    def close(self) -> None:
        if not self.file_handle.closed:
            self.file_handle.close()

    def will_exceed_limits(self, estimated_tokens: int, line_size: int) -> bool:
        if self._exceeds_token_limit(estimated_tokens):
            return True
        if self._exceeds_request_limit():
            return True
        if self._exceeds_file_size_limit(line_size):
            return True
        return False

    def _exceeds_token_limit(self, estimated_tokens: int) -> bool:
        return (
            self.entity.estimated_tokens + estimated_tokens
            > MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD[self.entity.ai_model] * TOKENS_RATE_LIMIT_THRESHOLD_MULTIPLIER
        )

    def _exceeds_request_limit(self) -> bool:
        return self.entity.total_requests + 1 > MAX_REQUESTS_PER_BATCH

    def _exceeds_file_size_limit(self, line_size: int) -> bool:
        return self.file_handle.tell() + line_size > MAX_BATCH_INPUT_FILE_SIZE_BYTES


class BatchTaskCreateService:
    """
    BatchTask Service class

    This service handles batch_task creation and management, including the logic for
    creating single or multiple tasks based on the batch_task type.
    """

    def __init__(
        self,
        batch_task_repository: BatchTaskRepository,
        batch_repository: BatchRepository,
        file_storage_repository: FileStorageRepository,
    ):
        self.batch_task_repository = batch_task_repository
        self.batch_repository = batch_repository
        self.file_storage_repository = file_storage_repository
        self.model_to_batch_map: Dict[AIModel, List[BatchFileHandler]] = {}
        self.batch_task: Optional[BatchTask] = None
        self.tmp_dir: Path = Path(tempfile.mkdtemp())
        _log.debug("BatchTaskCreateService initialized")

    async def create_task(
        self,
        batch_task_type: BatchTaskType,
        file: BinaryIO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BatchTask:
        """
        Create batch_task based on the provided DTO and file.

        Args:
            batch_task_type: The type of batch_task to create
            metadata: The metadata for the batch_task
            file: The uploaded JSONL file containing requests

        Returns:
            Created batch_task
        """
        _log.info("Creating batch_task")

        self.batch_task = BatchTask(
            task_type=batch_task_type,
            metadata=metadata,
        )
        self.model_to_batch_map = {}

        try:
            self._handle_line_batching_from_file(file)
            await self._upload_batch_files()
            await self._save_batches_to_db()
            saved_task = await self._save_task_to_db()

            return saved_task

        except Exception as e:
            _log.error(f"Error creating tasks: {str(e)}")
            if isinstance(e, BusinessException):
                raise
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to create tasks: {str(e)}")

        finally:
            self._delete_tmp_files()

    def _handle_line_batching_from_file(self, file: BinaryIO) -> None:
        if self.batch_task is None:
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, "BatchTask not initialized")

        for line, line_size in self._read_file_lines_with_size(file):
            line = line.strip()
            if not line:
                continue

            json_line: Dict[str, Any] = self._get_json_line_from_line(line)
            model: AIModel = self._get_model_from_json(json_line)
            estimated_tokens: int = self._count_tokens_from_json(json_line)

            if model not in self.model_to_batch_map:
                self.model_to_batch_map[model] = [
                    BatchFileHandler(
                        ai_model=model,
                        endpoint=self.batch_task.endpoint,
                        tmp_dir=self.tmp_dir,
                    )
                ]

            # Check if can proceed with the current batch, if not, add to batch_task and create a new batch
            if self.model_to_batch_map[model][-1].will_exceed_limits(estimated_tokens, line_size):
                self.model_to_batch_map[model][-1].close()
                self.model_to_batch_map[model].append(
                    BatchFileHandler(
                        ai_model=model,
                        endpoint=self.batch_task.endpoint,
                        tmp_dir=self.tmp_dir,
                    )
                )

            self.model_to_batch_map[model][-1].add_line(
                line=line,
                estimated_tokens=estimated_tokens,
            )

        self._add_batches_to_task()

    def _delete_tmp_files(self) -> None:
        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                if batch_file_handler.file_path.exists():
                    batch_file_handler.close()

        # Clean up temporary directory
        if self.tmp_dir.exists():
            try:
                shutil.rmtree(self.tmp_dir)
            except OSError as e:
                _log.warning(f"Could not remove temporary directory {self.tmp_dir}: {e}")

    def _add_batches_to_task(self) -> None:
        if self.batch_task is None:
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, "BatchTask not initialized")

        for batch_file_handlers in self.model_to_batch_map.values():
            for batch_file_handler in batch_file_handlers:
                self.batch_task.add_batch(batch_file_handler.entity)

    def _get_json_line_from_line(self, line: str) -> Dict[str, Any]:
        try:
            json_line: Dict[str, Any] = json.loads(line)
            return json_line
        except json.JSONDecodeError as e:
            _log.error(f"Error getting JSON line from line: {line} error: {e}")
            raise

    def _get_model_from_json(self, json_line: Dict[str, Any]) -> AIModel:
        try:
            model = json_line["body"]["model"]
            return AIModel(model)
        except json.JSONDecodeError as e:
            _log.error(f"Error getting model from JSON line: {json_line} error: {e}")
            raise
        except ValueError as e:
            _log.error(f"Invalid model: {model} error: {e}")
            raise

    def _count_tokens_from_json(self, json_line: Dict[str, Any]) -> int:
        try:
            input_list: Union[List[Dict[str, Any]], str] = json_line["body"]["input"]
            if isinstance(input_list, str):
                input_list = [{"content": input_list}]
            estimated_tokens = 0
            for input_item in input_list:
                estimated_tokens += len(ENCODER.encode(input_item["content"]))
            return estimated_tokens
        except json.JSONDecodeError as e:
            _log.error(f"Error counting tokens from JSON line: {json_line} error: {e}")
            raise

    def _read_file_lines_with_size(self, file: BinaryIO) -> Iterator[Tuple[str, int]]:
        for line_bytes in file:
            line_size = len(line_bytes)
            line = line_bytes.decode("utf-8").strip()
            if not line:
                continue
            yield line, line_size

    async def _upload_batch_files(self) -> Dict[str, FileMetadata]:
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
                batch_file_handler.close()

                upload_task = self._upload_single_batch_file(batch_file_handler)
                upload_tasks.append(upload_task)
                batch_handlers.append(batch_file_handler)

        try:
            # Execute all uploads in parallel
            _log.info(f"Uploading {len(upload_tasks)} batch files")
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)

            # Process results
            successful_uploads: Dict[str, FileMetadata] = {}
            failed_uploads = []

            for i, result in enumerate(upload_results):
                batch_handler: BatchFileHandler = batch_handlers[i]
                batch_id = str(batch_handler.entity.id)

                if isinstance(result, BaseException):
                    _log.error(f"Failed to upload batch file {batch_id}: {str(result)}")
                    failed_uploads.append((batch_id, result))
                else:
                    # At this point, result is guaranteed to be FileMetadata
                    file_metadata: FileMetadata = result
                    _log.debug(f"Successfully uploaded batch file {batch_id}")
                    successful_uploads[batch_id] = file_metadata
                    # Update batch entity with file metadata
                    batch_handler.entity.db_input_file_name = file_metadata.minio_object_name

            # Check if any uploads failed
            if failed_uploads:
                failed_batch_ids = [batch_id for batch_id, _ in failed_uploads]
                error_msg = f"Failed to upload {len(failed_uploads)} batch files: {', '.join(failed_batch_ids)}"
                _log.error(error_msg)
                raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, error_msg)

            _log.info(f"Successfully uploaded {len(successful_uploads)} batch files")
            return successful_uploads

        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Unexpected error during parallel file upload: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to upload batch files: {str(e)}")

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
        batch_id = str(batch_file_handler.entity.id)
        file_path = str(batch_file_handler.file_path)

        try:
            _log.debug(f"Uploading batch file: {batch_id} from {file_path}")

            # Verify file exists
            if not batch_file_handler.file_path.exists():
                raise FileNotFoundError(f"Batch file not found: {file_path}")

            # Upload to file storage repository
            file_metadata = self.file_storage_repository.upload_batch_input_file(
                batch_id=batch_id, file_data=file_path, content_type="application/jsonl"
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
            await self.batch_repository.bulk_create(batches_to_save)
        except Exception as e:
            _log.error(f"Failed to save batches to database: {str(e)}")
            raise

    async def _save_task_to_db(self) -> BatchTask:
        """
        Save batch_task entity to the database.
        """
        if not self.batch_task:
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, "BatchTask not initialized")

        _log.info("Saving batch_task to database")

        try:
            saved_task = await self.batch_task_repository.create(self.batch_task)
            _log.info("Successfully saved batch_task to database")
            return saved_task
        except Exception as e:
            _log.error(f"Failed to save batch_task to database: {str(e)}")
            raise
