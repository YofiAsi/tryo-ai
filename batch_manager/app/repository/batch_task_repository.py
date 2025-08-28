"""
BatchTaskRepository for managing batch tasks in the database.
"""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, List

from app.conf.page_response import PageResponse
from app.entity.batch_entity import Batch, BatchStatus
from app.entity.batch_task_entity import BatchTask, BatchTaskStatus
from app.errors.business_exception import BusinessException, ErrorCodes

if TYPE_CHECKING:
    from datetime import datetime

    from beanie import PydanticObjectId

_log = logging.getLogger(__name__)


class BatchTaskRepository:
    """
    BatchTask Repository class

    This class is responsible for handling all the database operations related to the BatchTask entity.
    BatchTask entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self) -> None:
        _log.debug("BatchTaskRepository Connecting to database")

    async def create(self, batch_task: BatchTask) -> BatchTask:
        _log.debug(f"BatchTaskRepository Creating batch_task: {batch_task.id}")
        await BatchTask.insert(batch_task)
        _log.debug("BatchTaskRepository BatchTask created")
        return batch_task

    async def bulk_create(self, batch_tasks: List[BatchTask]) -> List[BatchTask]:
        """
        Create multiple batch_tasks in a single database operation.
        
        Args:
            batch_tasks: List of BatchTask entities to create
            
        Returns:
            List of created BatchTask entities with assigned IDs
            
        Raises:
            BusinessException: If bulk creation fails
        """
        if not batch_tasks:
            _log.warning("BatchTaskRepository No batch_tasks to create")
            return []
        
        _log.debug(f"BatchTaskRepository Creating {len(batch_tasks)} batch_tasks in bulk")
        
        try:
            # Use Beanie's insert_many for bulk insertion
            await BatchTask.insert_many(batch_tasks)
            _log.info(f"BatchTaskRepository Successfully created {len(batch_tasks)} batch_tasks")
            return batch_tasks
        except Exception as e:
            _log.error(f"BatchTaskRepository Failed to bulk create batch_tasks: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to create batch_tasks: {str(e)}")

    async def update(self, batch_task: BatchTask) -> BatchTask:
        _log.debug(f"BatchTaskRepository Updating batch_task: {batch_task.id}")
        if batch_task.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "BatchTask id is required for update")
        await batch_task.replace()
        _log.debug("BatchTaskRepository BatchTask updated")
        return batch_task

    async def delete(self, id: str) -> None:
        _log.debug(f"BatchTaskRepository Deleting batch_task: {id}")
        result = await BatchTask.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"BatchTask not found: {id}")

        await result.delete()
        _log.debug("BatchTaskRepository BatchTask deleted")

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-created_at") -> PageResponse[BatchTask]:
        _log.debug("BatchTaskRepository list request")
        if query is None:
            query_dict = {}
        else:
            query_dict = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await BatchTask.find(query_dict).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = BatchTask.find(query_dict).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        _log.debug("BatchTaskRepository Tasks retrieved")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count(self, query_dict: dict[str, Any]) -> int:
        _log.debug(f"BatchTaskRepository Counting batch_tasks with query: {query_dict}")
        doc = BatchTask.find(query_dict)
        result = await doc.count()
        _log.debug("BatchTaskRepository Tasks counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> BatchTask:
        _log.debug(f"BatchTaskRepository Retrieving batch_task: {id}")
        batch_task = await BatchTask.find_one({"_id": id})
        if not batch_task:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"BatchTask not found: {id}")
        _log.debug("BatchTaskRepository BatchTask retrieved")
        return batch_task

    async def retrieve_by_task_id(self, id: PydanticObjectId) -> BatchTask:
        _log.debug(f"BatchTaskRepository Retrieving batch_task by id: {id}")
        batch_task = await BatchTask.find_one({"_id": id})
        if not batch_task:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"BatchTask not found: {id}")
        _log.debug("BatchTaskRepository BatchTask retrieved")
        return batch_task

    async def find_by_status(self, status: BatchTaskStatus, page: int = 1, size: int = 10) -> PageResponse[BatchTask]:
        _log.debug(f"BatchTaskRepository Finding batch_tasks by status: {status}")
        query = {"status": status.value}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await BatchTask.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = BatchTask.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchTaskRepository Tasks found by status")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_api_key_id(self, api_key_id: str, page: int = 1, size: int = 10) -> PageResponse[BatchTask]:
        _log.debug(f"BatchTaskRepository Finding batch_tasks by api_key_id: {api_key_id}")
        query = {"api_key_id": api_key_id}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await BatchTask.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = BatchTask.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchTaskRepository Tasks found by api_key_id")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_running_tasks(self, page: int = 1, size: int = 10) -> PageResponse[BatchTask]:
        _log.debug("BatchTaskRepository Finding running batch_tasks")
        query = {"status": BatchTaskStatus.RUNNING.value}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await BatchTask.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = BatchTask.find(query).skip((page-1) * size).limit(size).sort("-started_at")
        content = await document.to_list()
        _log.debug("BatchTaskRepository Running batch_tasks found")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count_by_status(self, status: BatchTaskStatus) -> int:
        _log.debug(f"BatchTaskRepository Counting batch_tasks by status: {status}")
        query = {"status": status.value}
        result = await BatchTask.find(query).count()
        _log.debug("BatchTaskRepository Tasks counted by status")
        return result

    async def find_tasks_by_batch_id(self, batch_id: PydanticObjectId) -> List[BatchTask]:
        """
        Get all batch tasks that have the batch id in their batch_ids list.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            List[BatchTask]: List of batch tasks
        """
        batch_tasks = await BatchTask.find({"batch_ids": {"$in": [batch_id]}}).to_list()
        return batch_tasks

    async def find_tasks_created_after(self, after_date: datetime, page: int = 1, size: int = 10) -> PageResponse[BatchTask]:
        _log.debug(f"BatchTaskRepository Finding batch_tasks created after: {after_date}")
        query = {"created_at": {"$gte": after_date}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await BatchTask.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = BatchTask.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchTaskRepository Tasks found by creation date")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def get_completed_running_tasks_iterator(self) -> AsyncIterator[BatchTask]:
        """
        Stream all BatchTask documents that are RUNNING and whose referenced
        batches are ALL COMPLETED. Results are parsed as BatchTask models.
        """
        pipeline = [
            # Only tasks that are currently RUNNING and actually have batches
            {"$match": {
                "status": BatchTaskStatus.RUNNING.value,
                "batch_ids": {"$ne": []},
            }},
            {
                # Pull ONLY the not-completed batches among the referenced ids
                "$lookup": {
                    "from": Batch.get_collection_name(),
                    "let": {"ids": "$batch_ids"},
                    "pipeline": [
                        {"$match": {"$expr": {"$in": ["$_id", "$$ids"]}}},
                        {"$match": {"status": {"$ne": BatchStatus.COMPLETED.value}}},
                        {"$limit": 1},                 # short-circuit: we just need to know if any exist
                    ],
                    "as": "incomplete_batches",
                }
            },
            # Keep only tasks with zero not-completed batches => all completed
            {"$match": {"incomplete_batches": {"$size": 0}}},
            # Remove lookup helper so projection to BatchTask is clean
            {"$project": {"incomplete_batches": 0}},
        ]

        # Parse each aggregation result back into a BatchTask model
        query = BatchTask.aggregate(pipeline, projection_model=BatchTask)

        # Beanie's aggregation query supports async iteration over results
        async for task in query:
            yield task
