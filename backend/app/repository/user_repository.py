import json
import logging
from typing import Optional
import uuid

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.user_entity import User
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class UserRepository:
    """
    User Repository class

    This class is responsible for handling all the database operations related to the User entity.
    User entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug(f"UserRepository Connecting to database")

    async def create(self, user: User) -> User:
        _log.debug(f"UserRepository Creating user: {user}")
        result = await User.insert(user)
        _log.debug(f"UserRepository User created")
        return result

    async def update(self, user: User) -> User | None:
        _log.debug(f"UserRepository Updating user")
        if user.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "User id is required for update")
        result = await user.replace()
        _log.debug(f"UserRepository User updated")
        return result

    async def delete(self, id: PydanticObjectId):
        _log.debug(f"UserRepository Deleting user: {id}")
        result = await User.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {id}")

        await result.delete()
        _log.debug(f"UserRepository User deleted")
        return

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-id") -> PageResponse:
        _log.debug(f"UserRepository list request")
        if query is None:
            query = {}
        else:
            query = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await User.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = User.find(query).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        page_content = content
        _log.debug(f"UserRepository Users retrieved")
        return PageResponse(content=page_content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        _log.debug(f"UserRepository Counting users with query: {query}")
        doc = User.find(query)
        result = await doc.count()
        _log.debug(f"UserRepository Users counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> User | None:
        _log.debug(f"UserRepository Retrieving user: {id}")
        doc = await User.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {id}")
        result = doc
        _log.debug(f"UserRepository User retrieved")
        return result

    async def retrieve_by_email(self, email: str) -> Optional[User]:
        _log.debug(f"UserRepository Retrieving user by email: {email}")
        doc = await User.find_one({"email": email})
        if not doc:
            return None
        result = doc
        _log.debug(f"UserRepository User retrieved")
        return result

    async def retrieve_by_email_or_fail(self, email: str) -> User:
        _log.debug(f"UserRepository Retrieving user by email or fail: {email}")
        doc = await User.find_one({"email": email})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {email}")
        result = doc
        _log.debug(f"UserRepository User retrieved")
        return result

