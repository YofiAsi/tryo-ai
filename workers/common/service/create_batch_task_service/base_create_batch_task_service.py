"""
Base class for task processors.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterator, List, Type

from common.utils.json_schema_tools import get_strict_json_schema

if TYPE_CHECKING:
    from pydantic import BaseModel

logger = logging.getLogger(__name__)



class BaseCreateBatchTaskService(ABC):
    """Base class for batch task processors that handle both creation and processing."""
    
    @property
    @abstractmethod
    def endpoint(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass
    
    @abstractmethod
    async def create_tasks(self, task_size: int, **kwargs: Any) -> List[str]:
        """
        Create batch tasks from input data.
        
        Args:
            task_size: Maximum number of tasks per JSONL file
            **kwargs: Additional arguments specific to the implementation
            
        Returns:
            List of paths to created JSONL files
        """
        pass
    
    def _create_batches_from_iterator(self, data_iterator: Iterator[Dict[str, Any]], 
                                     batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Create batches from data iterator in a memory-efficient way.
        
        Args:
            data_iterator: Iterator of data items
            batch_size: Maximum number of items per batch
            
        Yields:
            Lists of batch items
        """
        batch = []
        for item in data_iterator:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        # Yield remaining items
        if batch:
            yield batch
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary JSONL files.
        
        Args:
            file_paths: List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file {file_path}: {e}") 
    
    def convert_model_to_json_schema(self, model: Type[BaseModel]) -> dict[str, Any]:
        return {
            "format": {
                "type": "json_schema",
                "name": model.__name__,
                "schema": get_strict_json_schema(model),
                "strict": True,
            }
        }