"""
Dependency injection configuration for FastAPI
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from common.repository.minio_repository import MinioRepository
from common.repository.processing_candidate_repository import ProcessingCandidateRepository
from common.service.batch_manager_client_service import BatchManagerClientService
from common.service.create_batch_task_service.create_cv_parse_batch_task_service import CreateCvParseBatchTaskService

_log = logging.getLogger(__name__)


@lru_cache()
def get_minio_repository() -> MinioRepository:
    """Get MinioRepository instance"""
    return MinioRepository()


@lru_cache()
def get_batch_manager_client_service() -> BatchManagerClientService:
    """Get BatchManagerClientService instance"""
    base_url = os.getenv("BATCH_MANAGER_URL", "http://tyro-batch-manager:8000")
    timeout = int(os.getenv("BATCH_MANAGER_TIMEOUT", "30"))
    return BatchManagerClientService(base_url=base_url, timeout=timeout)


@lru_cache()
def get_processing_candidate_repository() -> ProcessingCandidateRepository:
    """Get ProcessingCandidateRepository instance"""
    return ProcessingCandidateRepository()


@lru_cache()
def get_cv_parse_batch_task_service() -> CreateCvParseBatchTaskService:
    """Get CreateCvParseBatchTaskService instance"""
    return CreateCvParseBatchTaskService(
        minio_repository=get_minio_repository(),
        batch_manager_client=get_batch_manager_client_service(),
        processing_candidate_repository=get_processing_candidate_repository()
    )