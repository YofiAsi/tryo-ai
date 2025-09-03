"""
Test API for CreateCvParseBatchTaskService.

This FastAPI application provides REST endpoints to test the CV parse batch task service.
It can be run in Docker and tested with Postman.
"""

from typing import Any, Dict, List

from common.conf.dependencies import get_cv_parse_batch_task_service
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel, Field

# Initialize FastAPI app
app = FastAPI(
    title="CV Parse Batch Task Service Test API",
    description="Test API for CreateCvParseBatchTaskService - Create and manage CV parsing batch tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize the service
cv_parse_service = get_cv_parse_batch_task_service()

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


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "cv-parse-batch-task-test-api"}


@app.post("/create-tasks", response_model=CreateTasksResponse)
async def create_batch_tasks(
    minio_directory: str = Form(...),
    task_size: int = Form(..., ge=1, le=1000),
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
