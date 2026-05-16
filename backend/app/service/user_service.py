from datetime import datetime, timezone
import logging
import uuid
from typing import Optional
from beanie import PydanticObjectId
from fastapi import Depends

from app.conf.app_settings import app_settings
from app.conf.page_response import PageResponse
from app.entity.user_entity import User
from app.errors.business_exception import BusinessException, ErrorCodes
from app.repository.user_repository import UserRepository
from app.schema.user_dto import CreateUserDTO, UserDTO
from app.consts import UserRole

_log = logging.getLogger(__name__)


class UserService:
    """
    User Business Logic Service that is responsible for handling business logic for User entity operations.

    Attributes:
    user_repository: UserRepository
        Repository for User entity operations

    """

    def __init__(self, user_repository: UserRepository = Depends()):
        _log.info("UserService Initializing")
        self.repository = user_repository

    async def retrieve(self, user_id: PydanticObjectId) -> Optional[UserDTO]:
        _log.debug(f"UserService Retrieving user: {user_id}")
        
        final_user = await self.repository.retrieve(user_id)
        if final_user is None:
            _log.error("UserService User not found")
            return None
        result = UserDTO.model_validate(final_user)
        _log.debug("UserService User retrieved")
        return result


    async def find(self, query, page: int, size: int, sort: str = "_id") -> PageResponse[UserDTO]:
        _log.debug("UserService list request")
        entity_page_response = await self.repository.find(query, page, size, sort)
        page_response = PageResponse[UserDTO](
            content=[UserDTO.model_validate(user) for user in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug("UserService Users retrieved")
        return page_response

    async def delete(self, user_id: str):
        _log.debug(f"Deleting user: {user_id}")
        
        # Convert string user_id to UUID if needed

        await self.check_default_user(user_id)
        await self.repository.delete(user_id)
        _log.debug("Deleted user")

    async def count(self, query: dict) -> int:
        _log.debug(f"UserService Counting users with query: {query}")
        result = await self.repository.count(query)
        _log.debug(f"UserService Users counted: {result}")
        return result

    async def retrieve_by_email(self, email: str) -> Optional[UserDTO]:
        _log.debug(f"UserService Retrieving user by email: {email}")
        final_user = await self.repository.retrieve_by_email(email)
        if final_user is None:
            return None
        result = UserDTO.model_validate(final_user)
        _log.debug(f"UserService User retrieved: {result}")
        return result

    async def retrieve_by_email_or_fail(self, email: str) -> UserDTO:
        _log.debug(f"UserService Retrieving user by email or fail: {email}")
        final_user = await self.repository.retrieve_by_email_or_fail(email)
        result = UserDTO.model_validate(final_user)
        _log.debug(f"UserService User retrieved: {result}")
        return result

    async def create(self, user: CreateUserDTO) -> UserDTO:
        _log.debug(f"UserService Creating user: {user.name}, {user.email}, {user.role}")
        
        # Check if user with email already exists
        existing_user = await self.repository.retrieve_by_email(user.email)
        if existing_user:
            raise BusinessException(ErrorCodes.CONFLICT, f"User with email {user.email} already exists")
        
        # Create new user entity
        from datetime import datetime, timezone
        import uuid
        
        user = User(
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        created_user = await self.repository.create(user)
        result = UserDTO.model_validate(created_user)
        _log.debug(f"UserService User created: {result}")
        return result

    async def check_default_user(self, user_id: PydanticObjectId):
        _log.debug(f"UserService Checking if user is default user: {user_id}")
        # Add logic to prevent deactivation of default admin user
        # This is a placeholder - implement based on your business rules
        # For example, you might have a specific user ID that should never be deactivated
        # You could check against a configuration or environment variable
        # if user_id == app_settings.DEFAULT_ADMIN_USER_ID:
        #     raise BusinessException(ErrorCodes.FORBIDDEN, "Cannot deactivate default admin user")
        pass

    async def change_active_status(self, user_id: PydanticObjectId, is_active: bool) -> UserDTO:
        _log.debug(f"UserService Changing active status for user: {user_id} to {is_active}")
        
        # Retrieve the user
        user = await self.repository.retrieve(user_id)
        if user is None:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {user_id}")
        
        # Check if trying to deactivate default user
        if not is_active:
            await self.check_default_user(user_id)
        
        # Update the active status
        user.is_active = is_active
        
        updated_user = await self.repository.update(user)
        result = UserDTO.model_validate(updated_user)
        _log.debug(f"UserService User active status changed: {result}")
        return result
