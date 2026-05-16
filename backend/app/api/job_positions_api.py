import logging
from typing import Annotated, Optional
from beanie import PydanticObjectId

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Request,
    status,
    Query
)
from fastapi.responses import JSONResponse

from app.conf.app_settings import server_settings
from app.schema.paging import PagingDTO
from app.schema.job_position_dto import (
    JobPositionDTO, 
    CreateJobPositionDTO, 
    UpdateJobPositionDTO
)
from app.api.api_response import response_fail_status_codes
from app.service.job_position_service import JobPositionService
from app.conf.dependencies import get_job_position_service
from app.utils.header_utils import create_list_header
from app.entity.job_position_entity import JobStatus

_resource = "job-positions"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
                   responses=response_fail_status_codes
                   )


@router.get(
    path="/",
    operation_id="get_job_positions",
    name="get_job_positions",
    summary="Get Job Positions",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def get_job_positions(
        request: Request, 
        query: PagingDTO = Depends(PagingDTO),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_positions rest request")
    page_response = await job_position_service.find(None, query.page, query.size, "_id")
    _log.debug(f"JobPositionsApi get_job_positions rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/count",
    operation_id="count_job_positions",
    name="count_job_positions",
    summary="Count Job Positions",
    status_code=status.HTTP_200_OK
)
async def count_job_positions(
        request: Request,
        query: str = Query("{}", description="Query to filter job positions"),
        job_position_service: JobPositionService = Depends(get_job_position_service)):
    _log.debug(f"BEGIN:count_job_positions rest request")
    try:
        import json
        query_dict = {} if query == "{}" else json.loads(query)  # Convert string to dict safely
        count = await job_position_service.count(query_dict)
        _log.debug(f"JobPositionsApi count_job_positions rest response: {count}")
        return {"count": count}
    except json.JSONDecodeError as e:
        _log.error(f"Error parsing query JSON: {e}")
        return JSONResponse(
            content={"detail": "Invalid JSON query format"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        _log.error(f"Error counting job positions: {e}")
        return JSONResponse(
            content={"detail": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    path="/search",
    operation_id="search_job_positions",
    name="search_job_positions",
    summary="Search Job Positions by Text",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def search_job_positions(
        request: Request,
        q: str = Query(..., description="Search text to find in job positions"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:search_job_positions rest request with query: {q}")
    page_response = await job_position_service.search_by_text(q, page, size)
    _log.debug(f"JobPositionsApi search_job_positions rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/by-status/{status}",
    operation_id="get_job_positions_by_status",
    name="get_job_positions_by_status",
    summary="Get Job Positions by Status",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def get_job_positions_by_status(
        request: Request,
        status: JobStatus,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_positions_by_status rest request for status: {status}")
    page_response = await job_position_service.find_by_status(status.value, page, size)
    _log.debug(f"JobPositionsApi get_job_positions_by_status rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/by-employment-type/{employment_type}",
    operation_id="get_job_positions_by_employment_type",
    name="get_job_positions_by_employment_type",
    summary="Get Job Positions by Employment Type",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def get_job_positions_by_employment_type(
        request: Request,
        employment_type: str,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_positions_by_employment_type rest request for employment type: {employment_type}")
    page_response = await job_position_service.find_by_employment_type(employment_type, page, size)
    _log.debug(f"JobPositionsApi get_job_positions_by_employment_type rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/by-seniority-level/{seniority_level}",
    operation_id="get_job_positions_by_seniority_level",
    name="get_job_positions_by_seniority_level",
    summary="Get Job Positions by Seniority Level",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def get_job_positions_by_seniority_level(
        request: Request,
        seniority_level: str,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_positions_by_seniority_level rest request for seniority level: {seniority_level}")
    page_response = await job_position_service.find_by_seniority_level(seniority_level, page, size)
    _log.debug(f"JobPositionsApi get_job_positions_by_seniority_level rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/by-location",
    operation_id="get_job_positions_by_location",
    name="get_job_positions_by_location",
    summary="Get Job Positions by Location",
    response_model=list[JobPositionDTO],
    status_code=status.HTTP_200_OK
)
async def get_job_positions_by_location(
        request: Request,
        city: Optional[str] = Query(None, description="City name"),
        country: Optional[str] = Query(None, description="Country name"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_positions_by_location rest request for city: {city}, country: {country}")
    page_response = await job_position_service.find_by_location(city, country, page, size)
    _log.debug(f"JobPositionsApi get_job_positions_by_location rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [job_position.to_json() for job_position in page_response.content]
    return JSONResponse(content=json_result, headers=headers)



@router.get(
    path="/{job_position_id}",
    operation_id="get_job_position",
    name="get_job_position",
    summary="Get Job Position by ID",
    response_model=JobPositionDTO,
    status_code=status.HTTP_200_OK
)
async def get_job_position(
        request: Request,
        job_position_id: PydanticObjectId,
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_job_position rest request for job position: {job_position_id}")
    job_position = await job_position_service.retrieve(str(job_position_id))
    if not job_position:
        return JSONResponse(
            content={"detail": f"Job position not found: {job_position_id}"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    _log.debug(f"JobPositionsApi get_job_position rest response: {job_position}")
    return JSONResponse(content=job_position.to_json())


@router.post(
    path="/",
    operation_id="create_job_position",
    name="create_job_position",
    summary="Create Job Position",
    response_model=JobPositionDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_job_position(
        request: Request,
        job_position_data: CreateJobPositionDTO = Body(...),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:create_job_position rest request")
    created_job_position = await job_position_service.create(job_position_data=job_position_data)
    _log.debug(f"JobPositionsApi create_job_position rest response: {created_job_position}")
    
    return JSONResponse(
        content=created_job_position.to_json(),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    path="/{job_position_id}",
    operation_id="update_job_position",
    name="update_job_position",
    summary="Update Job Position",
    response_model=JobPositionDTO,
    status_code=status.HTTP_200_OK
)
async def update_job_position(
        request: Request,
        job_position_id: PydanticObjectId,
        job_position_data: UpdateJobPositionDTO = Body(...),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:update_job_position rest request for job position: {job_position_id}")
    updated_job_position = await job_position_service.update(str(job_position_id), job_position_data)
    _log.debug(f"JobPositionsApi update_job_position rest response: {updated_job_position}")
    
    return JSONResponse(content=updated_job_position.to_json())


@router.delete(
    path="/{job_position_id}",
    operation_id="delete_job_position",
    name="delete_job_position",
    summary="Delete Job Position",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_job_position(
        request: Request,
        job_position_id: PydanticObjectId,
        job_position_service: JobPositionService = Depends(get_job_position_service)):
    _log.debug(f"BEGIN:delete_job_position rest request for job position: {job_position_id}")
    await job_position_service.delete(str(job_position_id))
    _log.debug(f"JobPositionsApi delete_job_position rest response: deleted")
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    path="/{job_position_id}/status",
    operation_id="change_job_position_status",
    name="change_job_position_status",
    summary="Change Job Position Status",
    response_model=JobPositionDTO,
    status_code=status.HTTP_200_OK
)
async def change_job_position_status(
        request: Request,
        job_position_id: PydanticObjectId,
        new_status: JobStatus = Body(..., embed=True),
        job_position_service: JobPositionService = Depends(get_job_position_service)) -> JSONResponse:
    _log.debug(f"BEGIN:change_job_position_status rest request for job position: {job_position_id} to {new_status}")
    updated_job_position = await job_position_service.change_status(str(job_position_id), new_status)
    _log.debug(f"JobPositionsApi change_job_position_status rest response: {updated_job_position}")
    
    return JSONResponse(content=updated_job_position.to_json())

