from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime

    from app.entity.batch_entity import Batch, BatchStatus


class BatchDTO(BaseModel):
    """Response model for batch information"""

    id: str
    client_name: str
    openai_batch_id: Optional[str] = None
    task_id: Optional[str] = None

    endpoint: str
    completion_window: Optional[str] = None
    status: BatchStatus

    # File IDs
    input_file_id: Optional[str] = None
    output_file_id: Optional[str] = None
    error_file_id: Optional[str] = None

    # Progress information
    request_counts: Optional[Dict[str, int]] = None
    progress_percentage: Optional[float] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    openai_created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    # Error information
    errors: Optional[List[Dict[str, Any]]] = None

    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_entity(cls, batch: Batch) -> BatchDTO:
        """Create a BatchDTO instance from a Batch entity"""
        # Calculate request counts dictionary
        request_counts = None
        if batch.total_requests > 0:
            request_counts = {
                "total": batch.total_requests,
                "completed": batch.completed_requests,
                "failed": batch.failed_requests,
            }

        return cls(
            id=str(batch.id),
            client_name=batch.api_client_name or "",
            openai_batch_id=batch.openai_batch_id,
            task_id=batch.task_id,
            endpoint=batch.endpoint,
            completion_window=batch.completion_window,
            status=batch.status,
            input_file_id=batch.input_file_id,
            output_file_id=batch.output_file_id,
            error_file_id=batch.error_file_id,
            request_counts=request_counts,
            progress_percentage=batch.get_progress_percentage(),
            created_at=batch.created_at,
            updated_at=batch.updated_at,
            openai_created_at=batch.openai_created_at,
            expires_at=batch.expires_at,
            completed_at=batch.completed_at,
            failed_at=batch.failed_at,
            errors=batch.errors,
            metadata=batch.metadata,
        )


class BatchStatusDTO(BaseModel):
    """Response model for batch status information"""

    id: str
    openai_batch_id: Optional[str] = None
    status: BatchStatus
    progress_percentage: float
    request_counts: Optional[Dict[str, int]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    errors: Optional[Dict[str, Any]] = None


class BatchResultsDTO(BaseModel):
    """Response model for batch results"""

    id: str
    openai_batch_id: Optional[str] = None
    status: BatchStatus

    # Result files
    output_file_id: Optional[str] = None
    error_file_id: Optional[str] = None

    # Result data (if available)
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Processed results")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="Error details")

    # Summary statistics
    total_requests: Optional[int] = None
    completed_requests: Optional[int] = None
    failed_requests: Optional[int] = None

    completed_at: Optional[datetime] = None

