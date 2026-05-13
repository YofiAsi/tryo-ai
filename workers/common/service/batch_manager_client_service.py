"""
HTTP client service for communicating with tyro-batch-manager.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CreateBatchTaskRequest(BaseModel):
    """Request model for creating a batch task."""
    type: str
    metadata: Optional[Dict[str, Any]] = None


class BatchTaskResponse(BaseModel):
    """Response model for batch task information."""
    id: str
    batch_ids: List[str]
    total_requests: int
    completed_requests: int
    failed_requests: int
    progress_percentage: float
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None



class BatchManagerClientService:
    """HTTP client service for communicating with tyro-batch-manager."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the batch manager client.
        
        Args:
            base_url: Base URL of the batch manager service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> 'BatchManagerClientService':
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def create_batch_task(
        self, 
        task_type: str, 
        jsonl_file_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> BatchTaskResponse:
        """
        Create a new batch task by uploading a JSONL file.
        
        Args:
            task_type: Type of batch task (e.g., 'cv_parsing', 'embedding')
            jsonl_file_path: Path to the JSONL file to upload
            metadata: Optional metadata for the batch task
            
        Returns:
            BatchTaskResponse: Information about the created batch task
            
        Raises:
            httpx.HTTPError: If the HTTP request fails
            ValueError: If the file doesn't exist or is invalid
        """
        await self._ensure_client()
        
        file_path = Path(jsonl_file_path)
        if not file_path.exists():
            raise ValueError(f"File does not exist: {jsonl_file_path}")
        
        if not file_path.suffix == '.jsonl':
            raise ValueError(f"File must be a JSONL file: {jsonl_file_path}")
        
        # Prepare form data
        form_data = {
            "dto_form": json.dumps({
                "type": task_type,
                "metadata": metadata or {}
            })
        }
        
        try:
            with open(file_path, 'rb') as f:
                files = {"file": (file_path.name, f, "application/json")}
                
                logger.info(f"Creating batch task of type '{task_type}' with file: {file_path.name}")
                logger.debug(f"Form data: {form_data}")
                if self._client is None:
                    raise RuntimeError("Client not initialized")
                response = await self._client.post(
                    "/api/v1/manager/create",
                    data=form_data,
                    files=files
                )
                
                # Log response details before raising for status
                if response.status_code != 201:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully created batch task with ID: {result['id']}")
                return BatchTaskResponse(**result)
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to create batch task: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating batch task: {e}")
            raise
    
    async def get_batch_task(self, task_id: str) -> BatchTaskResponse:
        """
        Get information about a batch task by ID.
        
        Args:
            task_id: ID of the batch task
            
        Returns:
            BatchTaskResponse: Information about the batch task
            
        Raises:
            httpx.HTTPError: If the HTTP request fails
        """
        await self._ensure_client()
        
        try:
            logger.info(f"Getting batch task: {task_id}")
            if self._client is None:
                raise RuntimeError("Client not initialized")
            response = await self._client.get(f"/api/v1/manager/{task_id}")
            response.raise_for_status()
            
            result = response.json()
            return BatchTaskResponse(**result)
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get batch task {task_id}: {e}")
            raise
    