"""
Candidate finalization service - processes candidates ready for finalization.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from common.consts.enums import CandidateStatus
from common.entity.candidate_entity import CandidateDocument, CandidateMetadata, Embeddings

if TYPE_CHECKING:
    from common.entity.candidate_entity import ProcessingCandidate
    from common.repository.candidate_repository import CandidateRepository
    from common.repository.processing_candidate_repository import ProcessingCandidateRepository

logger = logging.getLogger(__name__)


@dataclass
class FinalizationStats:
    """Statistics for candidate finalization processing."""
    total_processed: int = 0
    successful_finalizations: int = 0
    failed_finalizations: int = 0


class CandidateFinalizationService:
    """Service for finalizing candidates from ProcessingCandidate to CandidateDocument."""
    
    def __init__(self, 
                 processing_candidate_repository: ProcessingCandidateRepository,
                 candidate_repository: CandidateRepository):
        """Initialize the service with repositories."""
        self.processing_candidate_repository = processing_candidate_repository
        self.candidate_repository = candidate_repository
    
    async def finalize_candidates(self) -> FinalizationStats:
        """
        Process all candidates with 'pending_finalization' status.
        Creates CandidateDocument for each and updates ProcessingCandidate status.
        
        Returns:
            FinalizationStats with processing statistics
        """
        logger.info("Starting candidate finalization process")
        
        stats = FinalizationStats()
        candidates_to_update = []
        candidates_to_create = []
        
        try:
            # Process candidates with pending_finalization status
            async for processing_candidate in self.processing_candidate_repository.find_by_status_iterator("pending_finalization"):
                stats.total_processed += 1
                
                try:
                    # Create CandidateDocument from ProcessingCandidate
                    candidate_document = self._create_candidate_document(processing_candidate)
                    candidates_to_create.append(candidate_document)
                    
                    # Mark processing candidate for status update
                    processing_candidate.status = "completed"
                    candidates_to_update.append(processing_candidate)
                    
                    logger.debug(f"Prepared candidate {processing_candidate.id} for finalization")
                    
                except Exception as e:
                    logger.error(f"Failed to prepare candidate {processing_candidate.id} for finalization: {e}")
                    # Mark as failed
                    processing_candidate.status = "failed"
                    if isinstance(processing_candidate.errors, list):
                        processing_candidate.errors.append(f"Finalization failed: {str(e)}")
                    else:
                        processing_candidate.errors = [f"Finalization failed: {str(e)}"]
                    candidates_to_update.append(processing_candidate)
                    stats.failed_finalizations += 1
                    continue
            
            # Bulk operations for better performance
            if candidates_to_create:
                logger.info(f"Bulk creating {len(candidates_to_create)} CandidateDocuments")
                await self.candidate_repository.bulk_create_candidates(candidates_to_create)
                stats.successful_finalizations = len(candidates_to_create)
            
            if candidates_to_update:
                logger.info(f"Bulk updating {len(candidates_to_update)} ProcessingCandidates")
                await self.processing_candidate_repository.bulk_update(candidates_to_update)
        
        except Exception as e:
            logger.error(f"Error during candidate finalization process: {e}")
            raise
        
        logger.info(f"Finalization complete. Stats: {stats}")
        return stats
    
    def _create_candidate_document(self, processing_candidate: ProcessingCandidate) -> CandidateDocument:
        """
        Create a CandidateDocument from a ProcessingCandidate.
        
        Args:
            processing_candidate: ProcessingCandidate to convert
            
        Returns:
            CandidateDocument ready for insertion
            
        Raises:
            ValueError: If processing candidate is missing required data
        """
        if not processing_candidate.parsed_data:
            raise ValueError(f"ProcessingCandidate {processing_candidate.id} has no parsed data")
        
        if not processing_candidate.embeddings:
            raise ValueError(f"ProcessingCandidate {processing_candidate.id} has no embeddings")
        
        # Create metadata from processing candidate
        metadata = CandidateMetadata(
            file_id=processing_candidate.file_id,
            original_cv_minio_path=processing_candidate.original_cv_minio_path,
            txt_cv_minio_path=processing_candidate.txt_cv_minio_path,
            parse_model=processing_candidate.parse_model
        )
        
        # Create embeddings
        embeddings = Embeddings(
            general=processing_candidate.embeddings.general,
            skills=processing_candidate.embeddings.skills,
            work_experience=processing_candidate.embeddings.work_experience
        )
        
        # Create CandidateDocument with all relevant properties
        candidate_document = CandidateDocument(
            status=CandidateStatus.COMPLETED,
            embeddings=embeddings,
            name=processing_candidate.parsed_data.name,
            gender=processing_candidate.parsed_data.gender,
            year_of_birth=processing_candidate.parsed_data.year_of_birth,
            city=processing_candidate.parsed_data.city,
            country=processing_candidate.parsed_data.country,
            email=processing_candidate.parsed_data.email,
            phone=processing_candidate.parsed_data.phone,
            title=processing_candidate.parsed_data.title,
            seniority_level=processing_candidate.parsed_data.seniority_level,
            education=processing_candidate.parsed_data.education,
            work_experience=processing_candidate.parsed_data.work_experience,
            certifications=processing_candidate.parsed_data.certifications,
            skills=processing_candidate.parsed_data.skills,
            languages=processing_candidate.parsed_data.languages,
            keywords=processing_candidate.parsed_data.keywords,
            links=processing_candidate.parsed_data.links,
            raw_cv=processing_candidate.raw_cv,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
        
        return candidate_document
