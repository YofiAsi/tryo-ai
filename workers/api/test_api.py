"""
Test API for CreateCvParseBatchTaskService.

This module provides REST endpoints to test the CV parse batch task service.
It can be run in Docker and tested with Postman.
"""

import logging
from typing import Any, Dict, List

from common.conf.dependencies import (
    get_candidate_finalization_service,
    get_cv_parse_batch_task_service,
    get_cv_parse_results_processor_service,
    get_embed_results_processor_service,
    get_embed_task_service,
)
from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Initialize the services
cv_parse_service = get_cv_parse_batch_task_service()
cv_parse_results_service = get_cv_parse_results_processor_service()
embed_task_service = get_embed_task_service()
embed_results_service = get_embed_results_processor_service()
candidate_finalization_service = get_candidate_finalization_service()

# Global storage for test data (in production, use proper database)
test_data_storage: Dict[str, Any] = {
    "data_directories": {},
    "databases": {}
}


class CreateTasksRequest(BaseModel):
    """Request model for creating batch tasks."""
    task_size: int = Field(..., description="Maximum number of tasks per JSONL file", ge=1, le=1000)


class CreateTasksResponse(BaseModel):
    """Response model for created batch tasks."""
    success: bool
    message: str
    batch_task_ids: List[str]


class UploadResponse(BaseModel):
    """Response model for file uploads."""
    success: bool
    message: str
    minio_directory: str
    uploaded_files: List[str]
    total_files: int


class DatabaseInfo(BaseModel):
    """Database information model."""
    database_id: str
    file_count: int
    relevant_files: int
    year_range: Dict[str, int]
    length_range: Dict[str, int]


class ProcessResultsRequest(BaseModel):
    """Request model for processing batch results."""
    minio_directory: str = Field(..., description="Directory path in MinIO containing result files")
    bucket_name: str = Field(..., description="MinIO bucket name containing the result files")


class ProcessResultsResponse(BaseModel):
    """Response model for processed batch results."""
    success: bool
    message: str
    total_lines_processed: int
    successful_updates: int
    failed_updates: int


class FinalizationResponse(BaseModel):
    """Response model for candidate finalization."""
    success: bool
    message: str
    total_processed: int
    successful_finalizations: int
    failed_finalizations: int


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "cv-parse-batch-task-test-api"}


@router.post("/create-tasks", response_model=CreateTasksResponse)
async def create_batch_tasks(
    minio_directory: str = Form(...),
    task_size: int = Form(..., ge=1),
) -> CreateTasksResponse:
    """
    Create batch tasks from uploaded CV files.
    
    This endpoint uses the CreateCvParseBatchTaskService to generate JSONL files
    and send them to the batch manager for processing.
    """
    
    try:
        # Create batch tasks using the service (now async)
        batch_task_ids = await cv_parse_service.create_tasks(
            task_size=task_size,
            minio_directory=minio_directory,
        )
        
        return CreateTasksResponse(
            success=True,
            message=f"Successfully created {len(batch_task_ids)} batch tasks",
            batch_task_ids=batch_task_ids,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")


@router.post("/process-results", response_model=ProcessResultsResponse)
async def process_batch_results(
    minio_directory: str = Form(...),
    bucket_name: str = Form(...),
) -> ProcessResultsResponse:
    """
    Process batch task results from MinIO JSONL files.
    
    This endpoint uses the CvParseResultsProcessorService to process JSONL result files
    and update ProcessingCandidate documents with parsed data.
    """
    
    try:
        # Process batch results using the service
        stats = await cv_parse_results_service.process_results(
            minio_directory=minio_directory,
            bucket_name=bucket_name
        )
        
        return ProcessResultsResponse(
            success=True,
            message=f"Successfully processed {stats.total_lines_processed} result lines",
            total_lines_processed=stats.total_lines_processed,
            successful_updates=stats.successful_updates,
            failed_updates=stats.failed_updates,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Results processing failed: {str(e)}")


@router.post("/create-embed-tasks", response_model=CreateTasksResponse)
async def create_embed_tasks(
    task_size: int = Form(..., ge=1, le=50000),
) -> CreateTasksResponse:
    """
    Create embedding batch tasks from candidates ready for vectorization.
    
    This endpoint uses the CreateEmbedTaskService to generate JSONL files
    for embedding tasks and send them to the batch manager for processing.
    """
    
    try:
        # Create embedding batch tasks using the service
        batch_task_ids = await embed_task_service.create_tasks(
            task_size=task_size,
        )
        
        return CreateTasksResponse(
            success=True,
            message=f"Successfully created {len(batch_task_ids)} embedding batch tasks",
            batch_task_ids=batch_task_ids,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding task creation failed: {str(e)}")


@router.post("/process-embed-results", response_model=ProcessResultsResponse)
async def process_embed_results(
    minio_directory: str = Form(...),
    bucket_name: str = Form(...),
) -> ProcessResultsResponse:
    """
    Process embedding batch task results from MinIO JSONL files.
    
    This endpoint uses the EmbedResultsProcessorService to process JSONL result files
    and update ProcessingCandidate documents with embedding vectors.
    """
    
    try:
        # Process embedding batch results using the service
        stats = await embed_results_service.process_results(
            minio_directory=minio_directory,
            bucket_name=bucket_name
        )
        
        return ProcessResultsResponse(
            success=True,
            message=f"Successfully processed {stats.total_lines_processed} embedding result lines",
            total_lines_processed=stats.total_lines_processed,
            successful_updates=stats.successful_updates,
            failed_updates=stats.failed_updates,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding results processing failed: {str(e)}")


@router.post("/finalize-candidates", response_model=FinalizationResponse)
async def finalize_candidates() -> FinalizationResponse:
    """
    Finalize candidates that are ready for finalization.
    
    This endpoint uses the CandidateFinalizationService to process candidates
    with 'pending_finalization' status, create CandidateDocument instances,
    and update ProcessingCandidate statuses to 'completed'.
    """
    
    try:
        # Finalize candidates using the service
        stats = await candidate_finalization_service.finalize_candidates()
        
        return FinalizationResponse(
            success=True,
            message=f"Successfully finalized {stats.successful_finalizations} candidates",
            total_processed=stats.total_processed,
            successful_finalizations=stats.successful_finalizations,
            failed_finalizations=stats.failed_finalizations,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate finalization failed: {str(e)}")


