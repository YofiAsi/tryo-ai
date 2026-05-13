"""
Dependency injection configuration for FastAPI
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from common.repository.candidate_repository import CandidateRepository
from common.repository.minio_repository import MinioRepository
from common.repository.processing_candidate_repository import ProcessingCandidateRepository
from common.service.batch_manager_client_service import BatchManagerClientService
from common.service.candidate_finalization_service import CandidateFinalizationService
from common.service.create_batch_task_service.create_cv_parse_batch_task_service import CreateCvParseBatchTaskService
from common.service.create_batch_task_service.create_embed_task_service import CreateEmbedTaskService
from common.service.process_batch_task_results_service.cv_parse_results_processor_service import CvParseResultsProcessorService
from common.service.process_batch_task_results_service.embed_results_processor_service import EmbedResultsProcessorService

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
def get_candidate_repository() -> CandidateRepository:
    """Get CandidateRepository instance"""
    return CandidateRepository()


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


@lru_cache()
def get_embed_task_service() -> CreateEmbedTaskService:
    """Get CreateEmbedTaskService instance"""
    return CreateEmbedTaskService(
        batch_manager_client=get_batch_manager_client_service(),
        processing_candidate_repository=get_processing_candidate_repository()
    )


@lru_cache()
def get_cv_parse_results_processor_service() -> CvParseResultsProcessorService:
    """Get CvParseResultsProcessorService instance"""
    return CvParseResultsProcessorService(
        minio_repository=get_minio_repository(),
        processing_candidate_repository=get_processing_candidate_repository()
    )


@lru_cache()
def get_embed_results_processor_service() -> EmbedResultsProcessorService:
    """Get EmbedResultsProcessorService instance"""
    return EmbedResultsProcessorService(
        minio_repository=get_minio_repository(),
        processing_candidate_repository=get_processing_candidate_repository()
    )


@lru_cache()
def get_candidate_finalization_service() -> CandidateFinalizationService:
    """Get CandidateFinalizationService instance"""
    return CandidateFinalizationService(
        processing_candidate_repository=get_processing_candidate_repository(),
        candidate_repository=get_candidate_repository()
    )