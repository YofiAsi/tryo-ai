from datetime import datetime
from typing import List, Optional, Union
import uuid

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict
from app.entity.task_entity import TaskType, TaskStatus
from app.schema.base_dto import BaseModelJsonSerializable

class CVProcessingTaskDTO(BaseModelJsonSerializable):
    candidates_ids: List[uuid.UUID]

class CreateTaskDTO(BaseModelJsonSerializable):
    type: TaskType
    data: CVProcessingTaskDTO

class BaseTaskDTO(BaseModelJsonSerializable):
    id: PydanticObjectId
    type: TaskType
    status: TaskStatus
    progress_percentage: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TaskWithDataDTO(BaseTaskDTO):
    data: Union[CVProcessingTaskDTO, None]

class UpdateTaskStatusDTO(BaseModelJsonSerializable):
    status: TaskStatus
    progress_percentage: Optional[float] = None