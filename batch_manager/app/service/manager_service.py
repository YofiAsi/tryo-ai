"""
ManagerService for managing batch and batch task operations.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beanie import PydanticObjectId

    from app.service.batch_service import BatchService
    from app.service.batch_task_service import BatchTaskService
    

_log = logging.getLogger(__name__)

class ManagerService:
    def __init__(self, batch_service: BatchService, batch_task_service: BatchTaskService):
        self.batch_service = batch_service
        self.batch_task_service = batch_task_service

    async def start_pending_batches(self) -> None:
        started_batches_ids = await self.batch_service.start_pending_batches()
        _log.info(f"Started {len(started_batches_ids)} batches: {started_batches_ids}")
    
    async def check_on_batches_in_progress(self) -> None:
        completed_batches_ids = await self.batch_service.check_on_batches_in_progress()
        _log.info(f"Completed {len(completed_batches_ids)} batches: {completed_batches_ids}")
    
    async def check_and_complete_batch_tasks(self) -> None:
        completed_tasks_ids = await self.batch_task_service.check_and_complete_batch_tasks()
        _log.info(f"Completed {len(completed_tasks_ids)} tasks: {completed_tasks_ids}")
        for task_id in completed_tasks_ids:
            self.notify_about_completed_task(task_id)
        
    # TODO: Implement this.
    def notify_about_completed_task(self, task_id: PydanticObjectId) -> None:
        task_id
        pass
