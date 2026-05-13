"""
MinIO directory structure utilities for handling CV processing pipeline directories.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class MinioDirectoryStructure(BaseModel):
    """
    Represents the directory structure for CV processing pipeline in MinIO.
    
    Expected structure:
    base_directory/
    ├── original/     # Original CV files (PDF, DOC, etc.)
    └── extracted/    # Extracted text files (.txt)
    """
    
    base_directory: str = Field(description="Base directory path in MinIO bucket")
    original_subdir: str = Field(default="original", description="Subdirectory for original CV files")
    extracted_subdir: str = Field(default="extracted", description="Subdirectory for extracted text files")
    
    @field_validator('base_directory')
    @classmethod
    def validate_base_directory(cls, v: str) -> str:
        """Validate base directory format."""
        if not v or v.isspace():
            raise ValueError("Base directory cannot be empty or whitespace")
        
        # Remove leading/trailing slashes for consistency
        return v.strip().strip('/')
    
    @field_validator('original_subdir', 'extracted_subdir')
    @classmethod
    def validate_subdirs(cls, v: str) -> str:
        """Validate subdirectory names."""
        if not v or v.isspace():
            raise ValueError("Subdirectory names cannot be empty or whitespace")
        
        # Remove leading/trailing slashes for consistency
        return v.strip().strip('/')
    
    @property
    def original_directory(self) -> str:
        """Get the full path to the original files directory."""
        return f"{self.base_directory}/{self.original_subdir}"
    
    @property
    def extracted_directory(self) -> str:
        """Get the full path to the extracted files directory."""
        return f"{self.base_directory}/{self.extracted_subdir}"
    
    def get_original_file_path(self, filename: str) -> str:
        """
        Get the full MinIO path for an original file.
        
        Args:
            filename: Name of the original file
            
        Returns:
            Full MinIO path to the original file
        """
        return f"{self.original_directory}/{filename}"
    
    def get_extracted_file_path(self, filename: str) -> str:
        """
        Get the full MinIO path for an extracted file.
        
        Args:
            filename: Name of the extracted file (should end with .txt)
            
        Returns:
            Full MinIO path to the extracted file
        """
        return f"{self.extracted_directory}/{filename}"
    
    def extract_candidate_id_from_filename(self, filepath: str) -> str:
        """
        Extract candidate ID from a file path.
        
        Args:
            filepath: Full file path in MinIO
            
        Returns:
            Candidate ID (filename without directory path and extension)
        """
        return Path(filepath).stem
    
    def get_corresponding_original_path(self, extracted_filepath: str) -> str:
        """
        Get the corresponding original file path for an extracted file.
        
        Args:
            extracted_filepath: Path to the extracted .txt file
            
        Returns:
            Corresponding path in the original directory
        """
        filename = Path(extracted_filepath).name

        return self.get_original_file_path(filename)
    
    def get_corresponding_extracted_path(self, original_filepath: str) -> str:
        """
        Get the corresponding extracted file path for an original file.
        
        Args:
            original_filepath: Path to the original file
            
        Returns:
            Corresponding path in the extracted directory with .txt extension
        """
        base_name = Path(original_filepath).stem
        return self.get_extracted_file_path(f"{base_name}.txt")
    
    def validate_structure_exists(self, minio_repository: Any) -> bool:
        """
        Validate that both original and extracted directories exist in MinIO.
        
        Args:
            minio_repository: MinIO repository instance
            
        Returns:
            True if both directories exist and contain files
            
        Raises:
            ValueError: If directory structure is invalid
        """
        try:
            # Check if original directory exists and has files
            original_files = minio_repository.list_files_in_import_directory(self.original_directory)
            if not original_files:
                raise ValueError(f"Original directory '{self.original_directory}' is empty or doesn't exist")
            
            # Check if extracted directory exists and has files
            extracted_files = minio_repository.list_files_in_import_directory(self.extracted_directory)
            if not extracted_files:
                raise ValueError(f"Extracted directory '{self.extracted_directory}' is empty or doesn't exist")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Directory structure validation failed: {e}") from e
    
    def __str__(self) -> str:
        return f"MinioDirectoryStructure(base='{self.base_directory}', original='{self.original_directory}', extracted='{self.extracted_directory}')"
