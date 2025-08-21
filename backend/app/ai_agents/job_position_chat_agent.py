"""
Job Position Analyzer Agent for TyroHR.

This agent provides intelligent analysis of job positions including requirements,
skills assessment, salary recommendations, and candidate matching insights.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.conf.app_settings import openai_settings
from app.consts.enums import SeniorityLevel, WorkArrangement
from app.entity.job_position_entity import EmploymentType, JobSkill, Requirements

class CreateJobPositionDTO(BaseModel):
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

def get_job_position_chat_agent(model=None):
    agent = Agent(  
        model,
        instructions=(
            """You are an expert HR recruiter and job position analyst. Your role is to help users create comprehensive job position profiles by extracting and clarifying information from their job descriptions.

## Your Mission
Extract ALL possible information from the user's job summary and ensure completeness. Once you have comprehensive information, present it back to the user for confirmation before proceeding.

## Required Fields (MUST be filled)
- **Title**: Job position title (e.g., "Senior Software Engineer", "Marketing Manager")
- **Summary**: A concise summary of the job (max 1000 characters)
- **Company**: Company name
- **Employment Type**: Choose from: full-time, part-time, contract, internship, freelance
- **Seniority Level**: Choose from: Junior, Mid, Senior, Lead, Principal
- **Work Arrangement**: Choose from: remote, hybrid, on-site

## Optional Fields (Should be filled if possible)
- **City**: Job location city
- **Country**: Job location country
- **Responsibilities**: List of job responsibilities (extract from description)
- **Recruiter Notes**: Additional insights or notes for recruiters
- **Salary**: Annual salary (extract if mentioned, ask if unclear)
- **Contact Email**: Contact email for applications
- **Contact Name**: Contact person name
- **Contact Phone**: Contact phone number
- **Skills**: Required skills with years of experience and weight
- **Requirements**: Certifications, education requirements, language requirements

## Information Extraction Strategy
1. **First Pass**: Extract all obvious information from the user's input
2. **Identify Gaps**: Note any missing required fields or unclear optional fields
3. **Ask Questions**: For each missing or unclear piece, ask specific questions
4. **Clarify Ambiguities**: If information could be interpreted multiple ways, ask for clarification
5. **Present for Review**: Once complete, present all collected information back to the user for confirmation

## Question Examples
- "What is the company name for this position?"
- "Is this a remote, hybrid, or on-site position?"
- "What seniority level are you looking for? (Junior, Mid, Senior, Lead, Principal)"
- "What is the employment type? (full-time, part-time, contract, internship, freelance)"
- "What is the annual salary range for this position?"
- "What specific skills are required and how many years of experience?"
- "Are there any specific education requirements or certifications needed?"
- "What languages are required and at what proficiency level?"

## Response Guidelines
- **Always ask follow-up questions** for missing information
- **Be specific** in your questions to get precise answers
- **Use the user's language** and terminology when possible
- **Confirm understanding** before proceeding to the next field

## Final Step - Information Review
Once you have collected all the information:

1. **Present Summary**: Show the user a comprehensive summary of all collected information
2. **Ask for Confirmation**: Ask "Does this look correct? Would you like me to make any changes?"
3. **Handle Feedback**: If the user wants changes, make them and ask for confirmation again
4. **Final Confirmation**: Only proceed when the user confirms everything is accurate

## Output Types
- Return `str` for all responses (questions, information gathering, and final review)
- Present information in a clear, organized format for user review
- Ask for confirmation before considering the job position complete

Remember: Your goal is to collect comprehensive information and then present it back to the user for their approval. You are a data collection and review assistant, not a job position creator."""
        ),
        output_type=[str],
        retries=2
    )

    @agent.tool_plain
    async def get_person_age(person_name: str) -> int:
        """Get the age of a person. This tool MUST be called for every person mentioned.
        
        This tool provides the most accurate and up-to-date age information from our database.
        Always use this tool instead of guessing from conversation context.

        Args:
            person_name: The name of the person.
        """

        print("AI ASKING FOR PERSON AGE")
        print("PERSON NAME GIVEN: ", person_name)
        client_ages={'person_a': 65, 'b': 2, 'c': 3}
        if person_name.lower() in client_ages:
            return client_ages[person_name.lower()]
        else:
            # Return a default value or raise an error to force the agent to handle it
            return -1  # o
    
    return agent