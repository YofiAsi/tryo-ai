from datetime import datetime, timezone
import logging
import uuid
from typing import Optional

from fastapi import Depends

from app.conf.page_response import PageResponse
from app.entity.candidate_entity import Candidate, Links, Notes
from app.consts.enums import CandidateStatus
from app.errors.business_exception import BusinessException, ErrorCodes
from app.repository.candidate_repository import CandidateRepository
from app.schema.candidate_dto import CreateCandidateDTO, CandidateDTO, UpdateCandidateDTO

_log = logging.getLogger(__name__)


class CandidateService:
    """
    Candidate Business Logic Service that is responsible for handling business logic for Candidate entity operations.

    Attributes:
    candidate_repository: CandidateRepository
        Repository for Candidate entity operations

    """

    def __init__(self, candidate_repository: CandidateRepository = Depends()):
        _log.info("CandidateService Initializing")
        self.repository = candidate_repository

    async def retrieve(self, candidate_id: str) -> Optional[CandidateDTO]:
        _log.debug(f"CandidateService Retrieving candidate: {candidate_id}")
        
        # Convert string candidate_id to UUID if needed
        try:
            candidate_uuid = uuid.UUID(candidate_id) if isinstance(candidate_id, str) else candidate_id
        except ValueError:
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid candidate ID format: {candidate_id}")
        
        final_candidate = await self.repository.retrieve(candidate_uuid)
        if final_candidate is None:
            _log.error("CandidateService Candidate not found")
            return None
        result = CandidateDTO.model_validate(final_candidate)
        _log.debug("CandidateService Candidate retrieved")
        return result

    async def find(self, query, page: int, size: int, sort: str = "_id") -> PageResponse[CandidateDTO]:
        _log.debug("CandidateService list request")
        entity_page_response = await self.repository.find(query, page, size, sort)
        page_response = PageResponse[CandidateDTO](
            content=[CandidateDTO.model_validate(candidate) for candidate in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug("CandidateService Candidates retrieved")
        return page_response

    async def delete(self, candidate_id: uuid.UUID):
        _log.debug(f"Deleting candidate: {candidate_id}")
        
        # Convert string candidate_id to UUID if needed
        if isinstance(candidate_id, str):
            try:
                candidate_id = uuid.UUID(candidate_id)
            except ValueError:
                raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid candidate ID format: {candidate_id}")

        await self.repository.delete(candidate_id)
        _log.debug("Deleted candidate")

    async def count(self, query: dict) -> int:
        _log.debug(f"CandidateService Counting candidates with query: {query}")
        result = await self.repository.count(query)
        _log.debug(f"CandidateService Candidates counted: {result}")
        return result

    async def retrieve_by_email(self, email: str) -> Optional[CandidateDTO]:
        _log.debug(f"CandidateService Retrieving candidate by email: {email}")
        final_candidate = await self.repository.retrieve_by_email(email)
        if final_candidate is None:
            return None
        result = CandidateDTO.model_validate(final_candidate)
        _log.debug(f"CandidateService Candidate retrieved: {result}")
        return result

    async def retrieve_by_email_or_fail(self, email: str) -> CandidateDTO:
        _log.debug(f"CandidateService Retrieving candidate by email or fail: {email}")
        final_candidate = await self.repository.retrieve_by_email_or_fail(email)
        result = CandidateDTO.model_validate(final_candidate)
        _log.debug(f"CandidateService Candidate retrieved: {result}")
        return result

    async def create(self, candidate_data: CreateCandidateDTO) -> CandidateDTO:
        _log.debug(f"CandidateService Creating candidate: {candidate_data.name}, {candidate_data.email}")
        
        # Check if candidate with email already exists
        existing_candidate = await self.repository.retrieve_by_email(candidate_data.email)
        if existing_candidate:
            raise BusinessException(ErrorCodes.CONFLICT, f"Candidate with email {candidate_data.email} already exists")
        
        # Create new candidate entity
        candidate = Candidate(
            status=CandidateStatus.PENDING,
            name=candidate_data.name,
            gender=candidate_data.gender,
            year_of_birth=candidate_data.year_of_birth,
            city=candidate_data.city,
            country=candidate_data.country,
            email=candidate_data.email,
            phone=candidate_data.phone,
            title=candidate_data.title,
            seniority_level=candidate_data.seniority_level,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        created_candidate = await self.repository.create(candidate)
        result = CandidateDTO.model_validate(created_candidate)
        _log.debug(f"CandidateService Candidate created: {result}")
        return result

    async def update(self, candidate_id: uuid.UUID, candidate_data: UpdateCandidateDTO) -> CandidateDTO:
        _log.debug(f"CandidateService Updating candidate: {candidate_id}")
        
        # Convert string candidate_id to UUID if needed
        if isinstance(candidate_id, str):
            try:
                candidate_id = uuid.UUID(candidate_id)
            except ValueError:
                raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid candidate ID format: {candidate_id}")
        
        # Retrieve the candidate
        candidate = await self.repository.retrieve(candidate_id)
        if candidate is None:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Candidate not found: {candidate_id}")
        
        # Update fields if provided
        if candidate_data.name is not None:
            candidate.name = candidate_data.name
        if candidate_data.gender is not None:
            candidate.gender = candidate_data.gender
        if candidate_data.year_of_birth is not None:
            candidate.year_of_birth = candidate_data.year_of_birth
        if candidate_data.city is not None:
            candidate.city = candidate_data.city
        if candidate_data.country is not None:
            candidate.country = candidate_data.country
        if candidate_data.email is not None:
            # Check if new email already exists for another candidate
            if candidate_data.email != candidate.email:
                existing_candidate = await self.repository.retrieve_by_email(candidate_data.email)
                if existing_candidate and existing_candidate.candidate_id != candidate_id:
                    raise BusinessException(ErrorCodes.CONFLICT, f"Candidate with email {candidate_data.email} already exists")
            candidate.email = candidate_data.email
        if candidate_data.phone is not None:
            candidate.phone = candidate_data.phone
        if candidate_data.title is not None:
            candidate.title = candidate_data.title
        if candidate_data.seniority_level is not None:
            candidate.seniority_level = candidate_data.seniority_level
        
        updated_candidate = await self.repository.update(candidate)
        result = CandidateDTO.model_validate(updated_candidate)
        _log.debug(f"CandidateService Candidate updated: {result}")
        return result

    async def change_status(self, candidate_id: uuid.UUID, status: CandidateStatus) -> CandidateDTO:
        _log.debug(f"CandidateService Changing status for candidate: {candidate_id} to {status}")
        
        # Convert string candidate_id to UUID if needed
        if isinstance(candidate_id, str):
            try:
                candidate_id = uuid.UUID(candidate_id)
            except ValueError:
                raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid candidate ID format: {candidate_id}")
        
        # Retrieve the candidate
        candidate = await self.repository.retrieve(candidate_id)
        if candidate is None:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Candidate not found: {candidate_id}")
        
        # Update the status
        candidate.status = status
        
        updated_candidate = await self.repository.update(candidate)
        result = CandidateDTO.model_validate(updated_candidate)
        _log.debug(f"CandidateService Candidate status changed: {result}")
        return result

    async def find_by_skills(self, skills: list[str], page: int = 1, size: int = 10) -> PageResponse[CandidateDTO]:
        _log.debug(f"CandidateService Finding candidates by skills: {skills}")
        entity_page_response = await self.repository.find_by_skills(skills, page, size)
        page_response = PageResponse[CandidateDTO](
            content=[CandidateDTO.model_validate(candidate) for candidate in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        _log.debug(f"CandidateService Candidates found by skills")
        return page_response

    async def find_by_seniority(self, seniority_level: str, page: int = 1, size: int = 10) -> PageResponse[CandidateDTO]:
        _log.debug(f"CandidateService Finding candidates by seniority: {seniority_level}")
        entity_page_response = await self.repository.find_by_seniority(seniority_level, page, size)
        page_response = PageResponse[CandidateDTO](
            content=[CandidateDTO.model_validate(candidate) for candidate in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        _log.debug(f"CandidateService Candidates found by seniority")
        return page_response
