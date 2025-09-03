# Declare the entities that will be imported when importing the package

import logging
from typing import Any, List, Type

from common.entity.candidate_entity import CandidateDocument, ProcessingCandidate

# Only import entities that actually exist
db_entities: List[Type[Any]] = [CandidateDocument, ProcessingCandidate]
log = logging.getLogger(__name__)

# __all__ should be a list of strings, not a function
__all__ = ["CandidateDocument", "ProcessingCandidate", "db_entities"]


def get_db_entities() -> List[Type[Any]]:
    """Get the list of database entities."""
    log.info(f"Importing db entities names: {[entity.__name__ for entity in db_entities]}")
    return db_entities
