"""
Minio Repository for handling MinIO operations with cv-txt-files bucket.

This repository manages the retrieval of files from directories in the cv-txt-files bucket.
It provides functionality to list and download files based on directory prefixes.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generator, Iterator, List, Optional

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
    MINIO_CANDIDATE_IMPORT_BUCKET: str = os.getenv("MINIO_CANDIDATE_IMPORT_BUCKET") or "candidate-import"
    MINIO_CANDIDATE_FILES_BUCKET: str = os.getenv("MINIO_CANDIDATE_FILES_BUCKET") or "candidate-files"
    MINIO_REGION: str = os.getenv("MINIO_REGION") or ""
    
    class Config:
        env_prefix = "MINIO_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@dataclass
class FileInfo:
    """Information about a file in MinIO"""
    object_name: str
    size: int
    last_modified: datetime
    etag: str
    content_type: Optional[str] = None


class MinioRepository:
    """Repository for handling MinIO operations"""
    
    def __init__(self, settings: Optional[MinIOSettings] = None):
        """Initialize the MinIO repository
        
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
        """Ensure all buckets exist"""
        buckets = [
            self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
            self.settings.MINIO_CANDIDATE_FILES_BUCKET
        ]
        
        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name, location=self.settings.MINIO_REGION)
                    _log.info(f"Created bucket: {bucket_name}")
                else:
                    _log.debug(f"Bucket exists: {bucket_name}")
            except S3Error as e:
                _log.error(f"Error ensuring bucket '{bucket_name}' exists: {e}")
                raise
    
    def list_files_in_import_directory(self, directory: str) -> List[FileInfo]:
        """List all files in a specific directory within the candidate-import bucket
        
        Args:
            directory: Directory name (e.g., "test" will list files in /test/)
            
        Returns:
            List of FileInfo objects for files in the directory
            
        Raises:
            S3Error: If listing fails
        """
        try:
            # Ensure directory has trailing slash for proper prefix matching
            prefix = directory.rstrip('/') + '/' if directory else ''
            
            objects = self.client.list_objects(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                if obj.object_name is None:
                    continue
                    
                # Skip directory entries (objects ending with /)
                if obj.object_name.endswith('/'):
                    continue
                
                files.append(FileInfo(
                    object_name=obj.object_name,
                    size=obj.size or 0,
                    last_modified=obj.last_modified or datetime.now(),
                    etag=obj.etag or "",
                    content_type=None  # Not available in list_objects
                ))
            
            _log.info(f"Found {len(files)} files in directory '{directory}'")
            return files
            
        except S3Error as e:
            _log.error(f"Failed to list files in directory '{directory}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error listing files in directory '{directory}': {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """Download a file from the candidate-import bucket
        
        Args:
            object_name: Object name in MinIO (full path including directory)
            
        Returns:
            File content as bytes
            
        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
                object_name=object_name
            )
            
            data = response.read()
            response.close()
            response.release_conn()
            
            _log.info(f"Downloaded file: {object_name} ({len(data)} bytes)")
            return data
            
        except S3Error as e:
            _log.error(f"Failed to download file '{object_name}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error downloading file '{object_name}': {e}")
            raise
    
    def download_file_to_path(self, object_name: str, file_path: str) -> str:
        """Download a file from the candidate-import bucket to a local path
        
        Args:
            object_name: Object name in MinIO (full path including directory)
            file_path: Local file path to save the file
            
        Returns:
            Path to the downloaded file
            
        Raises:
            S3Error: If download fails
        """
        try:
            self.client.fget_object(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
                object_name=object_name,
                file_path=file_path,
            )
            
            _log.info(f"Downloaded file: {object_name} to {file_path}")
            return file_path
            
        except S3Error as e:
            _log.error(f"Failed to download file '{object_name}' to '{file_path}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error downloading file '{object_name}' to '{file_path}': {e}")
            raise
    
    def get_file_info(self, object_name: str) -> Optional[dict[str, Any]]:
        """Get information about a file in the candidate-import bucket
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            stat = self.client.stat_object(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
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
            _log.error(f"Failed to get file info for '{object_name}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error getting file info for '{object_name}': {e}")
            raise
    
    def file_exists(self, object_name: str) -> bool:
        """Check if a file exists in the candidate-import bucket
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
                object_name=object_name
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            _log.error(f"Error checking if file exists '{object_name}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error checking if file exists '{object_name}': {e}")
            raise
    
    def iterate_files_in_import_directory(self, directory: str) -> Generator[FileInfo, None, None]:
        """Iterate over files in a specific directory within the candidate-import bucket
        
        Args:
            directory: Directory name (e.g., "test" will list files in /test/)
            
        Yields:
            FileInfo objects for files in the directory
            
        Raises:
            S3Error: If listing fails
        """
        try:
            # Ensure directory has trailing slash for proper prefix matching
            prefix = directory.rstrip('/') + '/' if directory else ''
            
            objects = self.client.list_objects(
                bucket_name=self.settings.MINIO_CANDIDATE_IMPORT_BUCKET,
                prefix=prefix,
                recursive=True
            )
            
            for obj in objects:
                if obj.object_name is None:
                    continue
                    
                # Skip directory entries (objects ending with /)
                if obj.object_name.endswith('/'):
                    continue
                
                yield FileInfo(
                    object_name=obj.object_name,
                    size=obj.size or 0,
                    last_modified=obj.last_modified or datetime.now(),
                    etag=obj.etag or "",
                    content_type=None  # Not available in list_objects
                )
            
        except S3Error as e:
            _log.error(f"Failed to iterate files in directory '{directory}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error iterating files in directory '{directory}': {e}")
            raise
    
    def list_files_in_directory(self, directory: str, bucket_name: str) -> List[str]:
        """List all files in a specific directory within the specified bucket
        
        Args:
            directory: Directory name (e.g., "test" will list files in /test/)
            bucket_name: Name of the bucket to list files from
            
        Returns:
            List of file paths (object names) in the directory
            
        Raises:
            S3Error: If listing fails
        """
        try:
            # Ensure directory has trailing slash for proper prefix matching
            prefix = directory.rstrip('/') + '/' if directory else ''
            
            objects = self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                if obj.object_name is None:
                    continue
                    
                # Skip directory entries (objects ending with /)
                if obj.object_name.endswith('/'):
                    continue
                
                files.append(obj.object_name)
            
            _log.info(f"Found {len(files)} files in directory '{directory}' in bucket '{bucket_name}'")
            return files
            
        except S3Error as e:
            _log.error(f"Failed to list files in directory '{directory}' in bucket '{bucket_name}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error listing files in directory '{directory}' in bucket '{bucket_name}': {e}")
            raise
    
    def stream_file(self, file_path: str, bucket_name: str) -> Iterator[bytes]:
        """Stream a file line by line from the specified bucket
        
        Args:
            file_path: Path to the file in MinIO (full path including directory)
            bucket_name: Name of the bucket containing the file
            
        Yields:
            Individual lines from the file as bytes
            
        Raises:
            S3Error: If streaming fails
        """
        try:
            response = self.client.get_object(
                bucket_name=bucket_name,
                object_name=file_path
            )
            
            try:
                # Stream the file line by line
                buffer = b""
                for chunk in response.stream(32 * 1024):  # 32KB chunks
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        yield line + b'\n'
                
                # Yield any remaining content
                if buffer:
                    yield buffer
                    
            finally:
                response.close()
                response.release_conn()
            
            _log.debug(f"Successfully streamed file: {file_path} from bucket '{bucket_name}'")
            
        except S3Error as e:
            _log.error(f"Failed to stream file '{file_path}' from bucket '{bucket_name}': {e}")
            raise
        except Exception as e:
            _log.error(f"Unexpected error streaming file '{file_path}' from bucket '{bucket_name}': {e}")
            raise