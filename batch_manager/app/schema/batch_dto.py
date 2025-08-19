from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid

from app.entity.batch_entity import BatchStatus



class BatchDTO(BaseModel):
    """Response model for batch information"""
    
    batch_id: uuid.UUID
    openai_batch_id: Optional[str] = None
    api_key_id: str
    task_id: Optional[str] = None
    
    endpoint: str
    completion_window: str
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
    errors: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None


class BatchStatusDTO(BaseModel):
    """Response model for batch status information"""
    
    batch_id: uuid.UUID
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
    
    batch_id: uuid.UUID
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
