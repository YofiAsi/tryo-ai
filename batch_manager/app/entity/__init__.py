import logging

from app.entity.batch_entity import Batch
from app.entity.task_entity import Task

entities = [Batch, Task]
log = logging.getLogger(__name__)


def __all__():
    log.info(f"Importing entities names: {[entity.__name__ for entity in entities]}")
    return entities