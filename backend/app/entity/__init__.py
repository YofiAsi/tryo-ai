# Declare the entities that will be imported when importing the package

import logging

from app.entity.user_entity import User
from app.entity.candidate_entity import Candidate
from app.entity.job_position_entity import JobPosition
from app.entity.task_entity import Task 
from app.entity.activity_log_entity import ActivityLog

db_entities = [User, Candidate, JobPosition, Task, ActivityLog]
log = logging.getLogger(__name__)


def __all__():
    log.info(f"Importing db entities names: {[entity.__name__ for entity in db_entities]}")
    return db_entities
