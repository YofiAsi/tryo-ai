from datetime import datetime, timezone
from typing import Optional
import uuid

from beanie import Document, Update, Replace, before_event
from pydantic import Field

from app.consts.enums import TaskType, TaskStatus
from app.schema.tasks_dto import CVProcessingTaskDTO


class Task(Document):
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: TaskType
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress_percentage: Optional[float] = Field(default=0.0)
    data: CVProcessingTaskDTO
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tasks"
        validate_on_save = True

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"Task: {self.task_id}, {self.type.value}, {self.status.value}, {self.progress_percentage}%" 