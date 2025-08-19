"""
Dependency injection configuration for FastAPI
"""
import logging
from functools import lru_cache

from app.service.task_create_service import TaskCreateService
from app.repository.batch_repository import BatchRepository
from app.repository.task_repository import TaskRepository
from app.repository.file_storage_repository import FileStorageRepository

_log = logging.getLogger(__name__)


@lru_cache()
def get_batch_repository() -> BatchRepository:
    """Get BatchRepository instance"""
    return BatchRepository()


@lru_cache()
def get_task_repository() -> TaskRepository:
    """Get TaskRepository instance"""
    return TaskRepository()


@lru_cache()
def get_file_storage_repository() -> FileStorageRepository:
    """Get FileStorageRepository instance"""
    return FileStorageRepository()


@lru_cache()
def get_task_create_service() -> TaskCreateService:
    """Get TaskCreateService instance"""
    batch_repo = get_batch_repository()
    task_repo = get_task_repository()
    file_storage_repo = get_file_storage_repository()
    return TaskCreateService(task_repository=task_repo, batch_repository=batch_repo, file_storage_repository=file_storage_repo)
