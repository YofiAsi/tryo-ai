from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import UUID

from beanie import Document, Insert, PydanticObjectId, Replace, Save, Update, before_event
from pydantic import BaseModel, EmailStr, Field

from common.consts.enums import CandidateStatus, DegreeType, Gender, SeniorityLevel, WorkArrangement
from common.consts.models import Language


class PersonalInfo(BaseModel):
    name: str = Field(description="The full name of the candidate")
    gender: Optional[Gender] = Field(description="The gender of the candidate")
    year_of_birth: Optional[int] = Field(
        description="The year of birth of the candidate. If not mentioned, conclude from military service",
        ge=1950, le=2020
    )
    city: Optional[str] = Field(description="The city where the candidate lives")
    country: Optional[str] = Field(description="The country where the candidate lives")

    def __str__(self) -> str:
        text = self.name
        if self.gender:
            text += f", {self.gender}"
        if self.year_of_birth:
            text += f", {self.year_of_birth}"
        if self.city:
            text += f", {self.city}"
        if self.country:
            text += f", {self.country}"
        return text

class Education(BaseModel):
    school: Optional[str] = Field(None, description="The name of the educational institution")
    degree: Optional[DegreeType] = Field(None, description="The degree or qualification obtained")
    field_of_study: str = Field(description="Description of the education")
    start_year: Optional[int] = Field(None, description="The start year of the education")
    end_year: Optional[int] = Field(None, description="The end year of the education or null if still ongoing")
    grade: Optional[int] = Field(None, description="The grade or GPA obtained", ge=0, le=999)

    def __str__(self) -> str:
        text = ""
        if self.degree:
            text += f"{self.degree.value} in "
        
        text += self.field_of_study
        
        if text:
            text += " - "
        
        if self.school:
            text += f"at {self.school}"
        
        if self.start_year:
            text += f" ({self.start_year}"
            if self.end_year:
                text += f"-{self.end_year}"
            text += ")"
        
        if self.grade:
            text += f", grade: {self.grade}"
        
        return text

class WorkExperience(BaseModel):
    company: str = Field(description="The name of the company")
    title: str = Field(description="The job title, exclued seniority level")
    industry: str = Field(description="The industry or domain of the company/project (e.g. Fintech, Cybersecurity, Education)")
    start_year: int = Field(description="The start year of the job", ge=1900, le=2025)
    end_year: int = Field(description="The end year of the job, -1 if currently employed",
        ge=-1,
        le=2025,
    )
    seniority_level: SeniorityLevel = Field(description="Seniority level of the person inferred from years of experience and job titles")
    description: str = Field(description="Description of the role and responsibilities")
    responsibilities: List[str] = Field(description="List of key responsibilities")
    skills: List[str] = Field(description="Technologies, languages, frameworks, etc. used in the role")

    def __str__(self) -> str:
        text = ""
        if self.seniority_level and self.seniority_level.value.lower() not in self.title.lower():
            text += f"{self.seniority_level.value} "
        
        text += self.title
        
        if text:
            text += " - "
        
        if self.company:
            text += f"{self.company}"
        
        if self.start_year:
            text += f" ({self.start_year}"
            if self.end_year != -1:
                text += f"-{self.end_year}"
            else:
                text += "-present)"
            text += ")"

        if self.description:
            text += f"\n{self.description}"
        
        if self.responsibilities:
            text += f"\nResponsibilities:\n{'\n'.join(self.responsibilities)}"

        if self.skills:
            text += f"\nSkills:\n{'\n'.join(self.skills)}"
        
        return text

class Certification(BaseModel):
    name: str = Field(description="The name of the certification")
    issuer: str = Field(description="The issuing organization")
    year: Optional[int] = Field(None, description="The year when the certification was obtained", ge=1900, le=2025)
    description: Optional[str] = Field(None, description="Description of the certification")

    def __str__(self) -> str:
        text = f"{self.name} by {self.issuer}"
        if self.year:
            text += f" ({self.year})"
        if self.description:
            text += f"\n{self.description}"
        return text

class Skill(BaseModel):
    name: str = Field(description="The name of the skill")
    years_of_experience: int = Field(
        description="The total number of years the candidate has experience with the skill.",
        ge=0
    )

    def __str__(self) -> str:
        text = f"{self.name} ({self.years_of_experience} years of experience)"

        return text

