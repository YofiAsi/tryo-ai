from datetime import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, validator
from beanie import PydanticObjectId
from app.consts import UserRole
from app.schema.base_dto import BaseModelJsonSerializable

# @formatter:off
class _UserBase(BaseModelJsonSerializable):
    name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None

class CreateUserDTO(BaseModelJsonSerializable):
    name: str = Field(..., min_length=1, max_length=100, title="Name", description="User's full name")
    email: EmailStr = Field(..., title="Email", description="User's email address")
    role: UserRole = Field(..., title="Role", description="User's role in the system")
    
    model_config = ConfigDict(
        title="Create User Request",
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@doe.com",
                "role": "admin"
            }
        }
    )

class UserDTO(_UserBase):
    id: PydanticObjectId = Field(..., title="User ID", description="User ID of the record")
    is_active: bool = Field(..., title="Is Active", description="User's active status")
    created_at: datetime = Field(..., title="Created Date", description="Created Date of the record")
    updated_at: datetime = Field(..., title="Last Updated Date", description="Last Updated Date of the record")

    model_config = ConfigDict(
        from_attributes=True,
        title="User DTO",
        json_schema_extra={
            "example": {
                "id": "689c7713a998b5ddae540024",
                "name": "John Doe",
                "email": "john@doe.com",
                "role": "admin",
                "is_active": True,
                "created_at": "2021-01-01T00:00:00",
                "updated_at": "2021-01-01T00:00:00"
            }})




class ChangeUserActiveStatusDTO(BaseModelJsonSerializable):
    is_active: bool = Field(..., title="Is Active", description="User's active status")
    
    model_config = ConfigDict(
        title="Change User Active Status Request",
        json_schema_extra={
            "example": {
                "is_active": True
            }
        }
    )


