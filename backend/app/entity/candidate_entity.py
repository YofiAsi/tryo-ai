from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from beanie import Document, Insert, Replace, Save, Update, before_event
from pydantic import BaseModel, EmailStr, Field

from app.consts.enums import CandidateStatus, DegreeType, Gender, SeniorityLevel, WorkArrangement
from app.consts.models import Language


class PersonalInfo(BaseModel):
    name: str
    gender: Gender
    year_of_birth: int
    city: str
    country: str

class Education(BaseModel):
    school: Optional[str] = None
    degree: Optional[DegreeType] = None
    field_of_study: str
    start_year: Optional[str]
    end_year: Optional[str]
    grade: Optional[int]

class WorkExperience(BaseModel):
    company: str
    title: str
    industry: str
    start_year: int
    end_year: int
    seniority_level: SeniorityLevel
    description: str
    responsibilities: List[str]
    skills: List[str]

class Certification(BaseModel):
    name: str
    issuer: str
    year: Optional[int] = None
    description: Optional[str]

class Skill(BaseModel):
    name: str
    years_of_experience: int

class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    website: Optional[str] = None

class Notes(BaseModel):
    salary_expectation: Optional[int] = None
    work_region: Optional[List[str]] = None
    position_preference: Optional[WorkArrangement] = None
    notes: Optional[str] = None

class Embeddings(BaseModel):
    general: Optional[List[float]] = Field(None, description="The embeddings for the general information of the candidate")
    skills: Optional[List[float]] = Field(None, description="The embeddings for the skills of the candidate")
    work_experience: Optional[List[float]] = Field(None, description="The embeddings for the work experience of the candidate")

    def __str__(self) -> str:
        return ""

class CandidateMetadata(BaseModel):
    file_id: UUID = Field(description="The ID of the file that the candidate is being processed from")
    original_cv_minio_path: str = Field(description="The path to the original CV in Minio")
    txt_cv_minio_path: str = Field(description="The path to the txt CV in Minio")
    parse_model: Optional[str] = Field(None, description="The model that was used to parse the candidate")

class Candidate(Document):
    status: CandidateStatus
    embeddings: Embeddings
    name: str
    gender: Optional[Gender]
    year_of_birth: Optional[int]
    city: Optional[str]
    country: Optional[str]
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: str
    seniority_level: SeniorityLevel
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    links: Links = Field(default_factory=Links)
    notes: Notes = Field(default_factory=Notes)
    raw_cv: str
    metadata: CandidateMetadata
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Settings:
        name = "candidates"
        validate_on_save = True

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Save, Insert)
    def before_save(self):
        """Automatically update the created_at and updated_at fields before saving"""
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"Candidate: {self.id}, {self.name}, {self.title}" 