class Links(BaseModel):
    linkedin: Optional[str] = Field(None, description="The candidate's LinkedIn profile", pattern=r"^https://www\.linkedin\.com/in/[a-zA-Z0-9-]+$")
    github: Optional[str] = Field(None, description="The candidate's GitHub profile", pattern=r"^https://github\.com/[a-zA-Z0-9-]+$")
    portfolio: Optional[str] = Field(None, description="The candidate's portfolio website.")
    website: Optional[str] = Field(None, description="The candidate's personal website", pattern=r"^https://[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")

    def __str__(self) -> str:
        text = ""
        if self.linkedin:
            text += f"LinkedIn: {self.linkedin}\n"
        if self.github:
            text += f"GitHub: {self.github}\n"
        if self.portfolio:
            text += f"Portfolio: {self.portfolio}\n"
        if self.website:
            text += f"Website: {self.website}\n"
        return text

class Notes(BaseModel):
    salary_expectation: Optional[int] = Field(None, description="Expected salary range for the candidate in dollars", ge=0, le=1000000)
    work_region: Optional[List[str]] = Field(None, description="Preferred work regions or locations")
    position_preference: Optional[WorkArrangement] = Field(None, description="Preferred work arrangement (remote, hybrid, on-site)")
    notes: Optional[str] = Field(None, description="Additional notes about the candidate")

    def __str__(self) -> str:
        text = ""
        if self.salary_expectation:
            text += f"Salary expectation: {self.salary_expectation}\n"
        if self.work_region:
            text += f"Work region: {', '.join(self.work_region)}\n"
        if self.position_preference:
            text += f"Position preference: {self.position_preference}\n"
        if self.notes:
            text += f"Notes: {self.notes}\n"
        return text

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

class CandidateDocument(Document):
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
    def before_update(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    @property
    def work_experience_text(self) -> str:
        text = ""
        if self.work_experience:
            text += '\n\n'.join(f'{i+1}) {str(exp)}' for i,exp in enumerate(self.work_experience))
        return text

    @property
    def skills_text(self) -> str:
        text = ""
        if self.skills:
            text += '\n'.join(str(skill) for skill in self.skills)
        return text

    @property
    def general_text(self) -> str:
        text = ""
        if self.seniority_level and self.seniority_level.value.lower() not in self.title.lower():
            text += f"{self.seniority_level.value} "
        text += self.title

        if self.city:
            text += f"\n{self.city}"
        
        if self.country:
            text += f"{", " if self.city else ""}{self.country}"

        if self.work_experience:
            text += f"\n\nWork Experience:\n{self.work_experience_text}"
        
        if self.education:
            text += f"\n\nEducation:\n{'\n\n'.join(f'{i+1}) {str(edu)}' for i,edu in enumerate(self.education))}"
        
        if self.certifications:
            text += f"\n\nCertifications:\n{'\n\n'.join(f'{i+1}) {str(cert)}' for i,cert in enumerate(self.certifications))}"
        
        if self.skills:
            text += f"\n\nSkills:\n{self.skills_text}"
        
        if self.languages:
            text += f"\n\nLanguages:\n{'\n'.join(str(lang) for lang in self.languages)}"

        if str(self.notes):
            text += f"\n\nNotes:\n{str(self.notes)}"
        
        return text

class ParsedCandidate(BaseModel):
    name: str = Field(description="The full name of the candidate. In English.")
    gender: Optional[Gender] = Field(
        None, 
        description="The gender of the candidate. If not mentioned, conclude from the name.", 
    )
    year_of_birth: Optional[int] = Field(
        None,
        description="The year of birth of the candidate. If not mentioned, conclude from military service",
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
    title: str = Field(description="Professional title or headline. If not mentioned, conclude from the last work experience.")
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
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    file_id: UUID = Field(description="The ID of the file that the candidate is being processed from")
    original_cv_minio_path: str = Field(description="The path to the original CV in Minio")
    txt_cv_minio_path: str = Field(description="The path to the txt CV in Minio")
    parsed_data: Optional[ParsedCandidate] = Field(None, description="The parsed candidate data, populated after parsing")
    parse_model: Optional[str] = Field(None, description="The model that was used to parse the candidate")
    parse_batch_task_id: Optional[str] = Field(None, description="The ID of the batch task that is parsing the candidate")
    embed_batch_task_id: Optional[str] = Field(None, description="The ID of the batch task that is embedding the candidate")
    embeddings: Optional[Embeddings] = Field(None, description="The embeddings of the candidate")
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
    raw_cv: str = Field(description="The raw CV of the candidate")
    created_at: datetime | None = None
    updated_at: datetime | None = None
    errors: List[str] = Field(default_factory=list)

    class Settings:
        name = "candidates_processing"
        validate_on_save = True

    @before_event(Update, Replace, Insert)
    def before_update(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)
    
    @before_event(Save)
    def before_save(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)
        self.created_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        if self.parsed_data:
            return f"ProcessingCandidate: {self.parsed_data.name}, {self.parsed_data.title} (Status: {self.status})"
        return f"ProcessingCandidate: {self.file_id} (Status: {self.status})"

