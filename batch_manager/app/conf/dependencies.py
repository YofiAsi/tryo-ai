"""
Dependency injection configuration for FastAPI
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING

from app.repository.batch_repository import BatchRepository
from app.repository.batch_task_repository import BatchTaskRepository
from app.repository.file_storage_repository import FileStorageRepository
from app.repository.openai_client_repository import OpenAiClientRepository
from app.service.batch_download_queue_service import BatchDownloadQueueService
from app.service.batch_scheduler_service import BatchSchedulerService
from app.service.batch_task_create_service import BatchTaskCreateService
from app.service.manager_service import ManagerService
from app.service.multi_key_openai_service import MultiKeyOpenAiClientService

if TYPE_CHECKING:
    from app.service.batch_service import BatchService
    from app.service.batch_task_service import BatchTaskService

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

# Not a singleton
def get_batch_task_create_service() -> BatchTaskCreateService:
    """Get BatchTaskCreateService instance"""
    batch_repo: BatchRepository = get_batch_repository()
    batch_task_repo: BatchTaskRepository = get_batch_task_repository()
    file_storage_repo: FileStorageRepository = get_file_storage_repository()
    return BatchTaskCreateService(batch_task_repository=batch_task_repo, batch_repository=batch_repo, file_storage_repository=file_storage_repo)

@lru_cache()
def get_openai_client_repository() -> OpenAiClientRepository:
    return OpenAiClientRepository()


@lru_cache()
def get_multi_key_openai_client() -> MultiKeyOpenAiClientService:
    openai_client_repo: OpenAiClientRepository = get_openai_client_repository()
    multi_key_openai_client_service = MultiKeyOpenAiClientService(openai_client_repository=openai_client_repo)
    return multi_key_openai_client_service


# Global instances to handle circular dependency
_batch_service_instance: BatchService | None = None
_batch_task_service_instance: BatchTaskService | None = None
_batch_download_queue_service_instance: BatchDownloadQueueService | None = None


def _initialize_services() -> None:
    """Initialize both services together to handle circular dependency"""
    global _batch_service_instance, _batch_task_service_instance
    
    if _batch_service_instance is None or _batch_task_service_instance is None:
        # Import here to avoid circular import at module level
        from app.service.batch_service import BatchService
        from app.service.batch_task_service import BatchTaskService
        
        # Get all required dependencies
        multi_key_openai_client: MultiKeyOpenAiClientService = get_multi_key_openai_client()
        file_storage_repo: FileStorageRepository = get_file_storage_repository()
        batch_repo: BatchRepository = get_batch_repository()
        batch_task_repo: BatchTaskRepository = get_batch_task_repository()
        
        # Create BatchTaskService first without BatchService dependency
        _batch_task_service_instance = BatchTaskService(
            batch_task_repository=batch_task_repo,
            batch_repository=batch_repo,
            batch_service=None  # type: ignore # Will be set after BatchService creation
        )
        
        # Create BatchService with BatchTaskService
        _batch_service_instance = BatchService(
            multi_key_openai_client_service=multi_key_openai_client,
            batch_file_storage_repository=file_storage_repo,
            batch_repository=batch_repo,
            batch_task_service=_batch_task_service_instance
        )
        
        # Complete the circular dependency by setting batch_service on BatchTaskService
        _batch_task_service_instance.batch_service = _batch_service_instance


def get_batch_service() -> BatchService:
    """Get BatchService instance with circular dependency handling"""
    _initialize_services()
    return _batch_service_instance  # type: ignore


def get_batch_task_service() -> BatchTaskService:
    """Get BatchTaskService instance with circular dependency handling"""
    _initialize_services()
    return _batch_task_service_instance  # type: ignore


@lru_cache()
def get_manager_service() -> ManagerService:
    """Get ManagerService instance"""
    batch_service: BatchService = get_batch_service()
    batch_task_service: BatchTaskService = get_batch_task_service()
    return ManagerService(
        batch_service=batch_service,
        batch_task_service=batch_task_service
    )


async def get_batch_download_queue_service() -> BatchDownloadQueueService:
    """Get BatchDownloadQueueService singleton instance"""
    global _batch_download_queue_service_instance
    
    if _batch_download_queue_service_instance is None:
        batch_service: BatchService = get_batch_service()
        batch_repository: BatchRepository = get_batch_repository()
        _batch_download_queue_service_instance = await BatchDownloadQueueService.get_instance(
            batch_service=batch_service,
            batch_repository=batch_repository
        )
    
    return _batch_download_queue_service_instance


@lru_cache()
def get_batch_scheduler_service() -> BatchSchedulerService:
    """Get BatchSchedulerService instance"""
    manager_service: ManagerService = get_manager_service()
    return BatchSchedulerService(manager_service=manager_service)