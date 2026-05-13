from datetime import datetime, timezone
import uuid
from typing import List, Optional
from enum import Enum

from beanie import Document, Update, Replace, before_event, Link
from pydantic import BaseModel, Field, EmailStr

from app.consts.enums import SeniorityLevel, TournamentCandidateStatus, WorkArrangement
from app.consts.models import Language, EducationRequirement
from app.entity.candidate_entity import Candidate
from app.entity.task_entity import Task

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"
    ARCHIVED = "archived"

class JobTournamentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class JobSkill(BaseModel):
    name: str
    years_of_experience: int
    weight: Optional[int] = None

class Requirements(BaseModel):
    certifications: Optional[List[str]] = None
    educations: Optional[List[EducationRequirement]] = None
    languages: Optional[List[Language]] = None

class Reasoning(BaseModel):
    reason: List[str]
    language: str

class TournamentCandidate(BaseModel):
    candidate: Link[Candidate]
    reasoning: Optional[List[Reasoning]] = None
    status: TournamentCandidateStatus
    wins: int
    rank: int

class JobTournament(BaseModel):
    status: JobTournamentStatus
    task: Link[Task]
    candidates: Optional[List[TournamentCandidate]] = None

class JobPosition(Document):
    status: JobStatus
    title: str
    original_text: str
    summary: str
    company: str
    city: Optional[str] = None
    country: Optional[str] = None
    employment_type: EmploymentType
    seniority_level: SeniorityLevel
    work_arrangement: WorkArrangement
    responsibilities: Optional[List[str]] = None
    recruiter_notes: Optional[str] = None
    salary: Optional[int] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    skills: Optional[List[JobSkill]] = None
    requirements: Optional[Requirements] = None
    tournament: JobTournament
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Settings:
        name = "job_positions"
        validate_on_save = True

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"JobPosition: {self.id}, {self.title}, {self.company}" 


