"""
Base class for batch task result processors.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

if TYPE_CHECKING:
    from common.repository.minio_repository import MinioRepository

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for result processing."""
    total_lines_processed: int = 0
    successful_updates: int = 0
    failed_updates: int = 0


class BaseResultProcessorService(ABC):
    """Base class for processing batch task results from MinIO JSONL files."""
    
    def __init__(self, minio_repository: MinioRepository):
        """Initialize with MinIO repository."""
        self.minio_repository = minio_repository
    
    async def process_results(self, minio_directory: str, bucket_name: str) -> ProcessingStats:
        """
        Process all JSONL result files in the specified MinIO directory.
        
        Args:
            minio_directory: Directory path in MinIO containing result files
            bucket_name: MinIO bucket name
            
        Returns:
            ProcessingStats with processing statistics
        """
        logger.info(f"Processing batch task results from {bucket_name}/{minio_directory}")
        
        stats = ProcessingStats()
        result_files = self._get_result_files(minio_directory, bucket_name)
        
        for file_path in result_files:
            logger.info(f"Processing result file: {file_path}")
            file_stats = await self._process_single_result_file(file_path, bucket_name)
            self._merge_stats(stats, file_stats)
        
        logger.info(f"Processing complete. Stats: {stats}")
        return stats
    
    @abstractmethod
    async def _process_single_result_file(self, file_path: str, bucket_name: str) -> ProcessingStats:
        """
        Process a single JSONL result file.
        
        Args:
            file_path: Path to the JSONL file in MinIO
            bucket_name: MinIO bucket name
            
        Returns:
            ProcessingStats for this file
        """
        pass
    
    def _get_result_files(self, minio_directory: str, bucket_name: str) -> List[str]:
        """Get list of JSONL result files in the directory."""
        try:
            files = self.minio_repository.list_files_in_directory(minio_directory, bucket_name)
            jsonl_files = [f for f in files if f.endswith('.jsonl')]
            
            if not jsonl_files:
                logger.warning(f"No JSONL files found in {bucket_name}/{minio_directory}")
            else:
                logger.info(f"Found {len(jsonl_files)} JSONL files to process")
            
            return jsonl_files
        except Exception as e:
            logger.error(f"Error listing files in {bucket_name}/{minio_directory}: {e}")
            return []
    
    def _stream_jsonl_file(self, file_path: str, bucket_name: str) -> Iterator[str]:
        """
        Stream lines from a JSONL file in MinIO.
        
        Args:
            file_path: Path to the JSONL file in MinIO
            bucket_name: MinIO bucket name
            
        Yields:
            Individual lines from the JSONL file
        """
        try:
            stream = self.minio_repository.stream_file(file_path, bucket_name)
            
            for line in stream:
                line_str = line.decode('utf-8').strip()
                if line_str:
                    yield line_str
                    
        except Exception as e:
            logger.error(f"Error streaming file {bucket_name}/{file_path}: {e}")
            raise
    
    def _parse_result_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single line from JSONL result file.
        
        Args:
            line: JSON line string
            
        Returns:
            Parsed result data or None if parsing fails
        """
        try:
            line_data = json.loads(line)
            
            # Validate required fields based on old processor logic
            if not all(k in line_data for k in ['response', 'custom_id']):
                logger.error("Missing required fields in result line")
                return None
            
            return line_data  # type: ignore[no-any-return]
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON line: {e}")
            return None
    
    def _merge_stats(self, total_stats: ProcessingStats, file_stats: ProcessingStats) -> None:
        """Merge file statistics into total statistics."""
        total_stats.total_lines_processed += file_stats.total_lines_processed
        total_stats.successful_updates += file_stats.successful_updates
        total_stats.failed_updates += file_stats.failed_updates
