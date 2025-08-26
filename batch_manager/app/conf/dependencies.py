"""
Dependency injection configuration for FastAPI
"""
import logging
from functools import lru_cache
import asyncio

from app.service.batch_task_create_service import BatchTaskCreateService
from app.service.batch_task_service import BatchTaskService
from app.service.multi_key_openai_service import MultiKeyOpenAiClientService
from app.service.batch_service import BatchService
from app.repository.batch_repository import BatchRepository
from app.repository.batch_task_repository import BatchTaskRepository
from app.repository.file_storage_repository import FileStorageRepository
from app.repository.openai_client_repository import OpenAiClientRepository

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
    asyncio.create_task(multi_key_openai_client_service.init_clients())
    return multi_key_openai_client_service


@lru_cache()
def get_batch_service() -> BatchService:
    multi_key_openai_client: MultiKeyOpenAiClientService = get_multi_key_openai_client()
    file_storage_repo: FileStorageRepository = get_file_storage_repository()
    batch_repo: BatchRepository = get_batch_repository()
    return BatchService(
        multi_key_openai_client_service=multi_key_openai_client,
        batch_file_storage_repository=file_storage_repo,
        batch_repository=batch_repo
    )

@lru_cache()
def get_batch_task_service() -> BatchTaskService:
    batch_task_repo: BatchTaskRepository = get_batch_task_repository()
    batch_repo: BatchRepository = get_batch_repository()
    batch_service: BatchService = get_batch_service()
    return BatchTaskService(
        batch_task_repository=batch_task_repo,
        batch_repository=batch_repo,
        batch_service=batch_service
    )