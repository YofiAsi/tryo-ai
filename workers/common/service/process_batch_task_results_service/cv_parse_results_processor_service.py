"""
CV parse results processor service - processes JSONL files containing CV parsing results.
"""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from common.entity.candidate_entity import ParsedCandidate
from common.repository.processing_candidate_repository import ParsedDataUpdate
from common.service.process_batch_task_results_service.base_result_processor_service import (
    BaseResultProcessorService,
    ProcessingStats,
)

if TYPE_CHECKING:
    from common.repository.minio_repository import MinioRepository
    from common.repository.processing_candidate_repository import ProcessingCandidateRepository

logger = logging.getLogger(__name__)


class CvParseResultsProcessorService(BaseResultProcessorService):
    """Service for processing CV parse batch task results from MinIO JSONL files."""
    
    def __init__(self, 
                 minio_repository: MinioRepository,
                 processing_candidate_repository: ProcessingCandidateRepository):
        """Initialize with repositories."""
        super().__init__(minio_repository)
        self.processing_candidate_repository = processing_candidate_repository
    
    async def _process_single_result_file(self, file_path: str, bucket_name: str) -> ProcessingStats:
        """
        Process a single JSONL result file containing CV parse results.
        
        Args:
            file_path: Path to the JSONL file in MinIO
            bucket_name: MinIO bucket name
            
        Returns:
            ProcessingStats for this file
        """
        stats = ProcessingStats()
        processed_items: Dict[str, ParsedDataUpdate] = {}
        
        try:
            # Stream and process each line in the JSONL file
            for line in self._stream_jsonl_file(file_path, bucket_name):
                stats.total_lines_processed += 1
                
                processed_item = self._process_result_line(line)
                if processed_item:
                    processed_items[processed_item[0]] = processed_item[1]
                    stats.successful_updates += 1
                else:
                    stats.failed_updates += 1
            
            # Bulk update documents with processed results
            await self._update_documents_with_results(processed_items)
            
            logger.info(f"Processed {stats.total_lines_processed} lines from {file_path}")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing result file {file_path}: {e}")
            raise
    
    async def _update_documents_with_results(self, processed_items: Dict[str, ParsedDataUpdate]) -> None:
        """
        Update ProcessingCandidate documents with parsed results.
        
        Args:
            processed_items: Dict of processed result items
            
        Returns:
            None
        """
        if not processed_items:
            return None
        
        try:
            await self.processing_candidate_repository.add_parsed_data_to_candidates(
                processed_items
            )
            
            logger.info(f"Successfully updated {len(processed_items)} ProcessingCandidate documents")
            return None
            
        except Exception as e:
            logger.error(f"Error updating documents with results: {e}")
            return None
    
    def _process_result_line(self, line: str) -> Optional[Tuple[str, ParsedDataUpdate]]:
        """
        Process a single result line from the JSONL file.
        
        Args:
            line: JSON line string from the result file
            
        Returns:
            Processed item dict with candidate_id and parsed_data_update, or None if processing fails
        """
        try:
            # Parse the JSON line
            line_data = self._parse_result_line(line)
            if not line_data:
                return None
            
            # Extract candidate ID from custom_id
            candidate_id: str = line_data.get('custom_id', "")
            if not candidate_id:
                return None
            
            # Extract the parsed data from the response
            parsed_data: Optional[ParsedCandidate] = self._extract_parsed_data_from_response(line_data['response'])
            if parsed_data is None:
                data_update = ParsedDataUpdate(parsed_data=None, status="failed", errors=["JSON parsing failed"])
            else:
                data_update = ParsedDataUpdate(parsed_data=parsed_data, status="pending_vectorization")

            return candidate_id, data_update
            
        except Exception as e:
            logger.error(f"Error processing result line: {e}")
            return None
    
    def _extract_parsed_data_from_response(self, response: Dict[str, Any]) -> Optional[ParsedCandidate]:
        """
        Extract parsed CV data from the batch API response.
        
        Args:
            response: Response object from the batch API
            
        Returns:
            Parsed CV data as dict, or None if extraction fails
        """
        try:
            # Based on old processor logic: extract message output from response body
            output_items = response['body']['output']
            message_output = self._extract_message_output(output_items)
            
            if not message_output:
                logger.error("No message output found in response")
                return None
            
            # Extract the content text
            content = message_output['content'][0]['text']
            
            # Parse the JSON content (which should be structured ParsedCandidate data)
            parsed_data = self._robust_json_parse(content)
            
            if parsed_data is None:
                logger.error("Failed to parse JSON content from response")
                return None
            
            # Validate the parsed data matches ParsedCandidate structure
            try:
                return ParsedCandidate(**parsed_data)
            except Exception as e:
                logger.error(f"Parsed data doesn't match ParsedCandidate schema: {e}")
                return None
            
        except (KeyError, TypeError, IndexError) as e:
            logger.error(f"Error extracting parsed data from response: {e}")
            return None
    
    def _extract_message_output(self, output_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract message output from response output items.
        
        Args:
            output_items: List of output items from the response
            
        Returns:
            Message output dict or None if not found
        """
        for item in output_items:
            if item.get('type') == 'message':
                return item
        return None
    
    def _robust_json_parse(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Robust JSON parsing with fallback strategies.
        
        Args:
            content: JSON content string
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Strategy 1: Direct parsing
        try:
            return json.loads(content)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Clean markdown formatting and parse
        try:
            cleaned_content = self._clean_json_content(content)
            return json.loads(cleaned_content)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            pass
        
        logger.error(f"Failed to parse JSON content: {content[:200]}...")
        return None
    
    def _clean_json_content(self, content: str) -> str:
        """
        Clean JSON content by removing markdown formatting.
        
        Args:
            content: Raw JSON content string
            
        Returns:
            Cleaned JSON content string
        """
        cleaned = content.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        # Remove problematic characters
        cleaned = cleaned.replace('\r', '').replace('\t', '')
        
        return cleaned.strip()
