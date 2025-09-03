from typing import Optional

from pydantic import BaseModel

from .enums import DegreeType, LanguageLevel


class Language(BaseModel):
    name: str
    level: LanguageLevel

class EducationRequirement(BaseModel):
    school: Optional[str] = None
    degree: Optional[DegreeType] = None
    field_of_study: str
