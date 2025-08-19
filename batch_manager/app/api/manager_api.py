import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
    UploadFile,
    File
)
from fastapi.responses import JSONResponse

from app.schema.task_dto import CreateTaskDTO, CreateTaskResponseDTO
from app.service.task_create_service import TaskCreateService
from app.conf.dependencies import get_task_create_service

_resource = "manager"
_path = f"/api/v1/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path, tags=[_resource])


@router.post(
    path="/",
    operation_id="create_task",
    name="create_task",
    summary="Create a new task",
    description="Creates a new task for processing requests through OpenAI Batch API",
    response_model=CreateTaskResponseDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    request: Request,
    create_task_dto: CreateTaskDTO,
    file: UploadFile = File(...),
    task_create_service: TaskCreateService = Depends(get_task_create_service)
) -> JSONResponse:
    """
    Create a new task for OpenAI batch processing.
    
    This endpoint creates one or more tasks based on the multitask configuration.
    If multitask is True, creates multiple tasks each with a single batch.
    If multitask is False, creates a single task with multiple batches.
    """
    _log.info(f"Creating task with type: {create_task_dto.type}, multitask: {create_task_dto.multitask}")
    
    try:
        # Validate file format
        if not file.filename.endswith('.jsonl'):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "File must be in JSONL format"}
            )
        
        # Create tasks using the service
        result = await task_create_service.create_tasks(create_task_dto, file)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result.dict()
        )
        
    except Exception as e:
        _log.error(f"Error creating task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to create task: {str(e)}"}
        )