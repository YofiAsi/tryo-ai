"""
File Storage Repository for handling MinIO operations with OpenAI Batch API files.

This repository manages the storage of batch input files, output results, and error files
in MinIO object storage, following OpenAI Batch API patterns.
"""

import logging
import io
import uuid
from typing import Optional, BinaryIO, Union, Any
from pathlib import Path
from datetime import datetime, timezone, timedelta
import os
from dataclasses import dataclass

from minio import Minio
from minio.error import S3Error
from pydantic_settings import BaseSettings

_log = logging.getLogger(__name__)


class MinIOSettings(BaseSettings):
    """MinIO configuration settings"""
    
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT") or ""
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY") or ""
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY") or ""
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE") == "true"
    MINIO_BATCH_BUCKET: str = os.getenv("MINIO_BATCH_BUCKET") or ""
    MINIO_REGION: str = os.getenv("MINIO_REGION") or ""
    
    class Config:
        env_prefix = "MINIO_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@dataclass
class FileMetadata:
    """Metadata for stored files"""
    content_type: str
    size: int
    batch_id: str
    file_type: str
    created_at: datetime
    minio_object_name: str


class FileStorageRepository:
    """Repository for handling file storage operations with MinIO"""
    
    def __init__(self, settings: Optional[MinIOSettings] = None):
        """Initialize the file storage repository
        
        Args:
            settings: MinIO configuration settings. If None, loads from environment.
        """
        self.settings: MinIOSettings = settings or MinIOSettings()
        self._client: Optional[Minio] = None
        self._ensure_bucket_exists()
    
    @property
    def client(self) -> Minio:
        """Get MinIO client instance (lazy initialization)"""
        if self._client is None:
            self._client = Minio(
                endpoint=self.settings.MINIO_ENDPOINT,
                access_key=self.settings.MINIO_ACCESS_KEY,
                secret_key=self.settings.MINIO_SECRET_KEY,
                secure=self.settings.MINIO_SECURE,
                region=self.settings.MINIO_REGION
            )
            _log.debug(f"MinIO client initialized for endpoint: {self.settings.MINIO_ENDPOINT}")
        return self._client
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the batch files bucket exists"""
        try:
            if not self.client.bucket_exists(self.settings.MINIO_BATCH_BUCKET):
                self.client.make_bucket(self.settings.MINIO_BATCH_BUCKET, location=self.settings.MINIO_REGION)
                _log.info(f"Created bucket: {self.settings.MINIO_BATCH_BUCKET}")
            else:
                _log.debug(f"Bucket exists: {self.settings.MINIO_BATCH_BUCKET}")
        except S3Error as e:
            _log.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def _generate_object_name(self, batch_id: str, file_type: str, file_extension: str = "jsonl") -> str:
        """Generate a unique object name for the file
        
        Args:
            batch_id: The batch identifier
            file_type: Type of file ('input', 'output', 'error')
            file_extension: File extension (default: 'jsonl')
            
        Returns:
            Generated object name
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{batch_id}/{file_type}/{timestamp}_{unique_id}.{file_extension}"
    
    def upload_batch_input_file(
        self,
        batch_id: str,
        file_data: Union[bytes, BinaryIO, str],
        content_type: str = "application/jsonl"
    ) -> FileMetadata:
        """Upload a batch input file to MinIO
        
        Args:
            batch_id: Unique identifier for the batch
            file_data: File data as bytes, file-like object, or file path
            content_type: MIME type of the file
            
        Returns:
            FileMetadata object with upload information
            
        Raises:
            S3Error: If upload fails
        """
        object_name = self._generate_object_name(batch_id, "input", "jsonl")
        
        try:
            # Handle different input types
            if isinstance(file_data, str):
                # File path
                file_path = Path(file_data)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_data}")
                
                file_size = file_path.stat().st_size
                self.client.fput_object(
                    bucket_name=self.settings.MINIO_BATCH_BUCKET,
                    object_name=object_name,
                    file_path=str(file_path),
                    content_type=content_type
                )
                
            elif isinstance(file_data, bytes):
                # Bytes data
                file_size = len(file_data)
                data_stream = io.BytesIO(file_data)
                self.client.put_object(
                    bucket_name=self.settings.MINIO_BATCH_BUCKET,
                    object_name=object_name,
                    data=data_stream,
                    length=file_size,
                    content_type=content_type
                )
                
            else:
                # File-like object
                file_data.seek(0, 2)  # Seek to end
                file_size = file_data.tell()
                file_data.seek(0)  # Reset to beginning
                
                self.client.put_object(
                    bucket_name=self.settings.MINIO_BATCH_BUCKET,
                    object_name=object_name,
                    data=file_data,
                    length=file_size,
                    content_type=content_type
                )
            
            _log.info(f"Uploaded batch input file: {object_name} ({file_size} bytes)")
            
            return FileMetadata(
                content_type=content_type,
                size=file_size,
                batch_id=batch_id,
                file_type="input",
                created_at=datetime.now(timezone.utc),
                minio_object_name=object_name
            )
            
        except S3Error as e:
            _log.error(f"Failed to upload batch input file: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error uploading file: {e}")
            raise

    def download_batch_input_to_tmp_file(
        self,
        object_name: str,
        tmp_file_path: str
    ) -> str:
        """Download a batch input file from MinIO
        
        Args:
            object_name: Object name in MinIO
            destination_path: Path to save the file
        Returns:
            Path to the downloaded file
            
        Raises:
            S3Error: If download fails
        """
        try:
            self.client.fget_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name,
                file_path=tmp_file_path,
            )
            
            _log.info(f"Downloaded batch input file: {object_name} to {tmp_file_path}")
            return tmp_file_path
            
        except S3Error as e:
            _log.error(f"Failed to download batch input file: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error downloading file: {e}")
            raise

    def download_batch_output_file(
        self,
        object_name: str
    ) -> bytes:
        """Download a batch output file from MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            File content as bytes
            
        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name
            )
            
            data = response.read()
            response.close()
            response.release_conn()
            
            _log.info(f"Downloaded batch output file: {object_name} ({len(data)} bytes)")
            return data
            
        except S3Error as e:
            _log.error(f"Failed to download batch output file: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error downloading file: {e}")
            raise
    
    def download_batch_error_file(
        self,
        object_name: str
    ) -> bytes:
        """Download a batch error file from MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            File content as bytes
            
        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name
            )
            
            data = response.read()
            response.close()
            response.release_conn()
            
            _log.info(f"Downloaded batch error file: {object_name} ({len(data)} bytes)")
            return data
            
        except S3Error as e:
            _log.error(f"Failed to download batch error file: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error downloading file: {e}")
            raise
    
    def store_batch_results(
        self,
        batch_id: str,
        results_data: bytes,
        content_type: str = "application/jsonl"
    ) -> FileMetadata:
        """Store batch processing results in MinIO
        
        Args:
            batch_id: Unique identifier for the batch
            results_data: Results data as bytes
            content_type: MIME type of the results
            
        Returns:
            FileMetadata object with storage information
            
        Raises:
            S3Error: If storage fails
        """
        object_name = self._generate_object_name(batch_id, "output", "jsonl")
        
        try:
            data_stream = io.BytesIO(results_data)
            file_size = len(results_data)
            
            self.client.put_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name,
                data=data_stream,
                length=file_size,
                content_type=content_type
            )
            
            _log.info(f"Stored batch results: {object_name} ({file_size} bytes)")
            
            return FileMetadata(
                content_type=content_type,
                size=file_size,
                batch_id=batch_id,
                file_type="output",
                created_at=datetime.now(timezone.utc),
                minio_object_name=object_name
            )
            
        except S3Error as e:
            _log.error(f"Failed to store batch results: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error storing results: {e}")
            raise
    
    def store_batch_errors(
        self,
        batch_id: str,
        error_data: bytes,
        content_type: str = "application/jsonl"
    ) -> FileMetadata:
        """Store batch processing errors in MinIO
        
        Args:
            batch_id: Unique identifier for the batch
            error_data: Error data as bytes
            content_type: MIME type of the error data
            
        Returns:
            FileMetadata object with storage information
            
        Raises:
            S3Error: If storage fails
        """
        object_name = self._generate_object_name(batch_id, "error", "jsonl")
        
        try:
            data_stream = io.BytesIO(error_data)
            file_size = len(error_data)
            
            self.client.put_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name,
                data=data_stream,
                length=file_size,
                content_type=content_type
            )
            
            _log.info(f"Stored batch errors: {object_name} ({file_size} bytes)")
            
            return FileMetadata(
                content_type=content_type,
                size=file_size,
                batch_id=batch_id,
                file_type="error",
                created_at=datetime.now(timezone.utc),
                minio_object_name=object_name
            )
            
        except S3Error as e:
            _log.error(f"Failed to store batch errors: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error storing errors: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """Delete a file from MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self.client.remove_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name
            )
            
            _log.info(f"Deleted file: {object_name}")
            return True
            
        except S3Error as e:
            _log.error(f"Failed to delete file {object_name}: {e}")
            return False
        except Exception as e:
            _log.error(f"Unexpected error deleting file {object_name}: {e}")
            return False
    
    def cleanup_batch_files(self, batch_id: str) -> bool:
        """Clean up all files associated with a batch
        
        Args:
            batch_id: Unique identifier for the batch
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            # List all objects with the batch prefix
            prefix = f"{batch_id}/"
            objects = self.client.list_objects(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                prefix=prefix,
                recursive=True
            )
            
            deleted_count = 0
            for obj in objects:
                if obj.object_name is None:
                    continue
                try:
                    self.client.remove_object(
                        bucket_name=self.settings.MINIO_BATCH_BUCKET,
                        object_name=obj.object_name
                    )
                    deleted_count += 1
                except S3Error as e:
                    _log.warning(f"Failed to delete {obj.object_name}: {e}")
            
            _log.info(f"Cleaned up {deleted_count} files for batch {batch_id}")
            return True
            
        except S3Error as e:
            _log.error(f"Failed to cleanup batch files for {batch_id}: {e}")
            return False
        except Exception as e:
            _log.error(f"Unexpected error cleaning up batch files for {batch_id}: {e}")
            return False
    
    def get_file_info(self, object_name: str) -> Optional[dict[str, Any]]:
        """Get information about a file in MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            stat = self.client.stat_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name
            )
            
            return {
                "object_name": stat.object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "metadata": stat.metadata
            }
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            _log.error(f"Failed to get file info for {object_name}: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error getting file info for {object_name}: {e}")
            raise
    
    def list_batch_files(self, batch_id: str) -> list[dict[str, Any]]:
        """List all files associated with a batch
        
        Args:
            batch_id: Unique identifier for the batch
            
        Returns:
            List of dictionaries with file information
        """
        try:
            prefix = f"{batch_id}/"
            objects = self.client.list_objects(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                files.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            
            _log.debug(f"Found {len(files)} files for batch {batch_id}")
            return files
            
        except S3Error as e:
            _log.error(f"Failed to list batch files for {batch_id}: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error listing batch files for {batch_id}: {e}")
            raise
    
    def get_presigned_download_url(
        self,
        object_name: str,
        expires_in_seconds: int = 3600
    ) -> str:
        """Generate a presigned URL for downloading a file
        
        Args:
            object_name: Object name in MinIO
            expires_in_seconds: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned download URL
            
        Raises:
            S3Error: If URL generation fails
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.settings.MINIO_BATCH_BUCKET,
                object_name=object_name,
                expires=timedelta(seconds=expires_in_seconds)
            )
            
            _log.debug(f"Generated presigned URL for {object_name}")
            return url
            
        except S3Error as e:
            _log.error(f"Failed to generate presigned URL for {object_name}: {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error generating presigned URL for {object_name}: {e}")
            raise
