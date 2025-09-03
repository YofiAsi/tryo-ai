from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import UUID

from beanie import Document, Insert, Replace, Update, before_event
from pydantic import BaseModel, EmailStr, Field

from common.consts.enums import CandidateStatus, DegreeType, SeniorityLevel, WorkArrangement
from common.consts.models import Language


class PersonalInfo(BaseModel):
    name: str = Field(description="The full name of the candidate")
    gender: Optional[str] = Field(description="The gender of the candidate", pattern=r"^(Male|Female)$")
    year_of_birth: Optional[int] = Field(
        description="The year of birth of the candidate. If not mentioned, conclude from military service",
        ge=1950, le=2020
    )
    city: Optional[str] = Field(description="The city where the candidate lives")
    country: Optional[str] = Field(description="The country where the candidate lives")

class Education(BaseModel):
    school: Optional[str] = Field(None, description="The name of the educational institution")
    degree: Optional[DegreeType] = Field(None, description="The degree or qualification obtained")
    field_of_study: str = Field(description="Description of the education")
    start_year: Optional[int] = Field(None, description="The start year of the education")
    end_year: Optional[int] = Field(None, description="The end year of the education or null if still ongoing")
    grade: Optional[int] = Field(None, description="The grade or GPA obtained", ge=0, le=999)

class WorkExperience(BaseModel):
    company: str = Field(description="The name of the company")
    title: str = Field(description="The job title")
    industry: str = Field(description="The industry or domain of the company/project (e.g. Fintech, Cybersecurity, Education)")
    start_year: int = Field(description="The start year of the job", ge=1900, le=2025)
    end_year: int = Field(description="The end year of the job, 'present' if currently employed, or null if unknown",
        ge=1900,
        le=2025,
    )
    seniority_level: SeniorityLevel = Field(description="Seniority level of the person inferred from years of experience and job titles")
    description: str = Field(description="Description of the role and responsibilities")
    responsibilities: List[str] = Field(description="List of key responsibilities")
    skills: List[str] = Field(description="Technologies, languages, frameworks, etc. used in the role")

class Certification(BaseModel):
    name: str = Field(description="The name of the certification")
    issuer: str = Field(description="The issuing organization")
    year: Optional[int] = Field(None, description="The year when the certification was obtained", ge=1900, le=2025)
    description: Optional[str] = Field(None, description="Description of the certification")

class Skill(BaseModel):
    name: str = Field(description="The name of the skill")
    years_of_experience: int = Field(
        description="The total number of years the candidate has experience with the skill.",
        ge=0, le=99, pattern=r"^[0-9]{1,2}$"
    )

class Links(BaseModel):
    linkedin: Optional[str] = Field(None, description="The candidate's LinkedIn profile", pattern=r"^https://www\.linkedin\.com/in/[a-zA-Z0-9-]+$")
    github: Optional[str] = Field(None, description="The candidate's GitHub profile", pattern=r"^https://github\.com/[a-zA-Z0-9-]+$")
    portfolio: Optional[str] = Field(None, description="The candidate's portfolio website.")
    website: Optional[str] = Field(None, description="The candidate's personal website", pattern=r"^https://[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")

class Notes(BaseModel):
    salary_expectation: Optional[int] = Field(None, description="Expected salary range for the candidate in dollars", ge=0, le=1000000)
    work_region: Optional[List[str]] = Field(None, description="Preferred work regions or locations")
    position_preference: Optional[WorkArrangement] = Field(None, description="Preferred work arrangement (remote, hybrid, on-site)")
    notes: Optional[str] = Field(None, description="Additional notes about the candidate")

class CandidateDocument(Document):
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
    def before_update(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self) -> str:
        return f"Candidate: {self.candidate_id}, {self.name}, {self.title}" 

class ParsedCandidate(BaseModel):
    name: str = Field(description="The full name of the candidate")
    gender: Optional[str] = Field(
        None, 
        description="The gender of the candidate. If not mentioned, conclude from the name.", 
        pattern=r"^(Male|Female)$"
    )
    year_of_birth: Optional[int] = Field(
        None,
        description="The year of birth of the candidate. If not mentioned, conclude from military service ",
        ge=1950, le=2020
    )
    city: Optional[str] = Field(None, description="The city where the candidate lives. In English.")
    country: Optional[str] = Field(None, description="The country where the candidate lives. In English.")
    email: Optional[EmailStr] = Field(None, description="The candidate's email address")
    phone: Optional[str] = Field(
        None, 
        description="The candidate's phone number",
        pattern=r"^[0-9]{10}$"
    )
    title: str = Field(description="Professional title or headline")
    seniority_level: SeniorityLevel = Field(description="Seniority level of the person inferred from years of experience and job titles")
    education: List[Education] = Field([], description="List of educational background")
    work_experience: List[WorkExperience]= Field([], description="List of work experience")
    certifications: List[Certification] = Field([], description="List of certifications")
    skills: List[Skill] = Field([], description="List of skills and technologies acquired from the work experience")
    languages: List[Language] = Field([], description="List of speaking languages")
    keywords: List[str] = Field([], description="Keywords that describe the candidate. Conclude from the skills, work experience and projects")
    links: Links = Field(description="Social media and professional links")

    def __str__(self) -> str:
        return f"Candidate: {self.name}, {self.title}"

class ProcessingCandidate(Document):
    file_id: UUID = Field(description="The ID of the file that the candidate is being processed from")
    original_cv_minio_path: str = Field(description="The path to the original CV in Minio")
    txt_cv_minio_path: str = Field(description="The path to the txt CV in Minio")
    parsed_data: Optional[ParsedCandidate] = Field(None, description="The parsed candidate data, populated after parsing")
    status: Literal[
        "pending_parse",
        "parsing",
        "pending_skill_normalization",
        "normalizing_skills",
        "pending_vectorization",
        "vectorizing",
        "pending_finalization",
        "finalizing",
        "completed",
        "failed"
    ] = "pending_parse"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    errors: List[str] = Field(default_factory=list)

    class Settings:
        name = "candidates_processing"  # collection name
        validate_on_save = True

    @before_event(Update, Replace, Insert)
    def before_update(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        if self.parsed_data:
            return f"ProcessingCandidate: {self.parsed_data.name}, {self.parsed_data.title} (Status: {self.status})"
        return f"ProcessingCandidate: {self.file_id} (Status: {self.status})"

