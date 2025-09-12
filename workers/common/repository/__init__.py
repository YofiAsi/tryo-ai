"""Repository modules for data access operations."""

from .candidate_repository import CandidateRepository
from .minio_repository import MinioRepository
from .processing_candidate_repository import ProcessingCandidateRepository

__all__ = ["CandidateRepository", "MinioRepository", "ProcessingCandidateRepository"]
