"""
Repository for ProcessingCandidate operations with bulk update capabilities.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Sequence

from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In

from common.entity.candidate_entity import ParsedCandidate, ProcessingCandidate

if TYPE_CHECKING:
    from uuid import UUID


logger = logging.getLogger(__name__)

@dataclass
class ParsedDataUpdate:
    status: Optional[str] = None
    parsed_data: Optional[ParsedCandidate] = None
    errors: List[str] = field(default_factory=list)

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
    
    async def update_status_bulk(self, candidate_ids: Sequence[PydanticObjectId], new_status: str) -> int:
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
        try:
            if not candidate_ids:
                logger.warning("No candidate IDs provided for bulk update")
                return 0
            
            
            await ProcessingCandidate.find(
                In(ProcessingCandidate.id, candidate_ids)
            ).update_many({"$set": {"status": new_status}})
            
            logger.info(f"Bulk updated {len(candidate_ids)} ProcessingCandidate statuses to '{new_status}'")
            return len(candidate_ids)
            
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
        return await self.update_status_bulk(candidate_ids, "parsing")
    
    async def update_batch_task_id_and_status(self, candidates: List[ProcessingCandidate], batch_task_id: str, status: str = "parsing") -> int:
        """
        Update multiple ProcessingCandidate documents with batch_task_id and status.
        
        Args:
            candidates: List of ProcessingCandidate instances
            batch_task_id: The batch task ID to assign
            status: The status to set (defaults to 'parsing')
            
        Returns:
            Number of documents updated
            
        Raises:
            Exception: If bulk update fails
        """
        try:
            if not candidates:
                logger.warning("No candidates provided for batch update")
                return 0
            
            candidate_ids = [candidate.id for candidate in candidates if candidate.id]
            if not candidate_ids:
                logger.warning("No candidate IDs found for batch update")
                return 0
            
            # Update both status and batch_task_id
            from beanie.odm.operators.find.comparison import In
            
            await ProcessingCandidate.find(
                In(ProcessingCandidate.id, candidate_ids)
            ).update_many({
                "$set": {
                    "status": status,
                    "parse_batch_task_id": batch_task_id
                }
            })
            
            logger.info(f"Updated {len(candidate_ids)} candidates with batch_task_id: {batch_task_id} and status: {status}")
            return len(candidate_ids)
            
        except Exception as e:
            logger.error(f"Error updating candidates with batch_task_id and status: {e}")
            raise
    

    async def cleanup_corrupted_errors_field(self) -> int:
        """
        Clean up documents that have aggregation expressions in their errors field.
        This fixes documents that were corrupted by incorrect bulk update operations.
        
        Returns:
            Number of documents cleaned up
        """
        try:
            # Find documents with corrupted errors field (containing aggregation expressions)
            corrupted_docs = await ProcessingCandidate.find(
                {"errors": {"$type": "object"}}  # errors field is an object instead of array
            ).to_list()
            
            cleaned_count = 0
            for doc in corrupted_docs:
                # Reset errors to empty array if it's corrupted
                if isinstance(doc.errors, dict):
                    doc.errors = []
                    await doc.save()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up corrupted errors field for document {doc.id}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} documents with corrupted errors field")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup corrupted errors field: {e}")
            raise

    async def find_by_status_iterator(self, status: str) -> AsyncIterator[ProcessingCandidate]:
        """
        Find ProcessingCandidate documents by status using an iterator.
        
        Args:
            status: Status to filter by
            
        Yields:
            ProcessingCandidate documents one at a time
            
        Raises:
            Exception: If query fails
        """
        try:
            # First, clean up any corrupted documents
            await self.cleanup_corrupted_errors_field()
            
            query = ProcessingCandidate.find(ProcessingCandidate.status == status)
            
            # Process in batches to avoid loading all documents into memory
            async for candidate in query:
                yield candidate
                
        except Exception as e:
            logger.error(f"Failed to iterate ProcessingCandidate documents by status '{status}': {e}")
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
            result = await ProcessingCandidate.find(ProcessingCandidate.status == status).delete()
            deleted_count = result.deleted_count if result else 0
            logger.info(f"Deleted {deleted_count} ProcessingCandidate documents with status '{status}'")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete ProcessingCandidate documents by status '{status}': {e}")
            raise

    async def bulk_update(self, candidates: List[ProcessingCandidate]) -> List[ProcessingCandidate]:
        """
        Bulk update ProcessingCandidate documents.
        
        Args:
            candidates: List of ProcessingCandidate instances
            
        Returns:
            List of updated ProcessingCandidate instances

        Raises:
            Exception: If bulk update fails
        """
        if not candidates:
            return []
        
        try:
            await ProcessingCandidate.replace_many(candidates)
            return candidates
        except Exception as e:
            logger.error(f"Failed to bulk update ProcessingCandidate documents: {e}")
            raise
    
    async def add_parsed_data_to_candidates(self, data: Dict[str, ParsedDataUpdate]) -> None:
        """
        Add parsed data to ProcessingCandidate documents.
        
        Args:
            data: Dictionary mapping candidate IDs to ParsedDataUpdate instances
            
        Returns:
            None
            
        Raises:
            Exception: If bulk update fails
        """
        if not data:
            logger.warning("No data provided for bulk update")
            return None

        try:
            updated_count = 0
            failed_updates = []
            
            async with ProcessingCandidate.bulk_writer(ordered=False) as bw:
                for _id, parsed_data_update in data.items():
                    try:
                        object_id = PydanticObjectId(_id)

                        # Prepare the update document
                        update_doc: Dict[str, Dict[str, Any]] = {
                            "$set": {
                                "parsed_data": parsed_data_update.parsed_data.model_dump() if parsed_data_update.parsed_data else None,
                                "status": parsed_data_update.status,
                            }
                        }
                        
                        # Only add errors concatenation if there are errors to add
                        if parsed_data_update.errors:
                            # First get the current document to append errors
                            current_doc = await ProcessingCandidate.find_one(ProcessingCandidate.id == object_id)
                            current_errors: List[str] = current_doc.errors if current_doc and current_doc.errors else []
                            update_doc["$set"]["errors"] = current_errors + parsed_data_update.errors
                        
                        # Perform the update
                        await ProcessingCandidate.find_one(
                            ProcessingCandidate.id == object_id
                        ).update(update_doc, bulk_writer=bw)
                            
                    except Exception as e:
                        logger.error(f"Failed to queue update for candidate {_id}: {e}")
                        failed_updates.append(_id)
                        continue
            
            # Log results
            logger.info(f"Bulk update completed: {updated_count} candidates queued for update")
            if failed_updates:
                logger.warning(f"Failed to update {len(failed_updates)} candidates: {failed_updates}")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to perform bulk update of parsed data: {e}")
            raise