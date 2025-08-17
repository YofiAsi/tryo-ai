import json
import logging
from typing import Optional
import uuid

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.task_entity import Task
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class TaskRepository:
    """
    Task Repository class

    This class is responsible for handling all the database operations related to the Task entity.
    Task entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug(f"TaskRepository Connecting to database")

    async def create(self, task: Task) -> Task:
        _log.debug(f"TaskRepository Creating task: {task}")
        result = await Task.insert(task)
        _log.debug(f"TaskRepository Task created")
        return result

    async def update(self, task: Task) -> Task | None:
        _log.debug(f"TaskRepository Updating task")
        if task.task_id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Task id is required for update")
        result = await task.replace()
        _log.debug(f"TaskRepository Task updated")
        return result

    async def delete(self, task_id: str):
        _log.debug(f"TaskRepository Deleting task: {task_id}")
        result = await Task.find_one({"_id": task_id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")

        await result.delete()
        _log.debug(f"TaskRepository Task deleted")
        return

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-id") -> PageResponse:
        _log.debug(f"TaskRepository list request")
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
        page_content = content
        _log.debug(f"TaskRepository Tasks retrieved")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        _log.debug(f"TaskRepository Counting tasks with query: {query}")
        doc = Task.find(query)
        result = await doc.count()
        _log.debug(f"TaskRepository Tasks counted")
        return result

    async def retrieve(self, task_id: str) -> Task | None:
        _log.debug(f"TaskRepository Retrieving task: {task_id}")
        doc = await Task.find_one({"_id": task_id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
        result = doc
        _log.debug(f"TaskRepository Task retrieved")
        return result

    async def retrieve_by_type(self, task_type: str) -> Optional[Task]:
        _log.debug(f"TaskRepository Retrieving task by type: {task_type}")
        doc = await Task.find_one({"type": task_type})
        if not doc:
            return None
        result = doc
        _log.debug(f"TaskRepository Task retrieved")
        return result

    async def retrieve_by_status(self, status: str) -> list[Task]:
        _log.debug(f"TaskRepository Retrieving tasks by status: {status}")
        docs = await Task.find({"status": status}).to_list()
        _log.debug(f"TaskRepository Tasks retrieved")
        return docs

    # Synchronous methods for Celery workers
    def create_sync(self, task: Task) -> Task:
        _log.debug(f"TaskRepository Creating task synchronously: {task}")
        # Note: This is a simplified version for Celery workers
        # In production, you might want to use a different approach
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(Task.insert(task))
        _log.debug(f"TaskRepository Task created synchronously")
        return result

    def update_sync(self, task: Task) -> Task | None:
        _log.debug(f"TaskRepository Updating task synchronously")
        if task.task_id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Task id is required for update")
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(task.replace())
        _log.debug(f"TaskRepository Task updated synchronously")
        return result

    def retrieve_sync(self, id: PydanticObjectId) -> Task | None:
        _log.debug(f"TaskRepository Retrieving task synchronously: {id}")
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        doc = loop.run_until_complete(Task.find_one({"_id": id}))
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {id}")
        result = doc
        _log.debug(f"TaskRepository Task retrieved synchronously")
        return result
