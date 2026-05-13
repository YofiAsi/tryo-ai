from datetime import datetime, timezone
import logging
from typing import Optional

from fastapi import Depends

from app.conf.page_response import PageResponse
from app.entity.job_position_entity import JobPosition, JobStatus, JobTournament, JobTournamentStatus
from app.entity.task_entity import Task
from app.errors.business_exception import BusinessException, ErrorCodes
from app.repository.job_position_repository import JobPositionRepository
from app.schema.job_position_dto import CreateJobPositionDTO, JobPositionDTO, UpdateJobPositionDTO

_log = logging.getLogger(__name__)


class JobPositionService:
    """
    Job Position Business Logic Service that is responsible for handling business logic for JobPosition entity operations.

    Attributes:
    job_position_repository: JobPositionRepository
        Repository for JobPosition entity operations

    """

    def __init__(self, job_position_repository: JobPositionRepository = Depends()):
        _log.info("JobPositionService Initializing")
        self.repository = job_position_repository

    async def retrieve(self, job_position_id: str) -> Optional[JobPositionDTO]:
        _log.debug(f"JobPositionService Retrieving job position: {job_position_id}")
        
        try:
            from beanie import PydanticObjectId
            job_position_object_id = PydanticObjectId(job_position_id)
        except Exception:
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid job position ID format: {job_position_id}")
        
        final_job_position = await self.repository.retrieve(job_position_object_id)
        if final_job_position is None:
            _log.error("JobPositionService Job position not found")
            return None
        result = JobPositionDTO.model_validate(final_job_position)
        _log.debug("JobPositionService Job position retrieved")
        return result

    async def find(self, query, page: int, size: int, sort: str = "_id") -> PageResponse[JobPositionDTO]:
        _log.debug("JobPositionService list request")
        entity_page_response = await self.repository.find(query, page, size, sort)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug("JobPositionService Job positions retrieved")
        return page_response

    async def delete(self, job_position_id: str):
        _log.debug(f"Deleting job position: {job_position_id}")
        
        try:
            from beanie import PydanticObjectId
            job_position_object_id = PydanticObjectId(job_position_id)
        except Exception:
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid job position ID format: {job_position_id}")

        await self.repository.delete(job_position_object_id)
        _log.debug("Deleted job position")

    async def count(self, query: dict) -> int:
        _log.debug(f"JobPositionService Counting job positions with query: {query}")
        result = await self.repository.count(query)
        _log.debug(f"JobPositionService Job positions counted: {result}")
        return result

    async def retrieve_by_title(self, title: str) -> Optional[JobPositionDTO]:
        _log.debug(f"JobPositionService Retrieving job position by title: {title}")
        final_job_position = await self.repository.retrieve_by_title(title)
        if final_job_position is None:
            return None
        result = JobPositionDTO.model_validate(final_job_position)
        _log.debug(f"JobPositionService Job position retrieved: {result}")
        return result

    async def retrieve_by_company(self, company: str) -> Optional[JobPositionDTO]:
        _log.debug(f"JobPositionService Retrieving job position by company: {company}")
        final_job_position = await self.repository.retrieve_by_company(company)
        if final_job_position is None:
            return None
        result = JobPositionDTO.model_validate(final_job_position)
        _log.debug(f"JobPositionService Job position retrieved: {result}")
        return result

    async def create(self, job_position_data: CreateJobPositionDTO) -> JobPositionDTO:
        _log.debug(f"JobPositionService Creating job position: {job_position_data.title}, {job_position_data.company}")
        
        # Check if job position with same title and company already exists
        existing_job_position = await self.repository.retrieve_by_title(job_position_data.title)
        if existing_job_position and existing_job_position.company == job_position_data.company:
            raise BusinessException(ErrorCodes.DUPLICATE_ENTRY, f"Job position with title '{job_position_data.title}' already exists at company '{job_position_data.company}'")

        # Create a new job position entity
        job_position = JobPosition(
            status=JobStatus.DRAFT,  # Default status for new job positions
            title=job_position_data.title,
            original_text=job_position_data.original_text,
            summary=job_position_data.summary,
            company=job_position_data.company,
            city=job_position_data.city,
            country=job_position_data.country,
            employment_type=job_position_data.employment_type,
            seniority_level=job_position_data.seniority_level,
            work_arrangement=job_position_data.work_arrangement,
            responsibilities=job_position_data.responsibilities,
            recruiter_notes=job_position_data.recruiter_notes,
            salary=job_position_data.salary,
            contact_email=job_position_data.contact_email,
            contact_name=job_position_data.contact_name,
            contact_phone=job_position_data.contact_phone,
            skills=job_position_data.skills,
            requirements=job_position_data.requirements,
            tournament=JobTournament(
                status=JobTournamentStatus.PENDING,
                task=None,  # Will be set when tournament is created
                candidates=[]
            ),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Save to database
        created_job_position = await self.repository.create(job_position)
        _log.debug(f"JobPositionService Job position created: {created_job_position}")
        
        result = JobPositionDTO.model_validate(created_job_position)
        return result

    async def update(self, job_position_id: str, job_position_data: UpdateJobPositionDTO) -> JobPositionDTO:
        _log.debug(f"JobPositionService Updating job position: {job_position_id}")
        
        try:
            from beanie import PydanticObjectId
            job_position_object_id = PydanticObjectId(job_position_id)
        except Exception:
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid job position ID format: {job_position_id}")

        # Retrieve existing job position
        existing_job_position = await self.repository.retrieve(job_position_object_id)
        if not existing_job_position:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Job position not found: {job_position_id}")

        # Update fields if provided
        if job_position_data.title is not None:
            existing_job_position.title = job_position_data.title
        if job_position_data.company is not None:
            existing_job_position.company = job_position_data.company
        if job_position_data.city is not None:
            existing_job_position.city = job_position_data.city
        if job_position_data.country is not None:
            existing_job_position.country = job_position_data.country
        if job_position_data.employment_type is not None:
            existing_job_position.employment_type = job_position_data.employment_type
        if job_position_data.seniority_level is not None:
            existing_job_position.seniority_level = job_position_data.seniority_level
        if job_position_data.work_arrangement is not None:
            existing_job_position.work_arrangement = job_position_data.work_arrangement
        if job_position_data.responsibilities is not None:
            existing_job_position.responsibilities = job_position_data.responsibilities
        if job_position_data.recruiter_notes is not None:
            existing_job_position.recruiter_notes = job_position_data.recruiter_notes
        if job_position_data.salary is not None:
            existing_job_position.salary = job_position_data.salary
        if job_position_data.contact_email is not None:
            existing_job_position.contact_email = job_position_data.contact_email
        if job_position_data.contact_name is not None:
            existing_job_position.contact_name = job_position_data.contact_name
        if job_position_data.contact_phone is not None:
            existing_job_position.contact_phone = job_position_data.contact_phone
        if job_position_data.skills is not None:
            existing_job_position.skills = job_position_data.skills
        if job_position_data.requirements is not None:
            existing_job_position.requirements = job_position_data.requirements

        # Update timestamp
        existing_job_position.updated_at = datetime.now(timezone.utc)

        # Save changes
        updated_job_position = await self.repository.update(existing_job_position)
        if not updated_job_position:
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, "Failed to update job position")

        _log.debug(f"JobPositionService Job position updated: {updated_job_position}")
        result = JobPositionDTO.model_validate(updated_job_position)
        return result

    async def change_status(self, job_position_id: str, new_status: JobStatus) -> JobPositionDTO:
        _log.debug(f"JobPositionService Changing job position status: {job_position_id} to {new_status}")
        
        try:
            from beanie import PydanticObjectId
            job_position_object_id = PydanticObjectId(job_position_id)
        except Exception:
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid job position ID format: {job_position_id}")

        # Retrieve existing job position
        existing_job_position = await self.repository.retrieve(job_position_object_id)
        if not existing_job_position:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Job position not found: {job_position_id}")

        # Validate status transition
        if not self._is_valid_status_transition(existing_job_position.status, new_status):
            raise BusinessException(ErrorCodes.INVALID_INPUT, f"Invalid status transition from {existing_job_position.status} to {new_status}")

        # Update status
        existing_job_position.status = new_status
        existing_job_position.updated_at = datetime.now(timezone.utc)

        # Save changes
        updated_job_position = await self.repository.update(existing_job_position)
        if not updated_job_position:
            raise BusinessException(ErrorCodes.INTERNAL_ERROR, "Failed to update job position status")

        _log.debug(f"JobPositionService Job position status changed: {updated_job_position}")
        result = JobPositionDTO.model_validate(updated_job_position)
        return result

    async def find_by_status(self, status: str, page: int = 1, size: int = 10) -> PageResponse[JobPositionDTO]:
        _log.debug(f"JobPositionService Finding job positions by status: {status}")
        entity_page_response = await self.repository.find_by_status(status, page, size)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        return page_response

    async def find_by_employment_type(self, employment_type: str, page: int = 1, size: int = 10) -> PageResponse[JobPositionDTO]:
        _log.debug(f"JobPositionService Finding job positions by employment type: {employment_type}")
        entity_page_response = await self.repository.find_by_employment_type(employment_type, page, size)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        return page_response

    async def find_by_seniority_level(self, seniority_level: str, page: int = 1, size: int = 10) -> PageResponse[JobPositionDTO]:
        _log.debug(f"JobPositionService Finding job positions by seniority level: {seniority_level}")
        entity_page_response = await self.repository.find_by_seniority_level(seniority_level, page, size)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        return page_response

    async def find_by_location(self, city: str = None, country: str = None, page: int = 1, size: int = 10) -> PageResponse[JobPositionDTO]:
        _log.debug(f"JobPositionService Finding job positions by location: city={city}, country={country}")
        entity_page_response = await self.repository.find_by_location(city, country, page, size)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        return page_response

    async def search_by_text(self, search_text: str, page: int = 1, size: int = 10) -> PageResponse[JobPositionDTO]:
        _log.debug(f"JobPositionService Searching job positions by text: {search_text}")
        entity_page_response = await self.repository.search_by_text(search_text, page, size)
        page_response = PageResponse[JobPositionDTO](
            content=[JobPositionDTO.model_validate(job_position) for job_position in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )
        return page_response

    def _is_valid_status_transition(self, current_status: JobStatus, new_status: JobStatus) -> bool:
        """Validate if the status transition is allowed"""
        valid_transitions = {
            JobStatus.DRAFT: [JobStatus.OPEN, JobStatus.ARCHIVED],
            JobStatus.OPEN: [JobStatus.CLOSED, JobStatus.ARCHIVED],
            JobStatus.CLOSED: [JobStatus.OPEN, JobStatus.ARCHIVED],
            JobStatus.ARCHIVED: [JobStatus.DRAFT, JobStatus.OPEN],
            JobStatus.PENDING: [JobStatus.PROCESSING, JobStatus.FAILED],
            JobStatus.PROCESSING: [JobStatus.COMPLETED, JobStatus.FAILED],
            JobStatus.COMPLETED: [JobStatus.OPEN, JobStatus.ARCHIVED],
            JobStatus.FAILED: [JobStatus.PENDING, JobStatus.ARCHIVED]
        }
        
        return new_status in valid_transitions.get(current_status, [])
