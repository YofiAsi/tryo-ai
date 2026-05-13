import json
import logging
from typing import Optional
import uuid

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.candidate_entity import Candidate
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class CandidateRepository:
    """
    Candidate Repository class

    This class is responsible for handling all the database operations related to the Candidate entity.
    Candidate entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug(f"CandidateRepository Connecting to database")

    async def create(self, candidate: Candidate) -> Candidate:
        _log.debug(f"CandidateRepository Creating candidate: {candidate}")
        result = await Candidate.insert(candidate)
        _log.debug(f"CandidateRepository Candidate created")
        return result

    async def update(self, candidate: Candidate) -> Candidate | None:
        _log.debug(f"CandidateRepository Updating candidate")
        if candidate.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Candidate id is required for update")
        result = await candidate.replace()
        _log.debug(f"CandidateRepository Candidate updated")
        return result

    async def delete(self, id: PydanticObjectId):
        _log.debug(f"CandidateRepository Deleting candidate: {id}")
        result = await Candidate.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Candidate not found: {id}")

        await result.delete()
        _log.debug(f"CandidateRepository Candidate deleted")
        return

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-id") -> PageResponse:
        _log.debug(f"CandidateRepository list request")
        if query is None:
            query = {}
        else:
            query = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Candidate.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Candidate.find(query).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        page_content = content
        _log.debug(f"CandidateRepository Candidates retrieved")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        _log.debug(f"CandidateRepository Counting candidates with query: {query}")
        doc = Candidate.find(query)
        result = await doc.count()
        _log.debug(f"CandidateRepository Candidates counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> Candidate | None:
        _log.debug(f"CandidateRepository Retrieving candidate: {id}")
        doc = await Candidate.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Candidate not found: {id}")
        result = doc
        _log.debug(f"CandidateRepository Candidate retrieved")
        return result

    async def retrieve_by_email(self, email: str) -> Optional[Candidate]:
        _log.debug(f"CandidateRepository Retrieving candidate by email: {email}")
        doc = await Candidate.find_one({"email": email})
        if not doc:
            return None
        result = doc
        _log.debug(f"CandidateRepository Candidate retrieved")
        return result

    async def retrieve_by_email_or_fail(self, email: str) -> Candidate:
        _log.debug(f"CandidateRepository Retrieving candidate by email or fail: {email}")
        doc = await Candidate.find_one({"email": email})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Candidate not found: {email}")
        result = doc
        _log.debug(f"CandidateRepository Candidate retrieved")
        return result

    async def find_by_skills(self, skills: list[str], page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"CandidateRepository Finding candidates by skills: {skills}")
        query = {"skills.name": {"$in": skills}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Candidate.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Candidate.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        page_content = content
        _log.debug(f"CandidateRepository Candidates found by skills")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)

    async def find_by_seniority(self, seniority_level: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"CandidateRepository Finding candidates by seniority: {seniority_level}")
        query = {"seniority_level": seniority_level}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Candidate.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Candidate.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        page_content = content
        _log.debug(f"CandidateRepository Candidates found by seniority")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)
