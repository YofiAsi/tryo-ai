import logging

from app.entity.batch_entity import Batch
from app.entity.batch_task_entity import BatchTask

entities = [Batch, BatchTask]
log = logging.getLogger(__name__)


def __all__():
    log.info(f"Importing entities names: {[entity.__name__ for entity in entities]}")
    return entities