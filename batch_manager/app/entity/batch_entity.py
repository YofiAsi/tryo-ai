from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
import uuid

from beanie import Document, Update, Replace, before_event
from pydantic import Field

from app.consts.ai_models import AIModel


class BatchStatus(str, Enum):
    """OpenAI Batch API status values"""
    VALIDATING = "validating"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"


class Batch(Document):
    """Entity representing an OpenAI Batch API batch"""
    
    # Unique identifier for this batch record
    batch_id: uuid.UUID = Field(default_factory=uuid.uuid4)

    api_key_id: Optional[str]
    task_id: Optional[str]
    ai_model: AIModel
    estimated_tokens: int = Field(default=0)
    
    # OpenAI batch ID returned by the API
    openai_batch_id: Optional[str] = Field(default=None)
    
    # OpenAI file IDs
    input_file_id: Optional[str] = Field(default=None)
    output_file_id: Optional[str] = Field(default=None)
    error_file_id: Optional[str] = Field(default=None)

    db_input_file_name: Optional[str] = Field(default=None)
    
    # Batch configuration
    endpoint: Optional[str] = Field(description="The API endpoint for the batch")
    completion_window: Optional[str] = Field(default="24h", description="Time window for completion")
    
    # Status and progress
    status: BatchStatus = Field(default=BatchStatus.VALIDATING)
    
    total_requests: int = Field(default=0)
    completed_requests: int = Field(default=0)
    failed_requests: int = Field(default=0)
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # OpenAI timestamps (when available)
    openai_created_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    finalizing_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    expired_at: Optional[datetime] = Field(default=None)
    cancelling_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    
    # Error information
    errors: Optional[Dict[str, Any]] = Field(default=None)
    
    class Settings:
        name = "batches"
        validate_on_save = True
    
    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        return f"Batch: {self.batch_id}, OpenAI ID: {self.openai_batch_id}, Status: {self.status.value}"
    
    @property
    def is_completed(self) -> bool:
        """Check if the batch has completed processing"""
        return self.status == BatchStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if the batch has failed"""
        return self.status == BatchStatus.FAILED
    
    @property
    def is_in_progress(self) -> bool:
        """Check if the batch is currently being processed"""
        return self.status in [BatchStatus.VALIDATING, BatchStatus.IN_PROGRESS, BatchStatus.FINALIZING]
    
    @property
    def is_terminal_state(self) -> bool:
        """Check if the batch is in a terminal state (no further processing expected)"""
        return self.status in [
            BatchStatus.COMPLETED,
            BatchStatus.FAILED,
            BatchStatus.EXPIRED,
            BatchStatus.CANCELLED
        ]
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage based on request counts"""
        if not self.total_requests:
            return 0.0
        
        return (self.completed_requests + self.failed_requests) / self.total_requests * 100.0