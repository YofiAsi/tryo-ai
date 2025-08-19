import json
import logging
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.task_entity import Task, TaskStatus
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class TaskRepository:
    """
    Task Repository class

    This class is responsible for handling all the database operations related to the Task entity.
    Task entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug("TaskRepository Connecting to database")

    async def create(self, task: Task) -> Task:
        _log.debug(f"TaskRepository Creating task: {task.name}")
        result = await Task.insert(task)
        _log.debug("TaskRepository Task created")
        return result

    async def bulk_create(self, tasks: List[Task]) -> List[Task]:
        """
        Create multiple tasks in a single database operation.
        
        Args:
            tasks: List of Task entities to create
            
        Returns:
            List of created Task entities with assigned IDs
            
        Raises:
            BusinessException: If bulk creation fails
        """
        if not tasks:
            _log.warning("TaskRepository No tasks to create")
            return []
        
        _log.debug(f"TaskRepository Creating {len(tasks)} tasks in bulk")
        
        try:
            # Use Beanie's insert_many for bulk insertion
            result = await Task.insert_many(tasks)
            _log.info(f"TaskRepository Successfully created {len(result)} tasks")
            return result
        except Exception as e:
            _log.error(f"TaskRepository Failed to bulk create tasks: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, f"Failed to create tasks: {str(e)}")

    async def update(self, task: Task) -> Task:
        _log.debug(f"TaskRepository Updating task: {task.task_id}")
        if task.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Task id is required for update")
        result = await task.replace()
        _log.debug("TaskRepository Task updated")
        return result

    async def delete(self, id: PydanticObjectId):
        _log.debug(f"TaskRepository Deleting task: {id}")
        result = await Task.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {id}")

        await result.delete()
        _log.debug("TaskRepository Task deleted")

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-created_at") -> PageResponse:
        _log.debug("TaskRepository list request")
        if query is None:
            query = {}
        else:
            query = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Task.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Task.find(query).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        _log.debug("TaskRepository Tasks retrieved")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        _log.debug(f"TaskRepository Counting tasks with query: {query}")
        doc = Task.find(query)
        result = await doc.count()
        _log.debug("TaskRepository Tasks counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> Task:
        _log.debug(f"TaskRepository Retrieving task: {id}")
        doc = await Task.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {id}")
        _log.debug("TaskRepository Task retrieved")
        return doc

    async def retrieve_by_task_id(self, task_id: uuid.UUID) -> Task:
        _log.debug(f"TaskRepository Retrieving task by task_id: {task_id}")
        doc = await Task.find_one({"task_id": task_id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
        _log.debug("TaskRepository Task retrieved")
        return doc

    async def find_by_status(self, status: TaskStatus, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"TaskRepository Finding tasks by status: {status}")
        query = {"status": status.value}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Task.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Task.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("TaskRepository Tasks found by status")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_api_key_id(self, api_key_id: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"TaskRepository Finding tasks by api_key_id: {api_key_id}")
        query = {"api_key_id": api_key_id}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Task.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Task.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("TaskRepository Tasks found by api_key_id")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_running_tasks(self, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug("TaskRepository Finding running tasks")
        query = {"status": TaskStatus.RUNNING.value}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Task.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Task.find(query).skip((page-1) * size).limit(size).sort("-started_at")
        content = await document.to_list()
        _log.debug("TaskRepository Running tasks found")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count_by_status(self, status: TaskStatus) -> int:
        _log.debug(f"TaskRepository Counting tasks by status: {status}")
        query = {"status": status.value}
        result = await Task.find(query).count()
        _log.debug("TaskRepository Tasks counted by status")
        return result

    async def find_tasks_created_after(self, after_date: datetime, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"TaskRepository Finding tasks created after: {after_date}")
        query = {"created_at": {"$gte": after_date}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Task.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Task.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("TaskRepository Tasks found by creation date")
        return PageResponse(content=content, page=page, size=size, total=total_count)
