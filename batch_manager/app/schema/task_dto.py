from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid

from app.entity.task_entity import TaskStatus, TaskType, Task
from app.consts.ai_models import AIModel


class CreateTaskDTO(BaseModel):
    """Request model for creating a new task"""
    type: TaskType
    multitask: bool = Field(default=False, description="Should split to several tasks (will process each batch separately)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class TaskDTO(BaseModel):
    """Response model for task information"""
    
    task_id: uuid.UUID
    batch_ids: List[str]
    
    total_requests: int
    
    completed_requests: int
    failed_requests: int
    progress_percentage: float
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Error information
    errors: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_entity(cls, task: Task) -> "TaskDTO":
        return cls(
            task_id=task.task_id,
            batch_ids=task.batch_ids,
            total_requests=task.total_requests,
            completed_requests=task.completed_requests,
            failed_requests=task.failed_requests,
            progress_percentage=task.get_progress_percentage(),
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            failed_at=task.failed_at,
            cancelled_at=task.cancelled_at,
            errors=task.errors,
            metadata=task.metadata,
        )


class CreateTaskResponseDTO(BaseModel):
    tasks: List[TaskDTO]


class TaskStatusDTO(BaseModel):
    """Response model for task status information"""
    
    task_id: uuid.UUID
    name: str
    status: TaskStatus
    progress_percentage: float
    
    # Progress details
    total_requests: int
    completed_requests: int
    failed_requests: int
    batch_count: int
    
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
