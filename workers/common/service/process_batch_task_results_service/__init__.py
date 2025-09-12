"""
Process batch task results service module.
"""

from .base_result_processor_service import BaseResultProcessorService, ProcessingStats
from .cv_parse_results_processor_service import CvParseResultsProcessorService

__all__ = ["BaseResultProcessorService", "ProcessingStats", "CvParseResultsProcessorService"]
