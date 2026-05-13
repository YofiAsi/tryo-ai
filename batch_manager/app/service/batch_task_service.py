"""
BatchTaskService for managing batch processing tasks.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

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
    
    async def get_next_pending_batch(self, batch_task: BatchTask) -> Optional[Batch]:
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
    
    async def update_task_status_running_if_needed(self, batch_task_id: PydanticObjectId) -> bool:
        """Update task status if it's in the right state for transition."""
        try:
            batch_task = await self.batch_task_repository.retrieve(batch_task_id)
            if not batch_task:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {batch_task_id}")

            # Only transition from created to running
            if batch_task.status == BatchTaskStatus.CREATED:
                batch_task.start()
                await self.batch_task_repository.update(batch_task)
            return True
        except Exception as e:
            _log.error(f"Failed to update task status: {e}")
            raise Exception(f"Failed to update task status: {e}")
    
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

    async def get_batch_tasks_from_batch_id(self, batch_id: PydanticObjectId) -> List[BatchTask]:
        """
        Get all the batch tasks associated with a batch id.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            List[BatchTask]: List of batch tasks
        """
        batch_tasks = await self.batch_task_repository.find_tasks_by_batch_id(batch_id)
        return batch_tasks

    def get_completed_running_tasks_iterator(self) -> AsyncIterator[BatchTask]:
        """
        Get all the batch tasks that are in progress.
        """
        return self.batch_task_repository.get_completed_running_tasks_iterator()

    async def complete_batch_task(self, batch_task: BatchTask) -> None:
        """
        Complete a batch task.
        """
        await self.update_task_status(batch_task.id, BatchTaskStatus.COMPLETED)

    async def check_and_complete_batch_tasks(self) -> List[PydanticObjectId]:
        tasks: AsyncIterator[BatchTask] = self.get_completed_running_tasks_iterator()
        completed_tasks: List[PydanticObjectId] = []
        async for task in tasks:
            await self.complete_batch_task(task)
            completed_tasks.append(task.id)
        
        return completed_tasks
