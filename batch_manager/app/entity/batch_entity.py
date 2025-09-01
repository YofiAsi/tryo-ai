from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from beanie import Document, PydanticObjectId, Replace, Update, before_event
from pydantic import Field

from app.consts.ai_models import AIModel

if TYPE_CHECKING:
    from openai.types.batch import Batch as OpenAiBatchDTO
    

class BatchStatus(str, Enum):
    """OpenAI Batch API status values"""

    PENDING_UPLOAD = "pending_upload"
    VALIDATING = "validating"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"

    # in terminal state
    TERMINAL_STATES = [COMPLETED, FAILED, EXPIRED, CANCELLED]


class Batch(Document):
    """Entity representing an OpenAI Batch API batch"""

    id: PydanticObjectId = Field(default_factory=PydanticObjectId)

    ai_model: AIModel
    task_id: PydanticObjectId
    files_collected: bool = Field(default=False)

    # OpenAI API key
    api_client_name: Optional[str] = Field(default=None)
    organization: Optional[str] = Field(default=None)
    project: Optional[str] = Field(default=None)

    # Estimated tokens
    estimated_tokens: int = Field(default=0)

    # OpenAI batch ID returned by the API
    openai_batch_id: Optional[str] = Field(default=None)

    # OpenAI file IDs
    input_file_id: Optional[str] = Field(default=None)
    output_file_id: Optional[str] = Field(default=None)
    error_file_id: Optional[str] = Field(default=None)

    # DB input file name
    db_input_file_name: Optional[str] = Field(default=None)
    db_output_file_name: Optional[str] = Field(default=None)
    db_error_file_name: Optional[str] = Field(default=None)

    # Batch configuration
    endpoint: Literal["/v1/responses", "/v1/chat/completions", "/v1/embeddings", "/v1/completions"] = Field(
        default="/v1/responses", description="The API endpoint for the batch"
    )
    completion_window: Optional[str] = Field(default="24h", description="Time window for completion")

    # Status and progress
    status: BatchStatus = Field(default=BatchStatus.PENDING_UPLOAD)

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
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    class Settings:
        name = "batches"
        validate_on_save = True

    @before_event(Update, Replace)
    def before_update(self) -> None:
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self) -> str:
        return f"Batch: {self.id}, OpenAI ID: {self.openai_batch_id}, Status: {self.status.value}"

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
        return self.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.EXPIRED, BatchStatus.CANCELLED]

    def get_progress_percentage(self) -> float:
        """Calculate progress percentage based on request counts"""
        if not self.total_requests:
            return 0.0

        return (self.completed_requests + self.failed_requests) / self.total_requests * 100.0

    def update_with_batch_dto(self, batch_dto: OpenAiBatchDTO) -> None:
        self.status = BatchStatus(batch_dto.status)

        self.expires_at = datetime.fromtimestamp(batch_dto.expires_at) if batch_dto.expires_at else None
        self.finalizing_at = datetime.fromtimestamp(batch_dto.finalizing_at) if batch_dto.finalizing_at else None
        self.completed_at = datetime.fromtimestamp(batch_dto.completed_at) if batch_dto.completed_at else None
        self.failed_at = datetime.fromtimestamp(batch_dto.failed_at) if batch_dto.failed_at else None
        self.expired_at = datetime.fromtimestamp(batch_dto.expired_at) if batch_dto.expired_at else None
        self.cancelling_at = datetime.fromtimestamp(batch_dto.cancelling_at) if batch_dto.cancelling_at else None
        self.cancelled_at = datetime.fromtimestamp(batch_dto.cancelled_at) if batch_dto.cancelled_at else None

        self.input_file_id = batch_dto.input_file_id if batch_dto.input_file_id else None
        self.output_file_id = batch_dto.output_file_id if batch_dto.output_file_id else None
        self.error_file_id = batch_dto.error_file_id if batch_dto.error_file_id else None

        self.completed_requests = batch_dto.request_counts.completed if batch_dto.request_counts else 0
        self.failed_requests = batch_dto.request_counts.failed if batch_dto.request_counts else 0

        if batch_dto.errors and batch_dto.errors.data:
            self.errors = [
                error.model_dump() if hasattr(error, "model_dump") else dict(error) for error in batch_dto.errors.data
            ]
        else:
            self.errors = []

        self.metadata = batch_dto.metadata

Batch.model_rebuild()
