"""
Dependency injection configuration for FastAPI
"""
import logging
from functools import lru_cache

from app.service.batch_task_create_service import BatchTaskCreateService
from app.repository.batch_repository import BatchRepository
from app.repository.batch_task_repository import BatchTaskRepository
from app.repository.file_storage_repository import FileStorageRepository

_log = logging.getLogger(__name__)


@lru_cache()
def get_batch_repository() -> BatchRepository:
    """Get BatchRepository instance"""
    return BatchRepository()


@lru_cache()
def get_batch_task_repository() -> BatchTaskRepository:
    """Get BatchTaskRepository instance"""
    return BatchTaskRepository()


@lru_cache()
def get_file_storage_repository() -> FileStorageRepository:
    """Get FileStorageRepository instance"""
    return FileStorageRepository()


@lru_cache()
def get_batch_task_create_service() -> BatchTaskCreateService:
    """Get BatchTaskCreateService instance"""
    batch_repo = get_batch_repository()
    batch_task_repo = get_batch_task_repository()
    file_storage_repo = get_file_storage_repository()
    return BatchTaskCreateService(batch_task_repository=batch_task_repo, batch_repository=batch_repo, file_storage_repository=file_storage_repo)
