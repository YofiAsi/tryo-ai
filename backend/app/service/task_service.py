import logging
import uuid
from typing import Optional
from datetime import datetime, timezone

from fastapi import Depends

from app.conf.page_response import PageResponse
from app.entity.task_entity import Task, TaskType, TaskStatus
from app.errors.business_exception import BusinessException, ErrorCodes
from app.repository.task_repository import TaskRepository
from app.schema.tasks_dto import CVProcessingTaskDTO

_log = logging.getLogger(__name__)


class TaskService:
    """
    Task Business Logic Service that is responsible for handling business logic for Task entity operations.

    Attributes:
    task_repository: TaskRepository
        Repository for Task entity operations

    """

    def __init__(self, task_repository: TaskRepository = Depends()):
        _log.info("TaskService Initializing")
        self.repository = task_repository

    async def retrieve(self, id: uuid.UUID) -> Optional[Task]:
        _log.debug(f"TaskService Retrieving task: {id}")
        
        final_task = await self.repository.retrieve(id)
        if final_task is None:
            _log.error("TaskService Task not found")
            return None
        _log.debug("TaskService Task retrieved")
        return final_task

    async def find(self, query, page: int, size: int, sort: str = "_id") -> PageResponse[Task]:
        _log.debug("TaskService list request")
        entity_page_response = await self.repository.find(query, page, size, sort)
        page_response = PageResponse[Task](
            content=entity_page_response.content,
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug("TaskService Tasks retrieved")
        return page_response

    async def delete(self, id: uuid.UUID):
        _log.debug(f"Deleting task: {id}")
        await self.repository.delete(id)
        _log.debug("Deleted task")

    async def count(self, query: dict) -> int:
        _log.debug(f"TaskService Counting tasks with query: {query}")
        result = await self.repository.count(query)
        _log.debug(f"TaskService Tasks counted: {result}")
        return result

    async def create_cv_processing_task(self, task_data: CVProcessingTaskDTO) -> Task:
        _log.debug(f"TaskService Creating CV processing task")
        
        # Create new task in database
        new_task = Task(
            task_id=uuid.uuid4(),
            type=TaskType.CV_PARSING,
            status=TaskStatus.PENDING,
            progress_percentage=0.0,
            data=task_data,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Save task to database
        created_task = await self.repository.create(new_task)
        _log.debug(f"TaskService CV processing task created in database: {created_task.task_id}")
        
        
        return created_task

    async def update_task_status(self, id: uuid.UUID, status: TaskStatus, progress_percentage: Optional[float] = None) -> Task:
        _log.debug(f"TaskService Updating task status: {id} to {status}")
        
        task = await self.repository.retrieve(id)
        if not task:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {id}")
        
        task.status = status
        if progress_percentage is not None:
            task.progress_percentage = progress_percentage
        
        updated_task = await self.repository.update(task)
        _log.debug(f"TaskService Task status updated")
        return updated_task

    async def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        _log.debug(f"TaskService Retrieving tasks by status: {status}")
        tasks = await self.repository.retrieve_by_status(status.value)
        _log.debug(f"TaskService Tasks retrieved by status: {len(tasks)}")
        return tasks

    async def get_tasks_by_type(self, task_type: TaskType) -> Optional[Task]:
        _log.debug(f"TaskService Retrieving task by type: {task_type}")
        task = await self.repository.retrieve_by_type(task_type.value)
        _log.debug(f"TaskService Task retrieved by type")
        return task