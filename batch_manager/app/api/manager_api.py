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

from app.schema.batch_task_dto import CreateBatchTaskDTO, BatchTaskDTO
from app.service.batch_task_create_service import BatchTaskCreateService
from app.conf.dependencies import get_batch_task_create_service
from app.entity.batch_task_entity import BatchTaskType, BatchTask

_resource = "manager"
_path = f"/api/v1/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path, tags=[_resource])


@router.post(
    path="/",
    operation_id="create_batch_task",
    name="create_batch_task",
    summary="Create a new batch task",
    description="Creates a new batch task for processing requests through OpenAI Batch API",
    response_model=BatchTaskDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_batch_task(
    request: Request,
    create_batch_task_dto: CreateBatchTaskDTO,
    file: UploadFile = File(...),
    batch_task_create_service: BatchTaskCreateService = Depends(get_batch_task_create_service)
) -> JSONResponse:
    """
    Create a new batch task for OpenAI batch processing.
    
    This endpoint creates a batch task that can manage multiple OpenAI batches
    for processing requests through the OpenAI Batch API.
    """
    _log.info(f"Creating batch task with type: {create_batch_task_dto.type}")
    
    try:
        # Validate file format
        if not file.filename.endswith('.jsonl'):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "File must be in JSONL format"}
            )
        
        # Create batch task using the service
        batch_task: BatchTask = await batch_task_create_service.create_task(
            batch_task_type=BatchTaskType(create_batch_task_dto.type),
            file=file.file,
            metadata=create_batch_task_dto.metadata,
        )

        result = BatchTaskDTO.from_entity(batch_task)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result
        )
        
    except Exception as e:
        _log.error(f"Error creating batch task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to create batch task: {str(e)}"}
        )