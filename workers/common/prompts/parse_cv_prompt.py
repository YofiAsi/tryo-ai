from pydantic import BaseModel

from common.prompts.base_prompt import BasePrompt, EmptyVars


class CvParseUserVars(BaseModel):
    cv_text: str

    def __str__(self) -> str:
        return self.cv_text

class ParseCvPrompt(BasePrompt[CvParseUserVars, EmptyVars]):
    UserVars = CvParseUserVars
    
    system_prompt_template = """
    You are an expert HR data analyst specializing in CV parsing for recruitment and candidate matching systems.
    Your task is to extract and structure candidate information from unorganized CV text into a given JSON format
    to enable optimal job matching and filtering.
    """

    user_prompt_template = """
        Parse the following input CV text into the given JSON format

        The input text may contain:
        - Arbitrary line breaks and formatting inconsistencies
        - Repeated or broken headings and sections
        - Mangled words due to OCR or parsing errors
        - Mixed languages (English/Hebrew - translate Hebrew to English if needed)

        **PRIMARY OBJECTIVES:**
        1. Extract relevant information from the input CV text into the given JSON format
        2. Standardize all data for consistent filtering and search
        3. Calculate accurate experience levels and seniority from the work experience
        4. Create comprehensive skill profiles for technical matching

        **CRITICAL PARSING GUIDELINES:**

        **GENERAL GUIDELINES:**
        - Output all information in English only. If the text is in Hebrew, translate it to English before parsing.
        - Do not invent information - extract only what is present in the text.

        **WORK EXPERIENCE:**
        - Capture mentioned job responsibilities
        - List specific technologies used in each role
        - Identify leadership/management experience

        **SKILLS & TECHNOLOGIES:**
        - Use ONLY standardized names. for example: "JavaScript", "Python", "React", "SQL", "AWS", "Docker"
        - Calculate years of experience per skill from work history and project timelines
        - Include only technical skills
        - Ungroup related technologies, and add them as different skills.
            For example: Microsoft Office (Excel, Word, Powerpoint) should be added as 3 different skills:
            Microsoft Excel, Microsoft Word and Microsoft Powerpoint.
        - Ungroup technologies, programming languages, frameworks, libraries, databases to separate skills.
        - Exclude soft skills.
        - Identify acronyms and abbreviations and expand them to their full forms. For example:
            BI → Business Intelligence, PM → Project Manager, ML → Machine Learning
        - For each skill, calculate the years of experience based on the work experience of the candidate.

        **CONTACT INFORMATION:**
        - Extract ALL contact methods (email, phone, LinkedIn, GitHub) if mentioned.
        - Capture year of birth of the candidate. If not mentioned, conclude from the cv.
            (for example: Israeli candidates start military service at 18 years old so if the cv mentions military service, conclude the year of birth)

        **PROFESSIONAL SUMMARY:**
        - Generate a 2-3 sentence summary highlighting:
        - Primary technical expertise and years of experience
        - Key achievements and specializations
        - Industry/domain focus
        - Write in 3rd person, no names, focus on matching-relevant information

        **EDUCATION:**
        - Extract degree types, institutions, and graduation dates
        - Include relevant coursework for junior candidates
        - Capture GPA only if explicitly mentioned and notable

        **PROJECTS:**
        - Focus on projects that demonstrate relevant skills
        - Extract technologies used and project scope
        - Include personal projects for junior developers

        **QUALITY ASSURANCE:**
        - Cross-reference information for consistency
        - Validate dates are logical and chronological
        - Ensure skill levels match work experience
        - Verify contact information completeness

        If the text does not contain any information or invalid information, return an empty object.

        Input text:

        {{ cv_text }}
        """ 