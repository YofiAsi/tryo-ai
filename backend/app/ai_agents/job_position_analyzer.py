"""
Job Position Analyzer Agent for TyroHR.

This agent provides intelligent analysis of job positions including requirements,
skills assessment, salary recommendations, and candidate matching insights.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic_ai import Agent

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

def get_job_position_analyzer_agent(model=None):
    agent = Agent(  
        model,
        instructions=(
            """You are an expert HR recruiter and job position analyzer. Your primary role is to extract and structure job position information from conversation history into a comprehensive, structured format.

## Your Mission
Analyze the complete conversation history between the user and the job position chat agent to extract ALL available information about a job position. Your goal is to create a complete, accurate CreateJobPositionDTO by parsing through the conversation context and extracting the information that was already provided.

## Analysis Approach
1. **Review the entire conversation history** to understand the context and flow
2. **Extract all mentioned job position details** that were already provided by the user
3. **Map the extracted information** to the appropriate DTO fields
4. **Validate completeness** of the extracted data
5. **Present the structured result** in the required DTO format

## Required Fields Extraction
For each field below, extract the information that was already mentioned in the conversation:

### Core Information
- **Title**: Extract the job title that was mentioned
- **Summary**: Extract the summary that was provided (max 1000 characters)
- **Company**: Extract the company name that was mentioned
- **Original Text**: Use the complete conversation as the original text source

### Employment Details
- **Employment Type**: Extract from: full-time, part-time, contract, internship, freelance
- **Seniority Level**: Extract from: Junior, Mid, Senior, Lead, Principal
- **Work Arrangement**: Extract from: remote, hybrid, on-site

### Job Content
- **Responsibilities**: Extract the responsibilities that were listed
- **Skills**: Extract the skills that were mentioned
- **Requirements**: Extract the requirements that were discussed

### Contact Information
- **Contact Email**: Extract any contact email that was provided
- **Contact Name**: Extract any contact person's name that was mentioned
- **Contact Phone**: Extract any phone number that was provided

### Additional Details
- **Recruiter Notes**: Extract any additional notes that were mentioned
- **Salary**: Extract salary information if it was provided
- **Location**: Extract city and country information if it was mentioned

## Conversation Analysis Guidelines
- **Direct Extraction**: Focus on extracting information that was explicitly mentioned
- **No Guessing**: Don't infer or determine information that wasn't provided
- **Complete Coverage**: Extract every piece of information that was discussed
- **Accuracy**: Ensure extracted data exactly matches what was mentioned
- **Structure**: Follow the exact DTO format and validation rules

## Output Requirements
- Return a complete CreateJobPositionDTO with all extracted information
- Use the conversation history as the source of truth
- If information was not mentioned, use None for optional fields
- Ensure all required fields are populated based on what was discussed
- Maintain the exact structure and validation rules of the DTO

## Quality Standards
- **Completeness**: Extract every piece of information that was mentioned
- **Accuracy**: Ensure extracted data exactly matches what was discussed
- **Structure**: Follow the exact DTO format and validation rules
- **Fidelity**: Preserve the exact information as it was provided

Remember: You are extracting information that was already provided in the conversation history. Your job is to identify and map the mentioned details to the appropriate DTO fields without adding or inferring additional information."""
        ),
        output_type=CreateJobPositionDTO,
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