"""Service for managing OpenAI batch operations."""
from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Callable, List, Literal, Optional

from openai.types.batch_request_counts import BatchRequestCounts as BatchRequestCountsDTO

from app.entity.batch_entity import Batch, BatchStatus
from app.errors.business_exception import BusinessException, ErrorCodes
from app.service.multi_key_openai_service import NoAvailableClient
from app.service.openai_api_service import BatchOperationResponse

if TYPE_CHECKING:
    from beanie import PydanticObjectId
    from openai import OpenAI
    from openai.types.batch import Batch as OpenAiBatchDTO

    from app.repository.batch_repository import BatchRepository
    from app.repository.file_storage_repository import FileStorageRepository
    from app.service.batch_task_service import BatchTaskService
    from app.service.multi_key_openai_service import MultiKeyOpenAiClientService, MultiKeyOpenAiClientServiceResponse

BATCH_FILE_EXPIRATION_TIME = 864000 # 10 days
BATCH_COMPLETION_WINDOW: Literal["24h"] = "24h"

_log = logging.getLogger(__name__)

@dataclass
class DownloadBatchFilesResponse:
    output_file_name: Optional[str]
    error_file_name: Optional[str]

class BatchService:
    def __init__(
        self, 
        multi_key_openai_client_service: MultiKeyOpenAiClientService,
        batch_file_storage_repository: FileStorageRepository,
        batch_repository: BatchRepository,
        batch_task_service: BatchTaskService,
    ):
        self.multi_key_openai_client_service = multi_key_openai_client_service
        self.batch_file_storage_repository = batch_file_storage_repository
        self.batch_task_service = batch_task_service
        self.batch_repository = batch_repository

    def _get_batch_operation(self, batch: Batch, temp_file_path: str) -> Callable[[OpenAI], BatchOperationResponse]:
        """
        Create a batch operation that creates a batch input file and a batch.
        """
        def batch_operation(client: OpenAI) -> BatchOperationResponse:
            with open(temp_file_path, 'rb') as file_handle:
                batch_input_file = client.files.create(
                    file=file_handle,
                    purpose="batch",
                    expires_after={
                        "anchor": "created_at",
                        "seconds": BATCH_FILE_EXPIRATION_TIME
                    }
                )
            
            batch_response = client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint=batch.endpoint,
                completion_window=BATCH_COMPLETION_WINDOW
            )

            return BatchOperationResponse(
                file_operation_response=batch_input_file,
                batch_operation_response=batch_response
            )

        return batch_operation
    
    async def _update_batch_after_batch_operation(
        self,
        batch: Batch,
        client_response: MultiKeyOpenAiClientServiceResponse[BatchOperationResponse],
    ) -> Batch:
        batch_operation_response: BatchOperationResponse = client_response.response
        batch.openai_batch_id = batch_operation_response.batch_operation_response.id
        batch.input_file_id = batch_operation_response.file_operation_response.id
        batch.api_client_name = client_response.client_name
        batch.status = BatchStatus.VALIDATING
        return await self.batch_repository.update(batch)
    
    async def create_openai_batch(self, batch: Batch) -> Optional[Batch]:
        if not batch.db_input_file_name:
            raise ValueError(f"Batch {batch.id} has no input file ID")
        
        fd, temp_file_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)  # Close the file descriptor to allow file operations
        
        try:
            self.batch_file_storage_repository.download_batch_input_to_tmp_file(batch.db_input_file_name, temp_file_path)
            batch_operation = self._get_batch_operation(batch, temp_file_path)
            client_response: MultiKeyOpenAiClientServiceResponse[BatchOperationResponse] = (
                await self.multi_key_openai_client_service.execute(
                    batch.estimated_tokens, batch.ai_model, batch_operation
                )
            )
            batch = await self._update_batch_after_batch_operation(batch, client_response)
            
            return batch

        except Exception as e:
            # Update batch to failed status on error
            batch.status = BatchStatus.FAILED
            batch.errors.append({"error": str(e), "failed_at": datetime.now().isoformat()})
            await self.batch_repository.update(batch)
            raise Exception(f"Failed to create OpenAI batch for {batch.id}: {e}")
            
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def _get_batch_retrieve_operation(self, batch: Batch) -> Callable[[OpenAI], OpenAiBatchDTO]:
        def batch_retrieve_operation(client: OpenAI) -> OpenAiBatchDTO:
            if not batch.openai_batch_id:
                raise ValueError(f"Batch {batch.id} has no OpenAI batch ID")
            batch_response: OpenAiBatchDTO = client.batches.retrieve(batch.openai_batch_id)
            return batch_response
        return batch_retrieve_operation

    def get_updated_batch(self, batch: Batch) -> OpenAiBatchDTO:
        if not batch.api_client_name:
            raise ValueError("Batch has no API client name")
        
        if not batch.openai_batch_id:
            raise ValueError(f"Batch {batch.id} has no OpenAI batch ID")
        
        try:
            batch_response: MultiKeyOpenAiClientServiceResponse[OpenAiBatchDTO] = (
                self.multi_key_openai_client_service.execute_with_client_name_no_tokens(
                    batch.api_client_name, 
                    self._get_batch_retrieve_operation(batch)
                )
            )
            return batch_response.response
        except Exception as e:
            raise Exception(f"Failed to get batch status for {batch.id}: {e}")
    
    async def update_batch(self, batch: Batch) -> Batch:
        if batch.status == BatchStatus.PENDING_UPLOAD:
            return batch
        
        try:
            updated_batch: OpenAiBatchDTO = self.get_updated_batch(batch)
            batch.update_with_batch_dto(updated_batch)
            return await self.batch_repository.update(batch)
        except Exception as e:
            # If we can't get status, mark as failed if it's not already in a terminal state
            if not batch.is_terminal_state:
                batch.status = BatchStatus.FAILED
                batch.errors.append({"error": f"Failed to update status: {str(e)}", "failed_at": datetime.now().isoformat()})
                await self.batch_repository.update(batch)
            raise Exception(f"Failed to update batch status for {batch.id}: {e}")
    
    def get_batch_progress(self, batch: Batch) -> BatchRequestCountsDTO:
        """
        Get batch progress information including request counts.
        
        Args:
            batch: Batch entity
            
        Returns:
            BatchRequestCountsDTO: Request counts with keys 'total', 'completed', 'failed'
            
        Raises:
            ValueError: If batch not found or missing required fields
            Exception: For API or database errors
        """
        # Handle different batch statuses
        if batch.status == BatchStatus.PENDING_UPLOAD:
            return BatchRequestCountsDTO(total=0, completed=0, failed=0)
        
        elif batch.status in [BatchStatus.COMPLETED, BatchStatus.FAILED]:
            # For completed/failed batches, return stored counts
            return BatchRequestCountsDTO(total=batch.total_requests, completed=batch.completed_requests, failed=batch.failed_requests)
        
        elif batch.status in [BatchStatus.VALIDATING, BatchStatus.IN_PROGRESS, BatchStatus.FINALIZING]:
            # Make API call to get real-time progress
            if not batch.openai_batch_id or not batch.api_client_name:
                return BatchRequestCountsDTO(total=0, completed=0, failed=0)
            
            try:
                batch_full_status: OpenAiBatchDTO = self.get_updated_batch(batch)
                return batch_full_status.request_counts if batch_full_status.request_counts else BatchRequestCountsDTO(total=0, completed=0, failed=0)
            except Exception:
                # Fall back to stored values if API call fails
                return BatchRequestCountsDTO(total=batch.total_requests, completed=batch.completed_requests, failed=batch.failed_requests)
        
        else:
            return BatchRequestCountsDTO(total=0, completed=0, failed=0)
    
    def _get_file_operation(self, file_id: str) -> Callable[[OpenAI], bytes]:
        """
        Create operation to download batch output file content from OpenAI.
        """
        def get_file_operation(client: OpenAI) -> bytes:
            file_content = client.files.content(file_id)
            return file_content.read()
        
        return get_file_operation
        
    async def download_output_batch_file(self, batch: Batch) -> Optional[bytes]:
        """
        Download results file of a completed batch and return as bytes.
        
        Args:
            batch: Batch entity
            
        Returns:
            bytes: Batch results content, or None if batch not completed
            
        Raises:
            ValueError: If batch is not completed or has no output file
            Exception: For API errors
        """
        if not batch.api_client_name:
            raise ValueError("Batch has no API client name")
        
        if not batch.is_terminal_state:
            raise ValueError(f"Batch {batch.id} is not in a terminal state")
        
        if not batch.openai_batch_id:
            raise ValueError(f"Batch {batch.id} has no OpenAI batch ID")

        if not batch.output_file_id:
            raise ValueError(f"Batch {batch.id} has no output file ID")
        
        try:
            file_operation = self._get_file_operation(batch.output_file_id)
            client_response: MultiKeyOpenAiClientServiceResponse[bytes] = self.multi_key_openai_client_service.execute_with_client_name_no_tokens(
                batch.api_client_name, 
                file_operation
            )
            return client_response.response
            
        except Exception as e:
            raise Exception(f"Failed to download batch results for {batch.id}: {e}")
    
    async def download_error_batch_file(self, batch: Batch) -> Optional[bytes]:
        if not batch.api_client_name:
            raise ValueError("Batch has no API client name")
        
        if not batch.is_terminal_state:
            raise ValueError(f"Batch {batch.id} is not in a terminal state")
        
        if not batch.error_file_id:
            raise ValueError(f"Batch {batch.id} has no error file ID")
        
        try:
            file_operation = self._get_file_operation(batch.error_file_id)
            client_response: MultiKeyOpenAiClientServiceResponse[bytes] = self.multi_key_openai_client_service.execute_with_client_name_no_tokens(
                batch.api_client_name, 
                file_operation
            )
            return client_response.response
        except Exception as e:
            raise Exception(f"Failed to download batch error file for {batch.id}: {e}")

    async def download_and_store_batch_files(self, batch: Batch) -> Optional[DownloadBatchFilesResponse]:
        """
        Download batch results and store them in MinIO.
        Update batch with relevant stats.

        Args:
            batch: Batch entity
            
        Returns:
            DownloadBatchFilesResponse: Response containing the output and error file names
        """
        if batch.files_collected:
            return None

        if not batch.is_terminal_state:
            return None
        
        _uploaded: bool = False

        if batch.output_file_id:
            output_file_content = await self.download_output_batch_file(batch)
            if not output_file_content:
                raise ValueError("Failed to download batch output file - batch may not be completed")
            file_metadata = self.batch_file_storage_repository.store_batch_results(str(batch.id), output_file_content)
            batch.db_output_file_name = file_metadata.minio_object_name
            _uploaded = True
        if batch.error_file_id:
            error_file_content = await self.download_error_batch_file(batch)
            if not error_file_content:
                raise ValueError("Failed to download batch error file - batch may not be completed")
            file_metadata = self.batch_file_storage_repository.store_batch_errors(str(batch.id), error_file_content)
            batch.db_error_file_name = file_metadata.minio_object_name
            _uploaded = True
        
        if _uploaded:
            batch.files_collected = True
            await self.batch_repository.update(batch)
        
        return DownloadBatchFilesResponse(output_file_name=batch.db_output_file_name, error_file_name=batch.db_error_file_name)

    async def start_batch(self, batch: Batch) -> bool:
        """
        Start a batch.
        """
        if batch.status != BatchStatus.PENDING_UPLOAD:
            raise BusinessException(ErrorCodes.INVALID_STATE, f"Batch {batch.id} is not in the pending upload state")
        
        openai_batch: Optional[Batch] = await self.create_openai_batch(batch)
        if not openai_batch:
            return False

        return True

    def get_pending_batches_iterator(self) -> AsyncIterator[Batch]:
        """
        Get pending batches iterator.
        """
        return self.batch_repository.get_pending_batches_iterator()
    
    def get_non_terminal_state_batches_iterator(self) -> AsyncIterator[Batch]:
        """
        Get non terminal state batches iterator.
        """
        return self.batch_repository.get_non_terminal_state_batches_iterator()

    async def _notify_batch_task_running(self, batch: Batch) -> None:
        if not batch.task_id:
            return
        await self.batch_task_service.update_task_status_running_if_needed(batch.task_id)
        
    async def start_pending_batches(self) -> List[PydanticObjectId]:
        pending_batches: AsyncIterator[Batch] = self.get_pending_batches_iterator()
        started_batches_ids: List[PydanticObjectId] = []
        async for batch in pending_batches:
            try:
                if await self.start_batch(batch):
                    await self._notify_batch_task_running(batch)
                    started_batches_ids.append(batch.id)
                else:
                    _log.error(f"Failed to start batch {batch.id}")
            except NoAvailableClient:
                continue
        
        return started_batches_ids

    async def update_non_terminal_state_batches(self) -> None:
        non_terminal_state_batches: AsyncIterator[Batch] = self.get_non_terminal_state_batches_iterator()
        async for batch in non_terminal_state_batches:
            updated_batch = await self.update_batch(batch)
            await self.download_and_store_batch_files(updated_batch)
        