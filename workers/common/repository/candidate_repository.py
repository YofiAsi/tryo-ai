"""
Repository for CandidateDocument operations.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional

from common.entity.candidate_entity import CandidateDocument

if TYPE_CHECKING:
    from beanie import PydanticObjectId

logger = logging.getLogger(__name__)


class CandidateRepository:
    """Repository for managing CandidateDocument operations."""
    
    def __init__(self) -> None:
        """Initialize the repository."""
        pass
    
    async def create_candidate(self, candidate: CandidateDocument) -> CandidateDocument:
        """
        Create a new CandidateDocument.
        
        Args:
            candidate: CandidateDocument instance to save
            
        Returns:
            Saved CandidateDocument with generated ID
            
        Raises:
            Exception: If creation fails
        """
        try:
            await candidate.save()
            logger.debug(f"Created CandidateDocument: {candidate.id}")
            return candidate
        except Exception as e:
            logger.error(f"Failed to create CandidateDocument: {e}")
            raise
    
    async def bulk_create_candidates(self, candidates: List[CandidateDocument]) -> List[CandidateDocument]:
        """
        Create multiple CandidateDocument instances in bulk.
        
        Args:
            candidates: List of CandidateDocument instances to save
            
        Returns:
            List of saved CandidateDocument instances
            
        Raises:
            Exception: If bulk creation fails
        """
        if not candidates:
            return []
        
        try:
            await CandidateDocument.insert_many(candidates)
            
            logger.info(f"Bulk created {len(candidates)} CandidateDocument instances")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to bulk create CandidateDocument instances: {e}")
            raise
    
    async def find_by_id(self, candidate_id: PydanticObjectId) -> Optional[CandidateDocument]:
        """
        Find CandidateDocument by ID.
        
        Args:
            candidate_id: ID of the candidate
            
        Returns:
            CandidateDocument if found, None otherwise
            
        Raises:
            Exception: If query fails
        """
        try:
            candidate = await CandidateDocument.find_one(CandidateDocument.id == candidate_id)
            if candidate:
                logger.debug(f"Found CandidateDocument: {candidate_id}")
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to find CandidateDocument by ID '{candidate_id}': {e}")
            raise
    
    async def count_all(self) -> int:
        """
        Count all CandidateDocument instances.
        
        Returns:
            Number of CandidateDocument instances
            
        Raises:
            Exception: If count fails
        """
        try:
            count = await CandidateDocument.count()
            logger.debug(f"Found {count} CandidateDocument instances")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count CandidateDocument instances: {e}")
            raise
