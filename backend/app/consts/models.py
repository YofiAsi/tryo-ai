from typing import List, Optional
from pydantic import BaseModel

from .enums import LanguageLevel, DegreeType

class Language(BaseModel):
    name: str
    level: LanguageLevel

class EducationRequirement(BaseModel):
    school: Optional[str] = None
    degree: Optional[DegreeType] = None
    field_of_study: str
