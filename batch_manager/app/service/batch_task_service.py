"""
BatchTaskService for managing batch processing tasks.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.entity.batch_entity import Batch, BatchStatus
from app.entity.batch_task_entity import BatchTask, BatchTaskStatus
from app.errors.business_exception import BusinessException, ErrorCodes

if TYPE_CHECKING:
    from beanie import PydanticObjectId
    from openai.types.batch_request_counts import BatchRequestCounts as BatchRequestCountsDTO
    
    from app.repository.batch_repository import BatchRepository
    from app.repository.batch_task_repository import BatchTaskRepository
    from app.service.batch_service import BatchService, DownloadBatchFilesResponse

_log = logging.getLogger(__name__)


class BatchTaskService:
    """Service for managing batch processing tasks with multiple batches."""
    
    def __init__(
        self,
        batch_task_repository: BatchTaskRepository,
        batch_repository: BatchRepository,
        batch_service: BatchService
    ):
        self.batch_task_repository = batch_task_repository
        self.batch_repository = batch_repository
        self.batch_service = batch_service
    
    async def start_next_batch(self, task_id: PydanticObjectId) -> bool:
        """
        Start the next pending batch in a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if a batch was started, False if no pending batches
            
        Raises:
            BusinessException: If task not found or invalid state
            Exception: For API or database errors
        """
        try:
            # Get task information
            batch_task: BatchTask = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
            
            # Find next pending batch
            pending_batch = await self._find_next_pending_batch(batch_task)
            if not pending_batch:
                _log.info(f"No pending batches found for task {task_id}")
                return False
            
            # Start the batch using BatchService
            started_batch = await self.batch_service.create_openai_batch(pending_batch)
            
            if started_batch and started_batch.status != BatchStatus.FAILED:
                # Update task status to running if it was created
                await self._update_task_status_if_needed(batch_task, BatchTaskStatus.RUNNING)
                _log.info(f"Started batch {started_batch.id} for task {task_id}")
                return True
            
            return False
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to start next batch for task {task_id}: {e}")
            raise Exception(f"Failed to start next batch for task {task_id}: {e}")
    
    async def _find_next_pending_batch(self, batch_task: BatchTask) -> Optional[Batch]:
        """Find the next pending batch for a task."""
        for batch_id in batch_task.batch_ids:
            batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
            if batch and batch.status == BatchStatus.PENDING_UPLOAD:
                return batch
        return None
    
    async def get_task_status(self, task_id: PydanticObjectId) -> BatchTaskStatus:
        """
        Get the current status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            BatchTaskStatus: Task status
            
        Raises:
            BusinessException: If task not found
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            return batch_task.status
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to get task status for {task_id}: {e}")
            raise Exception(f"Failed to get task status for {task_id}: {e}")
    
    async def get_task_info(self, task_id: PydanticObjectId) -> Optional[BatchTask]:
        """
        Get complete task information.
        
        Args:
            task_id: Task ID
            
        Returns:
            BatchTask: Complete task information or None if not found
            
        Raises:
            Exception: For database errors
        """
        try:
            return await self.batch_task_repository.retrieve_by_task_id(task_id)
            
        except BusinessException as e:
            if e.code == ErrorCodes.NOT_FOUND:
                return None
            raise
        except Exception as e:
            _log.error(f"Failed to get task info for {task_id}: {e}")
            raise Exception(f"Failed to get task info for {task_id}: {e}")
    
    async def update_task_status(self, task_id: PydanticObjectId, status: BatchTaskStatus) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            bool: True if successful
            
        Raises:
            BusinessException: If task not found
            Exception: For database errors
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            
            # Update status using entity methods
            if status == BatchTaskStatus.RUNNING:
                batch_task.start()
            elif status == BatchTaskStatus.COMPLETED:
                batch_task.complete()
            elif status == BatchTaskStatus.FAILED:
                batch_task.fail()
            elif status == BatchTaskStatus.CANCELLED:
                batch_task.cancel()
            elif status == BatchTaskStatus.PAUSED:
                batch_task.pause()
            else:
                batch_task.status = status
            
            await self.batch_task_repository.update(batch_task)
            return True
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to update task status for {task_id}: {e}")
            raise Exception(f"Failed to update task status for {task_id}: {e}")
    
    async def collect_completed_batch_results(self, task_id: PydanticObjectId) -> Dict[str, Any] | None:
        """
        Collect results for all completed batches in a task and update their status.
        
        Args:
            task_id: Task ID to process
            
        Returns:
            dict: Summary of processing results with counts and any errors
            
        Raises:
            BusinessException: If task not found
            Exception: For database errors
        """
        try:
            # Get task information
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
            
            if not batch_task.batch_ids:
                _log.info(f"No batches found for task {task_id}")
                return {"processed": 0, "skipped": 0, "errors": []}
            
            # Track processing results
            processed_count = 0
            skipped_count = 0
            errors = []
            
            _log.info(f"Processing completed batches for task {task_id}")
            
            # Process each batch
            for batch_id in batch_task.batch_ids:                
                try:
                    batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
                    if not batch:
                        error_msg = f"Batch {batch_id} not found"
                        _log.error(error_msg)
                        errors.append(error_msg)
                        skipped_count += 1
                        continue
                    
                    # Update batch status first
                    batch = await self.batch_service.update_batch_status(batch)
                    
                    # Skip if not completed
                    if batch.status != BatchStatus.COMPLETED:
                        skipped_count += 1
                        _log.debug(f"Skipping batch {batch_id} - status: {batch.status}")
                        continue
                    
                    # Download and store batch results
                    _log.info(f"Collecting results for batch {batch_id}")
                    download_batch_files_response: DownloadBatchFilesResponse = await self.batch_service.download_and_store_batch_files(batch)
                    if download_batch_files_response.output_file_name:
                        batch.db_output_file_name = download_batch_files_response.output_file_name
                    if download_batch_files_response.error_file_name:
                        batch.db_error_file_name = download_batch_files_response.error_file_name
                    await self.batch_repository.update(batch)
                    
                    processed_count += 1
                    _log.info(f"Successfully collected results for batch {batch_id}")
                    
                except Exception as e:
                    error_msg = f"Failed to collect results for batch {batch_id}: {str(e)}"
                    _log.error(error_msg)
                    errors.append(error_msg)
                    skipped_count += 1
                    continue
                    
            return {"processed": processed_count, "skipped": skipped_count, "errors": errors}
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to collect completed batch results for task {task_id}: {e}")
            raise Exception(f"Failed to collect completed batch results for task {task_id}: {e}")
    
    async def _check_all_batches_completed(self, batch_task: BatchTask) -> bool:
        """Check if all batches in the task are completed."""
        for batch_id in batch_task.batch_ids:
            batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
            if not batch or batch.status != BatchStatus.COMPLETED:
                return False
        return True
    
    async def get_task_progress(self, task_id: PydanticObjectId) -> float:
        """
        Get the current progress of a task as a percentage.
        
        Args:
            task_id: Task ID
            
        Returns:
            float: Progress percentage (0-100)
            
        Raises:
            BusinessException: If task not found
            Exception: For API or database errors
        """
        try:
            # Get task information
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
            
            if not batch_task.batch_ids:
                _log.info(f"No batches found for task {task_id}")
                return 0.0
            
            # Sum up request counts from all batches
            total_requests = 0
            completed_requests = 0
            failed_requests = 0
            
            for batch_id in batch_task.batch_ids:
                try:
                    batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
                    if not batch:
                        continue
                    
                    # Get batch progress from BatchService
                    batch_progress: BatchRequestCountsDTO = self.batch_service.get_batch_progress(batch)
                    
                    total_requests += batch_progress.total
                    completed_requests += batch_progress.completed
                    failed_requests += batch_progress.failed
                    
                except Exception as e:
                    _log.warning(f"Failed to get progress for batch {batch_id}: {e}")
                    continue
            
            # Calculate overall progress percentage
            if total_requests == 0:
                return 0.0
            
            progress_percentage = ((completed_requests + failed_requests) / total_requests) * 100
            
            # Ensure we don't exceed 100%
            return min(progress_percentage, 100.0)
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to get task progress for {task_id}: {e}")
            raise Exception(f"Failed to get task progress for {task_id}: {e}")
    
    async def update_task_progress(self, task_id: PydanticObjectId) -> BatchTask:
        """
        Update task progress by aggregating all batch progress.
        
        Args:
            task_id: Task ID
            
        Returns:
            BatchTask: Updated task entity
            
        Raises:
            BusinessException: If task not found
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
            
            # Aggregate progress from all batches
            total_requests = 0
            completed_requests = 0
            failed_requests = 0
            
            for batch_id in batch_task.batch_ids:
                try:
                    batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
                    if not batch:
                        continue
                    
                    batch_progress: BatchRequestCountsDTO = self.batch_service.get_batch_progress(batch)
                    total_requests += batch_progress.total
                    completed_requests += batch_progress.completed
                    failed_requests += batch_progress.failed
                    
                except Exception as e:
                    _log.warning(f"Failed to get progress for batch {batch_id}: {e}")
                    continue
            
            # Update task progress
            batch_task.update_progress(total_requests, completed_requests, failed_requests)
            updated_task = await self.batch_task_repository.update(batch_task)
            
            return updated_task
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to update task progress for {task_id}: {e}")
            raise Exception(f"Failed to update task progress for {task_id}: {e}")
    
    async def _update_task_status_if_needed(self, batch_task: BatchTask, new_status: BatchTaskStatus) -> None:
        """Update task status if it's in the right state for transition."""
        try:
            # Only transition from created to running
            if batch_task.status != new_status:
                if new_status == BatchTaskStatus.RUNNING and batch_task.status == BatchTaskStatus.CREATED:
                    batch_task.start()
                    await self.batch_task_repository.update(batch_task)
                    
        except Exception as e:
            _log.warning(f"Failed to update task status: {e}")
            # Don't raise - this is not critical for batch starting
    
    async def pause_task(self, task_id: PydanticObjectId) -> bool:
        """
        Pause a running task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if successful
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if batch_task.status == BatchTaskStatus.RUNNING:
                batch_task.pause()
                await self.batch_task_repository.update(batch_task)
                return True
            return False
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to pause task {task_id}: {e}")
            raise Exception(f"Failed to pause task {task_id}: {e}")
    
    async def resume_task(self, task_id: PydanticObjectId) -> bool:
        """
        Resume a paused task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if successful
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if batch_task.status == BatchTaskStatus.PAUSED:
                batch_task.resume()
                await self.batch_task_repository.update(batch_task)
                return True
            return False
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to resume task {task_id}: {e}")
            raise Exception(f"Failed to resume task {task_id}: {e}")
    
    async def cancel_task(self, task_id: PydanticObjectId) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if successful
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task.is_terminal_state:
                batch_task.cancel()
                await self.batch_task_repository.update(batch_task)
                return True
            return False
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to cancel task {task_id}: {e}")
            raise Exception(f"Failed to cancel task {task_id}: {e}")
    
    async def get_task_batches(self, task_id: PydanticObjectId) -> List[Batch]:
        """
        Get all batches associated with a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List[Batch]: List of batch entities
        """
        try:
            batch_task = await self.batch_task_repository.retrieve_by_task_id(task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
            
            batches = []
            for batch_id in batch_task.batch_ids:
                try:
                    batch = await self.batch_repository.retrieve_by_batch_id(batch_id)
                    if batch:
                        batches.append(batch)
                except Exception as e:
                    _log.warning(f"Failed to retrieve batch {batch_id}: {e}")
                    continue
            
            return batches
            
        except BusinessException:
            raise
        except Exception as e:
            _log.error(f"Failed to get task batches for {task_id}: {e}")
            raise Exception(f"Failed to get task batches for {task_id}: {e}")
