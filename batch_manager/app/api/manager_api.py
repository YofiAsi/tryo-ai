from __future__ import annotations
import logging
from typing import TYPE_CHECKING
import json
from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from app.schema.batch_task_dto import CreateBatchTaskDTO, BatchTaskDTO
from app.conf.dependencies import get_batch_task_create_service, get_batch_task_service
from app.entity.batch_task_entity import BatchTaskType, BatchTask


from app.service.batch_task_create_service import BatchTaskCreateService
from app.service.batch_task_service import BatchTaskService

_resource = "manager"
_path = f"/api/v1/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path, tags=[_resource])


@router.post(
    path="/create",
    operation_id="create_batch_task",
    name="create_batch_task",
    summary="Create a new batch task",
    description="Creates a new batch task for processing requests through OpenAI Batch API",
    response_model=BatchTaskDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_batch_task(
    dto_json: str = Form(...),
    file: UploadFile = File(...),
    batch_task_create_service: BatchTaskCreateService = Depends(get_batch_task_create_service),
) -> JSONResponse:
    """
    Create a new batch task for OpenAI batch processing.

    This endpoint creates a batch task that can manage multiple OpenAI batches
    for processing requests through the OpenAI Batch API.
    """
    create_batch_task_dto = CreateBatchTaskDTO(**json.loads(dto_json))

    _log.info(f"Creating batch task with type: {create_batch_task_dto.type}")

    try:
        # Validate file format
        if not file.filename:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "File is required"})

        if not file.filename.endswith(".jsonl"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"error": "File must be in JSONL format"}
            )

        # Create batch task using the service
        batch_task: BatchTask = await batch_task_create_service.create_task(
            batch_task_type=BatchTaskType(create_batch_task_dto.type),
            file=file.file,
            metadata=create_batch_task_dto.metadata,
        )

        result = BatchTaskDTO.from_entity(batch_task)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result.model_dump(mode="json"))

    except Exception as e:
        _log.error(f"Error creating batch task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to create batch task: {str(e)}"},
        )


@router.get(
    path="/{task_id}",
    operation_id="get_batch_task",
    name="get_batch_task",
    summary="Get batch task by ID",
    description="Retrieve a batch task by its ID",
    response_model=BatchTaskDTO,
    status_code=status.HTTP_200_OK,
)
async def get_batch_task(
    task_id: str,
    batch_task_service: BatchTaskService = Depends(get_batch_task_service),
) -> JSONResponse:
    """Get a batch task by its ID."""
    try:
        batch_task = await batch_task_service.get_task_info(PydanticObjectId(task_id))

        if not batch_task:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Batch task not found"})

        result = BatchTaskDTO.from_entity(batch_task)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.model_dump(mode="json"))

    except ValueError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid task ID format"})
    except Exception as e:
        _log.error(f"Error retrieving batch task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to retrieve batch task: {str(e)}"},
        )
