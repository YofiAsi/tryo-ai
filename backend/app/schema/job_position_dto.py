from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.consts.enums import SeniorityLevel, WorkArrangement
from app.entity.job_position_entity import JobStatus, EmploymentType, JobSkill, Requirements, JobTournament
from app.schema.base_dto import BaseModelJsonSerializable


class _JobPositionBase(BaseModelJsonSerializable):
    title: str | None = None
    company: str | None = None
    city: str | None = None
    country: str | None = None
    employment_type: EmploymentType | None = None
    seniority_level: SeniorityLevel | None = None
    work_arrangement: WorkArrangement | None = None
    responsibilities: Optional[List[str]] = None
    recruiter_notes: Optional[str] = None
    salary: Optional[int] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    skills: Optional[List[JobSkill]] = None
    requirements: Optional[Requirements] = None


class CreateJobPositionDTO(BaseModelJsonSerializable):
    title: str = Field(..., min_length=1, max_length=200, title="Title", description="Job position title")
    original_text: str = Field(..., min_length=1, title="Original Text", description="Original job description text")
    summary: str = Field(..., min_length=1, max_length=1000, title="Summary", description="Job position summary")
    company: str = Field(..., min_length=1, max_length=200, title="Company", description="Company name")
    city: Optional[str] = Field(None, max_length=100, title="City", description="Job location city")
    country: Optional[str] = Field(None, max_length=100, title="Country", description="Job location country")
    employment_type: EmploymentType = Field(..., title="Employment Type", description="Type of employment")
    seniority_level: SeniorityLevel = Field(..., title="Seniority Level", description="Required seniority level")
    work_arrangement: WorkArrangement = Field(..., title="Work Arrangement", description="Work arrangement type")
    responsibilities: Optional[List[str]] = Field(None, title="Responsibilities", description="Job responsibilities")
    recruiter_notes: Optional[str] = Field(None, title="Recruiter Notes", description="Additional recruiter notes")
    salary: Optional[int] = Field(None, ge=0, title="Salary", description="Annual salary in currency units")
    contact_email: Optional[EmailStr] = Field(None, title="Contact Email", description="Contact email for applications")
    contact_name: Optional[str] = Field(None, max_length=100, title="Contact Name", description="Contact person name")
    contact_phone: Optional[str] = Field(None, max_length=20, title="Contact Phone", description="Contact phone number")
    skills: Optional[List[JobSkill]] = Field(None, title="Skills", description="Required skills for the position")
    requirements: Optional[Requirements] = Field(None, title="Requirements", description="Job requirements")
    
    model_config = ConfigDict(
        title="Create Job Position Request",
        json_schema_extra={
            "example": {
                "title": "Senior Software Engineer",
                "original_text": "We are looking for a Senior Software Engineer...",
                "summary": "Join our team as a Senior Software Engineer...",
                "company": "TechCorp Inc.",
                "city": "San Francisco",
                "country": "USA",
                "employment_type": "full-time",
                "seniority_level": "Senior",
                "work_arrangement": "hybrid",
                "responsibilities": ["Develop software solutions", "Lead technical projects"],
                "recruiter_notes": "Looking for someone with Python experience",
                "salary": 120000,
                "contact_email": "hr@techcorp.com",
                "contact_name": "Jane Smith",
                "contact_phone": "+1234567890",
                "skills": [
                    {"name": "Python", "years_of_experience": 5, "weight": 10}
                ],
                "requirements": {
                    "certifications": ["AWS Certified Developer"],
                    "educations": [],
                    "languages": []
                }
            }
        }
    )


class UpdateJobPositionDTO(_JobPositionBase):
    pass


class JobPositionDTO(_JobPositionBase):
    id: PydanticObjectId = Field(..., alias="id", title="Job Position ID", description="Job Position ID of the record")
    status: JobStatus = Field(..., alias="status", title="Status", description="Job position status")
    original_text: str = Field(..., alias="original_text", title="Original Text", description="Original job description text")
    summary: str = Field(..., alias="summary", title="Summary", description="Job position summary")
    tournament: JobTournament = Field(..., alias="tournament", title="Tournament", description="Job tournament information")
    created_at: datetime | None = Field(..., alias="created_at", title="Created Date", description="Created Date of the record")
    updated_at: datetime | None = Field(..., alias="updated_at", title="Last Updated Date", description="Last Updated Date of the record")

    model_config = ConfigDict(
        from_attributes=True,
        title="Job Position DTO",
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "status": "open",
                "title": "Senior Software Engineer",
                "original_text": "We are looking for a Senior Software Engineer...",
                "summary": "Join our team as a Senior Software Engineer...",
                "company": "TechCorp Inc.",
                "city": "San Francisco",
                "country": "USA",
                "employment_type": "full-time",
                "seniority_level": "Senior",
                "work_arrangement": "hybrid",
                "responsibilities": ["Develop software solutions", "Lead technical projects"],
                "recruiter_notes": "Looking for someone with Python experience",
                "salary": 120000,
                "contact_email": "hr@techcorp.com",
                "contact_name": "Jane Smith",
                "contact_phone": "+1234567890",
                "skills": [
                    {"name": "Python", "years_of_experience": 5, "weight": 10}
                ],
                "requirements": {
                    "certifications": ["AWS Certified Developer"],
                    "educations": [],
                    "languages": []
                },
                "tournament": {
                    "status": "pending",
                    "task": "507f1f77bcf86cd799439012",
                    "candidates": []
                },
                "created_at": "2021-01-01T00:00:00",
                "updated_at": "2021-01-01T00:00:00"
            }
        }
    )


