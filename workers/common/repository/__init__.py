"""Repository modules for data access operations."""

from .minio_repository import MinioRepository
from .processing_candidate_repository import ProcessingCandidateRepository

__all__ = ["MinioRepository", "ProcessingCandidateRepository"]
