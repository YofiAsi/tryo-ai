import logging
from typing import Annotated
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
from app.schema.candidate_dto import (
    CandidateDTO, 
    CreateCandidateDTO, 
    UpdateCandidateDTO,
    ChangeCandidateStatusDTO
)
from app.api.api_response import response_fail_status_codes
from app.service.candidate_service import CandidateService
from app.conf.dependencies import get_candidate_service
from app.utils.header_utils import create_list_header

_resource = "candidates"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
                   # dependencies=[Depends(auth_handler.get_token_user)],
                   responses=response_fail_status_codes
                   )


@router.get(
    path="/",
    operation_id="get_candidates",
    name="get_candidates",
    summary="Get Candidates",
    response_model=list[CandidateDTO],
    status_code=status.HTTP_200_OK
)
async def get_candidates(
        request: Request, 
        query: PagingDTO = Depends(PagingDTO),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_candidates rest request")
    page_response = await candidate_service.find(None, query.page, query.size, "_id")
    _log.debug(f"CandidatesApi get_candidates rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [candidate.to_json() for candidate in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/{candidate_id}",
    operation_id="get_candidate",
    name="get_candidate",
    summary="Get Candidate by ID",
    response_model=CandidateDTO,
    status_code=status.HTTP_200_OK
)
async def get_candidate(
        request: Request,
        candidate_id: PydanticObjectId,
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_candidate rest request for candidate: {candidate_id}")
    candidate = await candidate_service.retrieve(str(candidate_id))
    if not candidate:
        return JSONResponse(
            content={"detail": f"Candidate not found: {candidate_id}"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    _log.debug(f"CandidatesApi get_candidate rest response: {candidate}")
    return JSONResponse(content=candidate.to_json())


@router.post(
    path="/",
    operation_id="create_candidate",
    name="create_candidate",
    summary="Create Candidate",
    response_model=CandidateDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_candidate(
        request: Request,
        candidate_data: CreateCandidateDTO = Body(...),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:create_candidate rest request")
    created_candidate = await candidate_service.create(candidate_data=candidate_data)
    _log.debug(f"CandidatesApi create_candidate rest response: {created_candidate}")
    
    return JSONResponse(
        content=created_candidate.to_json(),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    path="/{candidate_id}",
    operation_id="update_candidate",
    name="update_candidate",
    summary="Update Candidate",
    response_model=CandidateDTO,
    status_code=status.HTTP_200_OK
)
async def update_candidate(
        request: Request,
        candidate_id: PydanticObjectId,
        candidate_data: UpdateCandidateDTO = Body(...),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:update_candidate rest request for candidate: {candidate_id}")
    updated_candidate = await candidate_service.update(
        candidate_id=candidate_id,
        candidate_data=candidate_data
    )
    _log.debug(f"CandidatesApi update_candidate rest response: {updated_candidate}")
    
    return JSONResponse(content=updated_candidate.to_json())


@router.delete(
    path="/{candidate_id}",
    operation_id="delete_candidate",
    name="delete_candidate",
    summary="Delete Candidate",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_candidate(
        request: Request,
        candidate_id: PydanticObjectId,
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:delete_candidate rest request for candidate: {candidate_id}")
    await candidate_service.delete(candidate_id)
    _log.debug(f"CandidatesApi delete_candidate rest response: Candidate deleted")
    
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    path="/{candidate_id}/status",
    operation_id="change_candidate_status",
    name="change_candidate_status",
    summary="Change Candidate Status",
    response_model=CandidateDTO,
    status_code=status.HTTP_200_OK
)
async def change_candidate_status(
        request: Request,
        candidate_id: PydanticObjectId,
        status_data: ChangeCandidateStatusDTO = Body(...),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:change_candidate_status rest request for candidate: {candidate_id}")
    updated_candidate = await candidate_service.change_status(
        candidate_id=candidate_id,
        status=status_data.status
    )
    _log.debug(f"CandidatesApi change_candidate_status rest response: {updated_candidate}")
    
    return JSONResponse(content=updated_candidate.to_json())


@router.get(
    path="/search/skills",
    operation_id="find_candidates_by_skills",
    name="find_candidates_by_skills",
    summary="Find Candidates by Skills",
    response_model=list[CandidateDTO],
    status_code=status.HTTP_200_OK
)
async def find_candidates_by_skills(
        request: Request,
        skills: Annotated[list[str], Query(..., description="List of skills to search for")],
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:find_candidates_by_skills rest request for skills: {skills}")
    page_response = await candidate_service.find_by_skills(skills, page, size)
    _log.debug(f"CandidatesApi find_candidates_by_skills rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [candidate.to_json() for candidate in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.get(
    path="/search/seniority",
    operation_id="find_candidates_by_seniority",
    name="find_candidates_by_seniority",
    summary="Find Candidates by Seniority Level",
    response_model=list[CandidateDTO],
    status_code=status.HTTP_200_OK
)
async def find_candidates_by_seniority(
        request: Request,
        seniority_level: Annotated[str, Query(..., description="Seniority level to search for")],
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        candidate_service: CandidateService = Depends(get_candidate_service)) -> JSONResponse:
    _log.debug(f"BEGIN:find_candidates_by_seniority rest request for seniority: {seniority_level}")
    page_response = await candidate_service.find_by_seniority(seniority_level, page, size)
    _log.debug(f"CandidatesApi find_candidates_by_seniority rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [candidate.to_json() for candidate in page_response.content]
    return JSONResponse(content=json_result, headers=headers)
