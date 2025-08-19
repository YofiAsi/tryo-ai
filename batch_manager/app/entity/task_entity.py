from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from beanie import Document, Update, Replace, before_event
from pydantic import Field

from app.entity.batch_entity import Batch


class TaskStatus(str, Enum):
    """Task lifecycle status values"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Task type values"""
    CV_PROCESSING = "cv_processing"
    EMBEDDING = "embedding"
    TOURNAMENT = "tournament"


class Task(Document):
    """Entity representing a task that manages multiple OpenAI batches"""
    
    # Unique identifier for this task
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    task_type: TaskType
    
    # Status and progress
    status: TaskStatus = Field(default=TaskStatus.CREATED)
    
    # Batch management
    batch_ids: List[str] = Field(default_factory=list, description="List of associated batch IDs")
    
    # Progress tracking
    total_requests: int = Field(default=0, description="Total number of requests across all batches")
    completed_requests: int = Field(default=0, description="Number of completed requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    
    # Estimated tokens
    estimated_tokens: int = Field(default=0, description="Total number of tokens across all batches")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    
    # Error information
    errors: Optional[List[Dict[str, Any]]] = Field(default=None)
    
    class Settings:
        name = "tasks"
        validate_on_save = True
    
    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        return f"Task: {self.task_id}, Name: {self.name}, Status: {self.status.value}, Progress: {self.get_progress_percentage():.1f}%"
    
    @property
    def is_completed(self) -> bool:
        """Check if the task has completed processing"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if the task has failed"""
        return self.status == TaskStatus.FAILED
    
    @property
    def is_running(self) -> bool:
        """Check if the task is currently running"""
        return self.status == TaskStatus.RUNNING
    
    @property
    def is_terminal_state(self) -> bool:
        """Check if the task is in a terminal state (no further processing expected)"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def batch_count(self) -> int:
        """Get the number of batches associated with this task"""
        return len(self.batch_ids)
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage based on all batches"""
        if self.total_requests <= 0:
            return 0.0
        
        processed_requests = self.completed_requests + self.failed_requests
        return (processed_requests / self.total_requests) * 100.0
    
    def add_batch(self, batch: Batch) -> None:
        """Add a batch to this task"""
        self.batch_ids.append(batch.batch_id)
        self.total_requests += batch.total_requests
        self.completed_requests += batch.completed_requests
        self.failed_requests += batch.failed_requests

        self.estimated_tokens += batch.estimated_tokens
    
    def update_progress(self, total_requests: int, completed_requests: int, failed_requests: int) -> None:
        """Update progress counters based on batch status"""
        self.total_requests = total_requests
        self.completed_requests = completed_requests
        self.failed_requests = failed_requests
    
    def start(self) -> None:
        """Mark the task as started"""
        if self.status == TaskStatus.CREATED:
            self.status = TaskStatus.RUNNING
            self.started_at = datetime.now(timezone.utc)
    
    def complete(self) -> None:
        """Mark the task as completed"""
        if not self.is_terminal_state:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
    
    def fail(self, error: Optional[Dict[str, Any]] = None) -> None:
        """Mark the task as failed"""
        if not self.is_terminal_state:
            self.status = TaskStatus.FAILED
            self.failed_at = datetime.now(timezone.utc)
            if error:
                if self.errors is None:
                    self.errors = []
                self.errors.append(error)
    
    def cancel(self) -> None:
        """Mark the task as cancelled"""
        if not self.is_terminal_state:
            self.status = TaskStatus.CANCELLED
            self.cancelled_at = datetime.now(timezone.utc)
    
    def pause(self) -> None:
        """Pause the task"""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.PAUSED
    
    def resume(self) -> None:
        """Resume the task from paused state"""
        if self.status == TaskStatus.PAUSED:
            self.status = TaskStatus.RUNNING