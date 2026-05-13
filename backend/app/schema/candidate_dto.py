from datetime import datetime
import uuid
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.consts.enums import SeniorityLevel, CandidateStatus
from app.schema.base_dto import BaseModelJsonSerializable


class _CandidateBase(BaseModelJsonSerializable):
    name: str | None = None
    gender: str | None = None
    year_of_birth: int | None = None
    city: str | None = None
    country: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    title: str | None = None
    seniority_level: SeniorityLevel | None = None


class CreateCandidateDTO(BaseModelJsonSerializable):
    name: str = Field(..., min_length=1, max_length=100, title="Name", description="Candidate's full name")
    gender: str = Field(..., title="Gender", description="Candidate's gender")
    year_of_birth: int = Field(..., ge=1900, le=2024, title="Year of Birth", description="Candidate's year of birth")
    city: str = Field(..., min_length=1, max_length=100, title="City", description="Candidate's city")
    country: str = Field(..., min_length=1, max_length=100, title="Country", description="Candidate's country")
    email: EmailStr = Field(..., title="Email", description="Candidate's email address")
    phone: str = Field(..., min_length=1, max_length=20, title="Phone", description="Candidate's phone number")
    title: str = Field(..., min_length=1, max_length=200, title="Title", description="Candidate's job title")
    seniority_level: SeniorityLevel = Field(..., title="Seniority Level", description="Candidate's seniority level")
    
    model_config = ConfigDict(
        title="Create Candidate Request",
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "gender": "Male",
                "year_of_birth": 1990,
                "city": "New York",
                "country": "USA",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "title": "Senior Software Engineer",
                "seniority_level": "Senior"
            }
        }
    )


class UpdateCandidateDTO(_CandidateBase):
    pass


class CandidateDTO(_CandidateBase):
    id: PydanticObjectId = Field(..., alias="id", title="Candidate ID", description="Candidate ID of the record")
    status: CandidateStatus = Field(..., alias="status", title="Status", description="Candidate's processing status")
    education: Optional[List[dict]] = Field(None, alias="education", title="Education", description="Candidate's education history")
    work_experience: Optional[List[dict]] = Field(None, alias="work_experience", title="Work Experience", description="Candidate's work experience")
    certifications: Optional[List[dict]] = Field(None, alias="certifications", title="Certifications", description="Candidate's certifications")
    skills: Optional[List[dict]] = Field(None, alias="skills", title="Skills", description="Candidate's skills")
    languages: Optional[List[dict]] = Field(None, alias="languages", title="Languages", description="Candidate's language skills")
    keywords: Optional[List[str]] = Field(None, alias="keywords", title="Keywords", description="Candidate's keywords")
    links: dict = Field(..., alias="links", title="Links", description="Candidate's professional links")
    notes: dict = Field(..., alias="notes", title="Notes", description="Candidate's additional notes")
    created_at: datetime | None = Field(..., alias="created_at", title="Created Date", description="Created Date of the record")
    updated_at: datetime | None = Field(..., alias="updated_at", title="Last Updated Date", description="Last Updated Date of the record")

    model_config = ConfigDict(
        from_attributes=True,
        title="Candidate DTO",
        json_schema_extra={
            "example": {
                "candidate_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "name": "John Doe",
                "gender": "Male",
                "year_of_birth": 1990,
                "city": "New York",
                "country": "USA",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "title": "Senior Software Engineer",
                "seniority_level": "Senior",
                "education": [],
                "work_experience": [],
                "certifications": [],
                "skills": None,
                "languages": None,
                "keywords": None,
                "links": {},
                "notes": {},
                "created_at": "2021-01-01T00:00:00",
                "updated_at": "2021-01-01T00:00:00"
            }
        }
    )




class ChangeCandidateStatusDTO(BaseModelJsonSerializable):
    status: CandidateStatus = Field(..., title="Status", description="Candidate's new status")
    
    model_config = ConfigDict(
        title="Change Candidate Status Request",
        json_schema_extra={
            "example": {
                "status": "processing"
            }
        }
    ) 