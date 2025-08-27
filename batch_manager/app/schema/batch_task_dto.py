from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime

    from app.entity.batch_task_entity import BatchTask, BatchTaskStatus, BatchTaskType


class CreateBatchTaskDTO(BaseModel):
    """Request model for creating a new batch task"""

    type: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class BatchTaskDTO(BaseModel):
    """Response model for batch task information"""

    id: str
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
    def from_entity(cls, batch_task: BatchTask) -> BatchTaskDTO:
        return cls(
            id=str(batch_task.id),
            batch_ids=[str(batch_id) for batch_id in batch_task.batch_ids],
            total_requests=batch_task.total_requests,
            completed_requests=batch_task.completed_requests,
            failed_requests=batch_task.failed_requests,
            progress_percentage=batch_task.get_progress_percentage(),
            created_at=batch_task.created_at,
            updated_at=batch_task.updated_at,
            started_at=batch_task.started_at,
            completed_at=batch_task.completed_at,
            failed_at=batch_task.failed_at,
            cancelled_at=batch_task.cancelled_at,
            errors=batch_task.errors,
            metadata=batch_task.metadata,
        )


class BatchTaskStatusDTO(BaseModel):
    """Response model for batch task status information"""

    id: str
    task_type: BatchTaskType
    status: BatchTaskStatus
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


