"""
Embed results processor service - processes JSONL files containing embedding results.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId

from common.entity.candidate_entity import Embeddings, ProcessingCandidate
from common.service.process_batch_task_results_service.base_result_processor_service import (
    BaseResultProcessorService,
    ProcessingStats,
)

if TYPE_CHECKING:
    from common.repository.minio_repository import MinioRepository
    from common.repository.processing_candidate_repository import ProcessingCandidateRepository

logger = logging.getLogger(__name__)

# Embedding components that need to be processed
EMBEDDING_COMPONENTS = ["general", "skills", "work_experience"]


class EmbedResultsProcessorService(BaseResultProcessorService):
    """Service for processing embedding batch task results from MinIO JSONL files."""
    
    def __init__(self, 
                 minio_repository: MinioRepository,
                 processing_candidate_repository: ProcessingCandidateRepository):
        """Initialize with repositories."""
        super().__init__(minio_repository)
        self.processing_candidate_repository = processing_candidate_repository
    
    async def _process_single_result_file(self, file_path: str, bucket_name: str) -> ProcessingStats:
        """
        Process a single JSONL result file containing embedding results.
        
        Args:
            file_path: Path to the JSONL file in MinIO
            bucket_name: MinIO bucket name
            
        Returns:
            ProcessingStats for this file
        """
        stats = ProcessingStats()
        candidate_embeddings: Dict[str, Dict[str, List[float]]] = {}
        
        try:
            # Stream and process each line in the JSONL file
            for line in self._stream_jsonl_file(file_path, bucket_name):
                stats.total_lines_processed += 1
                
                processed_item = self._process_result_line(line)
                if processed_item:
                    candidate_id, component, embedding_vector = processed_item
                    
                    # Group embeddings by candidate_id
                    if candidate_id not in candidate_embeddings:
                        candidate_embeddings[candidate_id] = {}
                    
                    candidate_embeddings[candidate_id][component] = embedding_vector
                    stats.successful_updates += 1
                else:
                    stats.failed_updates += 1
            
            # Update documents with processed embeddings
            await self._update_documents_with_embeddings(candidate_embeddings)
            
            logger.info(f"Processed {stats.total_lines_processed} lines from {file_path}")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing result file {file_path}: {e}")
            raise
    
    async def _update_documents_with_embeddings(self, candidate_embeddings: Dict[str, Dict[str, List[float]]]) -> None:
        """
        Update ProcessingCandidate documents with embedding results.
        
        Args:
            candidate_embeddings: Dict of candidate embeddings grouped by candidate_id
            
        Returns:
            None
        """
        if not candidate_embeddings:
            return None
        
        try:
            # Group candidates by completion status
            completed_candidates = []
            partial_candidates = []
            
            for candidate_id, embeddings_dict in candidate_embeddings.items():
                # Check if all required components are present
                has_all_components = all(
                    component in embeddings_dict 
                    for component in EMBEDDING_COMPONENTS
                )
                
                if has_all_components:
                    completed_candidates.append((candidate_id, embeddings_dict))
                else:
                    partial_candidates.append((candidate_id, embeddings_dict))
            
            # Update completed candidates
            if completed_candidates:
                await self._update_completed_candidates(completed_candidates)
            
            # Update partial candidates (keep them in vectorizing status)
            if partial_candidates:
                await self._update_partial_candidates(partial_candidates)
            
            logger.info(
                f"Successfully updated {len(completed_candidates)} completed candidates "
                f"and {len(partial_candidates)} partial candidates"
            )
            return None
            
        except Exception as e:
            logger.error(f"Error updating documents with embeddings: {e}")
            return None
    
    async def _update_completed_candidates(self, completed_candidates: List[Tuple[str, Dict[str, List[float]]]]) -> None:
        """Update candidates with complete embeddings and move to pending_finalization status."""
        try:
            async with ProcessingCandidate.bulk_writer(ordered=False) as bw:
                for candidate_id, embeddings_dict in completed_candidates:
                    try:
                        object_id = PydanticObjectId(candidate_id)
                        
                        # Create Embeddings object
                        embeddings = Embeddings(
                            general=embeddings_dict.get("general"),
                            skills=embeddings_dict.get("skills"),
                            work_experience=embeddings_dict.get("work_experience")
                        )
                        
                        # Prepare the update document
                        update_doc = {
                            "$set": {
                                "embeddings": embeddings.model_dump(),
                                "status": "pending_finalization"
                            }
                        }
                        
                        # Perform the update
                        await ProcessingCandidate.find_one(
                            ProcessingCandidate.id == object_id
                        ).update(update_doc, bulk_writer=bw)
                        
                    except Exception as e:
                        logger.error(f"Failed to queue update for completed candidate {candidate_id}: {e}")
                        continue
            
            logger.info(f"Updated {len(completed_candidates)} candidates to pending_finalization status")
            
        except Exception as e:
            logger.error(f"Failed to update completed candidates: {e}")
            raise
    
    async def _update_partial_candidates(self, partial_candidates: List[Tuple[str, Dict[str, List[float]]]]) -> None:
        """Update candidates with partial embeddings but keep them in vectorizing status."""
        try:
            async with ProcessingCandidate.bulk_writer(ordered=False) as bw:
                for candidate_id, embeddings_dict in partial_candidates:
                    try:
                        object_id = PydanticObjectId(candidate_id)
                        
                        # Get current candidate to preserve existing embeddings
                        current_candidate = await ProcessingCandidate.find_one(
                            ProcessingCandidate.id == object_id
                        )
                        
                        if not current_candidate:
                            logger.error(f"Candidate {candidate_id} not found")
                            continue
                        
                        # Merge with existing embeddings if any
                        existing_embeddings = {}
                        if current_candidate.embeddings:
                            existing_embeddings = current_candidate.embeddings.model_dump()
                        
                        # Update with new embeddings
                        existing_embeddings.update(embeddings_dict)
                        
                        # Check if we now have all components
                        has_all_components = all(
                            component in existing_embeddings 
                            for component in EMBEDDING_COMPONENTS
                        )
                        
                        # Create Embeddings object (with partial data if needed)
                        embeddings = Embeddings(
                            general=existing_embeddings.get("general"),
                            skills=existing_embeddings.get("skills"),
                            work_experience=existing_embeddings.get("work_experience")
                        )
                        
                        if has_all_components:
                            # Move to pending_finalization when all components are complete
                            update_doc = {
                                "$set": {
                                    "embeddings": embeddings.model_dump(),
                                    "status": "pending_finalization"
                                }
                            }
                        else:
                            # Keep partial embeddings and stay in vectorizing status
                            update_doc = {
                                "$set": {
                                    "embeddings": embeddings.model_dump()
                                }
                            }
                        
                        # Perform the update
                        await ProcessingCandidate.find_one(
                            ProcessingCandidate.id == object_id
                        ).update(update_doc, bulk_writer=bw)
                        
                    except Exception as e:
                        logger.error(f"Failed to queue update for partial candidate {candidate_id}: {e}")
                        continue
            
            logger.info(f"Updated {len(partial_candidates)} candidates with partial embeddings")
            
        except Exception as e:
            logger.error(f"Failed to update partial candidates: {e}")
            raise
    
    def _process_result_line(self, line: str) -> Optional[Tuple[str, str, List[float]]]:
        """
        Process a single result line from the JSONL file.
        
        Args:
            line: JSON line string from the result file
            
        Returns:
            Tuple of (candidate_id, component, embedding_vector) or None if processing fails
        """
        try:
            # Parse the JSON line
            line_data = self._parse_result_line(line)
            if not line_data:
                return None
            
            # Extract candidate ID and component from custom_id
            # Format: "embed_{candidate_id}_{component}"
            custom_id: str = line_data.get('custom_id', "")
            if not custom_id or not custom_id.startswith('embed_'):
                logger.error(f"Invalid custom_id format: {custom_id}")
                return None
            
            # Parse custom_id to extract candidate_id and component
            parts = custom_id.split('_', 2)  # Split into ['embed', candidate_id, component]
            if len(parts) != 3:
                logger.error(f"Invalid custom_id format: {custom_id}")
                return None
            
            candidate_id = parts[1]
            component = parts[2]
            
            # Validate component
            if component not in EMBEDDING_COMPONENTS:
                logger.error(f"Unknown embedding component: {component}")
                return None
            
            # Extract the embedding vector from the response
            embedding_vector = self._extract_embedding_from_response(line_data['response'])
            if embedding_vector is None:
                logger.error(f"Failed to extract embedding for {custom_id}")
                return None

            return candidate_id, component, embedding_vector
            
        except Exception as e:
            logger.error(f"Error processing result line: {e}")
            return None
    
    def _extract_embedding_from_response(self, response: Dict[str, Any]) -> Optional[List[float]]:
        """
        Extract embedding vector from the batch API response.
        
        Args:
            response: Response object from the batch API
            
        Returns:
            Embedding vector as list of floats, or None if extraction fails
        """
        try:
            # Extract embedding data from response body
            response_body = response.get('body', {})
            data = response_body.get('data', [])
            
            if not data or not isinstance(data, list):
                logger.error("No data array found in response")
                return None
            
            # Get the first (and should be only) embedding
            embedding_data = data[0]
            embedding_vector = embedding_data.get('embedding')
            
            if not embedding_vector or not isinstance(embedding_vector, list):
                logger.error("No embedding vector found in response data")
                return None
            
            # Validate that all elements are numbers
            if not all(isinstance(x, (int, float)) for x in embedding_vector):
                logger.error("Embedding vector contains non-numeric values")
                return None
            
            return [float(x) for x in embedding_vector]
            
        except (KeyError, TypeError, IndexError) as e:
            logger.error(f"Error extracting embedding from response: {e}")
            return None
