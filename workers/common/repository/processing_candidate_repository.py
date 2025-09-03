"""
Repository for ProcessingCandidate operations with bulk update capabilities.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Sequence, Union
from uuid import UUID

from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In

from common.entity.candidate_entity import ProcessingCandidate

logger = logging.getLogger(__name__)


class ProcessingCandidateRepository:
    """Repository for managing ProcessingCandidate documents with bulk operations."""
    
    def __init__(self) -> None:
        """Initialize the repository."""
        pass
    
    async def create_candidate(self, candidate: ProcessingCandidate) -> ProcessingCandidate:
        """
        Create a new ProcessingCandidate document.
        
        Args:
            candidate: ProcessingCandidate instance to save
            
        Returns:
            Saved ProcessingCandidate with generated ID
            
        Raises:
            Exception: If creation fails
        """
        try:
            await candidate.save()
            logger.debug(f"Created ProcessingCandidate: {candidate.id}")
            return candidate
        except Exception as e:
            logger.error(f"Failed to create ProcessingCandidate: {e}")
            raise
    
    async def bulk_create_candidates(self, candidates: List[ProcessingCandidate]) -> List[ProcessingCandidate]:
        """
        Create multiple ProcessingCandidate documents in bulk.
        
        Args:
            candidates: List of ProcessingCandidate instances to save
            
        Returns:
            List of saved ProcessingCandidate instances
            
        Raises:
            Exception: If bulk creation fails
        """
        if not candidates:
            return []
        
        try:
            await ProcessingCandidate.insert_many(candidates)
            
            logger.info(f"Bulk created {len(candidates)} ProcessingCandidate documents")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to bulk create ProcessingCandidate documents: {e}")
            raise
    
    async def update_status_bulk(self, candidate_ids: Sequence[Union[UUID, PydanticObjectId]], new_status: str) -> int:
        """
        Update status for multiple ProcessingCandidate documents efficiently.
        
        Args:
            candidate_ids: List of candidate IDs to update
            new_status: New status value
            
        Returns:
            Number of documents updated
            
        Raises:
            Exception: If bulk update fails
        """
        if not candidate_ids:
            return 0
        
        try:
            # Import here to avoid circular imports
            from common.entity.candidate_entity import ProcessingCandidate
            
            # Use Beanie's bulk update with proper operators
            # Convert UUIDs to PydanticObjectIds if needed
            object_ids = []
            for cid in candidate_ids:
                if cid is not None:
                    if isinstance(cid, UUID):
                        object_ids.append(PydanticObjectId(str(cid)))
                    else:
                        object_ids.append(cid)
            
            if not object_ids:
                return 0
            
            
            result = await ProcessingCandidate.find(
                In(ProcessingCandidate.id, object_ids)
            ).update({"status": new_status})
            
            updated_count = result.modified_count if result else 0
            logger.info(f"Bulk updated {updated_count} ProcessingCandidate statuses to '{new_status}'")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to bulk update ProcessingCandidate statuses: {e}")
            raise
    
    async def update_status_to_parsing(self, candidates: List[ProcessingCandidate]) -> int:
        """
        Update multiple ProcessingCandidate documents to 'parsing' status.
        
        Args:
            candidates: List of ProcessingCandidate instances
            
        Returns:
            Number of documents updated
            
        Raises:
            Exception: If bulk update fails
        """
        if not candidates:
            return 0
        
        candidate_ids = [candidate.id for candidate in candidates if candidate.id]
        # Convert to list of PydanticObjectIds
        object_ids = [PydanticObjectId(str(cid)) if isinstance(cid, UUID) else cid for cid in candidate_ids]
        return await self.update_status_bulk(object_ids, "parsing")
    
    async def find_by_status(self, status: str, limit: Optional[int] = None) -> List[ProcessingCandidate]:
        """
        Find ProcessingCandidate documents by status.
        
        Args:
            status: Status to filter by
            limit: Optional limit on number of results
            
        Returns:
            List of ProcessingCandidate documents
            
        Raises:
            Exception: If query fails
        """
        try:
            from common.entity.candidate_entity import ProcessingCandidate
            
            query = ProcessingCandidate.find(ProcessingCandidate.status == status)
            if limit:
                query = query.limit(limit)
            
            candidates = await query.to_list()
            logger.debug(f"Found {len(candidates)} ProcessingCandidate documents with status '{status}'")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to find ProcessingCandidate documents by status '{status}': {e}")
            raise
    
    async def find_by_file_id(self, file_id: UUID) -> Optional[ProcessingCandidate]:
        """
        Find ProcessingCandidate by file_id.
        
        Args:
            file_id: UUID of the file
            
        Returns:
            ProcessingCandidate if found, None otherwise
            
        Raises:
            Exception: If query fails
        """
        try:
            from common.entity.candidate_entity import ProcessingCandidate
            
            candidate = await ProcessingCandidate.find_one(ProcessingCandidate.file_id == file_id)
            if candidate:
                logger.debug(f"Found ProcessingCandidate for file_id: {file_id}")
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to find ProcessingCandidate by file_id '{file_id}': {e}")
            raise
    
    async def count_by_status(self, status: str) -> int:
        """
        Count ProcessingCandidate documents by status.
        
        Args:
            status: Status to count
            
        Returns:
            Number of documents with the specified status
            
        Raises:
            Exception: If count fails
        """
        try:
            from common.entity.candidate_entity import ProcessingCandidate
            
            count = await ProcessingCandidate.find(ProcessingCandidate.status == status).count()
            logger.debug(f"Found {count} ProcessingCandidate documents with status '{status}'")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count ProcessingCandidate documents by status '{status}': {e}")
            raise
    
    async def delete_by_status(self, status: str) -> int:
        """
        Delete ProcessingCandidate documents by status.
        
        Args:
            status: Status to filter for deletion
            
        Returns:
            Number of documents deleted
            
        Raises:
            Exception: If deletion fails
        """
        try:
            from common.entity.candidate_entity import ProcessingCandidate
            
            result = await ProcessingCandidate.find(ProcessingCandidate.status == status).delete()
            deleted_count = result.deleted_count if result else 0
            logger.info(f"Deleted {deleted_count} ProcessingCandidate documents with status '{status}'")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete ProcessingCandidate documents by status '{status}': {e}")
            raise
