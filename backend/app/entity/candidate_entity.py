from datetime import datetime, timezone
import uuid
from typing import List, Optional
from enum import Enum

from beanie import Document, Update, Replace, before_event
from pydantic import EmailStr, Field, BaseModel

from app.consts.enums import SeniorityLevel, DegreeType, WorkArrangement, CandidateStatus
from app.consts.models import Language


class PersonalInfo(BaseModel):
    name: str
    gender: str
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

class Candidate(Document):
    status: CandidateStatus
    name: str
    gender: Optional[str]
    year_of_birth: Optional[int]
    city: Optional[str]
    country: Optional[str]
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: str
    seniority_level: SeniorityLevel
    education: Optional[List[Education]] = None
    work_experience: Optional[List[WorkExperience]] = None
    certifications: Optional[List[Certification]] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    keywords: Optional[List[str]] = None
    links: Links
    notes: Notes
    raw_cv: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Settings:
        name = "candidates"
        validate_on_save = True

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"Candidate: {self.candidate_id}, {self.name}, {self.title}" 