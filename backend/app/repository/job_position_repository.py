import json
import logging
from typing import Optional

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.job_position_entity import JobPosition
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class JobPositionRepository:
    """
    Job Position Repository class

    This class is responsible for handling all the database operations related to the JobPosition entity.
    JobPosition entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug(f"JobPositionRepository Connecting to database")

    async def create(self, job_position: JobPosition) -> JobPosition:
        _log.debug(f"JobPositionRepository Creating job position: {job_position}")
        result = await JobPosition.insert(job_position)
        _log.debug(f"JobPositionRepository Job position created")
        return result

    async def update(self, job_position: JobPosition) -> JobPosition | None:
        _log.debug(f"JobPositionRepository Updating job position")
        if job_position.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Job position id is required for update")
        result = await job_position.replace()
        _log.debug(f"JobPositionRepository Job position updated")
        return result

    async def delete(self, id: PydanticObjectId):
        _log.debug(f"JobPositionRepository Deleting job position: {id}")
        result = await JobPosition.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Job position not found: {id}")

        await result.delete()
        _log.debug(f"JobPositionRepository Job position deleted")
        return

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-id") -> PageResponse:
        _log.debug(f"JobPositionRepository list request")
        if query is None:
            query = {}
        else:
            query = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await JobPosition.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = JobPosition.find(query).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        page_content = content
        _log.debug(f"JobPositionRepository Job positions retrieved")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        _log.debug(f"JobPositionRepository Counting job positions with query: {query}")
        doc = JobPosition.find(query)
        result = await doc.count()
        _log.debug(f"JobPositionRepository Job positions counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> JobPosition | None:
        _log.debug(f"JobPositionRepository Retrieving job position: {id}")
        doc = await JobPosition.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Job position not found: {id}")
        result = doc
        _log.debug(f"JobPositionRepository Job position retrieved")
        return result

    async def retrieve_by_title(self, title: str) -> Optional[JobPosition]:
        _log.debug(f"JobPositionRepository Retrieving job position by title: {title}")
        doc = await JobPosition.find_one({"title": title})
        if not doc:
            return None
        result = doc
        _log.debug(f"JobPositionRepository Job position retrieved")
        return result

    async def retrieve_by_company(self, company: str) -> Optional[JobPosition]:
        _log.debug(f"JobPositionRepository Retrieving job position by company: {company}")
        doc = await JobPosition.find_one({"company": company})
        if not doc:
            return None
        result = doc
        _log.debug(f"JobPositionRepository Job position retrieved")
        return result

    async def find_by_status(self, status: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"JobPositionRepository Finding job positions by status: {status}")
        query = {"status": status}
        return await self.find(json.dumps(query), page, size)

    async def find_by_employment_type(self, employment_type: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"JobPositionRepository Finding job positions by employment type: {employment_type}")
        query = {"employment_type": employment_type}
        return await self.find(json.dumps(query), page, size)

    async def find_by_seniority_level(self, seniority_level: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"JobPositionRepository Finding job positions by seniority level: {seniority_level}")
        query = {"seniority_level": seniority_level}
        return await self.find(json.dumps(query), page, size)

    async def find_by_location(self, city: str = None, country: str = None, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"JobPositionRepository Finding job positions by location: city={city}, country={country}")
        query = {}
        if city:
            query["city"] = city
        if country:
            query["country"] = country
        
        if not query:
            return await self.find(None, page, size)
        
        return await self.find(json.dumps(query), page, size)

    async def search_by_text(self, search_text: str, page: int = 1, size: int = 10) -> PageResponse:
        _log.debug(f"JobPositionRepository Searching job positions by text: {search_text}")
        # Search in title, summary, and original_text fields
        query = {
            "$or": [
                {"title": {"$regex": search_text, "$options": "i"}},
                {"summary": {"$regex": search_text, "$options": "i"}},
                {"original_text": {"$regex": search_text, "$options": "i"}},
                {"company": {"$regex": search_text, "$options": "i"}}
            ]
        }
        return await self.find(json.dumps(query), page, size)
