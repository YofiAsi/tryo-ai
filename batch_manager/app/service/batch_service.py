from typing import Callable, Optional, Literal
from datetime import datetime
from app.entity.batch_entity import Batch, BatchStatus
from app.service.openai_api_service import BatchOperationResponse
from openai.types.batch import Batch as OpenAiBatchDTO
from openai.types.batch_request_counts import BatchRequestCounts as BatchRequestCountsDTO
from openai import OpenAI
from app.service.multi_key_openai_service import MultiKeyOpenAiClientServiceResponse, MultiKeyOpenAiClientService
from app.repository.batch_repository import BatchRepository
from app.repository.file_storage_repository import FileStorageRepository
import tempfile
import os
from dataclasses import dataclass

BATCH_FILE_EXPIRATION_TIME = 864000 # 10 days
BATCH_COMPLETION_WINDOW: Literal["24h"] = "24h"

@dataclass
class DownloadBatchFilesResponse:
    output_file_name: Optional[str]
    error_file_name: Optional[str]

class BatchService:
    def __init__(
        self, 
        multi_key_openai_client_service: MultiKeyOpenAiClientService,
        batch_file_storage_repository: FileStorageRepository,
        batch_repository: BatchRepository
    ):
        self.multi_key_openai_client_service = multi_key_openai_client_service
        self.batch_file_storage_repository = batch_file_storage_repository
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
    
    async def _update_batch_after_batch_operation(self, batch: Batch, client_response: MultiKeyOpenAiClientServiceResponse[BatchOperationResponse]) -> Batch:
        batch_operation_response: BatchOperationResponse = client_response.response
        client_name: str = client_response.client_name
        batch.openai_batch_id = batch_operation_response.batch_operation_response.id
        batch.input_file_id = batch_operation_response.file_operation_response.id
        batch.api_client_name = client_name
        batch.status = BatchStatus.VALIDATING
        return await self.batch_repository.update(batch)
    
    async def create_openai_batch(self, batch: Batch) -> Batch:
        if not batch.db_input_file_name:
            raise ValueError(f"Batch {batch.id} has no input file ID")
        
        fd, temp_file_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)  # Close the file descriptor to allow file operations
        
        try:
            self.batch_file_storage_repository.download_batch_input_to_tmp_file(batch.db_input_file_name, temp_file_path)
            batch_operation = self._get_batch_operation(batch, temp_file_path)
            client_response: MultiKeyOpenAiClientServiceResponse[BatchOperationResponse] = await self.multi_key_openai_client_service.execute(batch.estimated_tokens, batch.ai_model, batch_operation)
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

    def get_batch_full_status(self, batch: Batch) -> OpenAiBatchDTO:
        if not batch.api_client_name:
            raise ValueError("Batch has no API client name")
        
        if not batch.openai_batch_id:
            raise ValueError(f"Batch {batch.id} has no OpenAI batch ID")
        
        try:
            batch_response: MultiKeyOpenAiClientServiceResponse[OpenAiBatchDTO] = self.multi_key_openai_client_service.execute_with_client_name_no_tokens(
                batch.api_client_name, 
                self._get_batch_retrieve_operation(batch)
            )
            return batch_response.response
        except Exception as e:
            raise Exception(f"Failed to get batch status for {batch.id}: {e}")
    
    async def update_batch_status(self, batch: Batch) -> Batch:
        if batch.status == BatchStatus.PENDING_UPLOAD:
            return batch
        
        try:
            batch_full_status: OpenAiBatchDTO = self.get_batch_full_status(batch)
            batch.update_with_batch_dto(batch_full_status)
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
                batch_full_status: OpenAiBatchDTO = self.get_batch_full_status(batch)
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

    async def download_and_store_batch_files(self, batch: Batch) -> DownloadBatchFilesResponse:
        """
        Download batch results and store them in MinIO.
        
        Args:
            batch: Batch entity
            
        Returns:
            str: MinIO object name where the file was stored
            
        Raises:
            ValueError: If batch not completed
            Exception: For API, database, or file processing errors
        """
        try:
            updated_batch: Batch = await self.update_batch_status(batch)
            
            if updated_batch.output_file_id:
                output_file_content = await self.download_output_batch_file(updated_batch)
                if not output_file_content:
                    raise ValueError("Failed to download batch output file - batch may not be completed")
                file_metadata = self.batch_file_storage_repository.store_batch_results(str(updated_batch.id), output_file_content)
                updated_batch.db_output_file_name = file_metadata.minio_object_name
            
            if updated_batch.error_file_id:
                error_file_content = await self.download_error_batch_file(updated_batch)
                if not error_file_content:
                    raise ValueError("Failed to download batch error file - batch may not be completed")
                file_metadata = self.batch_file_storage_repository.store_batch_errors(str(updated_batch.id), error_file_content)
                updated_batch.db_error_file_name = file_metadata.minio_object_name
            
            await self.batch_repository.update(updated_batch)
            return DownloadBatchFilesResponse(output_file_name=updated_batch.db_output_file_name, error_file_name=updated_batch.db_error_file_name)
            
        except Exception as e:
            raise Exception(f"Failed to download and store batch results for {batch.id}: {e}")