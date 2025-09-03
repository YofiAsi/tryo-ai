from enum import Enum


class SeniorityLevel(str, Enum):
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"

class LanguageLevel(str, Enum):
    NATIVE = "native"
    FLUENT = "fluent"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BASIC = "basic"

class DegreeType(str, Enum):
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    DIPLOMA = "diploma"

class WorkArrangement(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"

class TournamentCandidateStatus(str, Enum):
    UNCHECKED = "unchecked"
    CHECKED = "checked"
    APPROVED = "approved"
    HIDDEN = "hidden"
    REJECTED = "rejected"
    INTERVIEWED = "interviewed"

class TaskType(str, Enum):
    CV_PARSING = "cv_parsing"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CandidateStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"