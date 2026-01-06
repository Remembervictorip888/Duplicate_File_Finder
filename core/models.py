"""
Pydantic models for the Duplicate File Finder application.

PURPOSE:
This module defines structured data models for file information, 
duplicate groups, and scan results with proper validation. These
models serve as the foundation for data validation and serialization
throughout the application.

RELATIONSHIPS:
- Used by: core.scanning, core.hashing, core.image_similarity, core.file_operations
- Depends on: pydantic, pathlib, typing, datetime, xxhash
- Consumed by: database module to store scan results

DEPENDENCIES:
- pydantic: For data validation and serialization
- pathlib: For path manipulation
- xxhash: For hash value validation (indirect)

USAGE:
Import specific models as needed in other modules:
    from core.models import FileInfo, DuplicateGroup, ScanResult, ScanSettings

These models provide automatic validation and serialization capabilities
that ensure data integrity across the application.
"""
from pydantic import BaseModel, Field, validator
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import xxhash


class FileInfo(BaseModel):
    """Model representing information about a single file."""
    path: Path
    size: int = Field(ge=0, description="File size in bytes")
    hash_value: Optional[str] = None
    created_time: datetime
    modified_time: datetime
    extension: str
    name: str
    
    @validator('path')
    def path_must_exist(cls, v):
        if not v.exists():
            raise ValueError(f'File does not exist: {v}')
        return v
    
    @validator('size')
    def size_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Size must be non-negative')
        return v


class DuplicateGroup(BaseModel):
    """Model representing a group of duplicate files."""
    id: str
    files: List[FileInfo] = Field(min_items=1)
    primary_file: Optional[FileInfo] = None
    detection_method: str = Field(..., description="Method used to detect duplicates (hash, filename, size, etc.)")
    
    @validator('files')
    def files_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Duplicate group must contain at least one file')
        return v


class ScanResult(BaseModel):
    """Model representing the results of a scan operation."""
    directory: Path
    scanned_files_count: int = Field(ge=0)
    duplicate_groups: List[DuplicateGroup]
    scan_start_time: datetime
    scan_end_time: datetime
    scan_duration: float  # in seconds
    methods_used: List[str]
    
    @property
    def total_duplicates_found(self) -> int:
        """Total number of duplicate files found."""
        return sum(len(group.files) - 1 for group in self.duplicate_groups)
    
    @property
    def duplicate_groups_count(self) -> int:
        """Number of duplicate groups found."""
        return len(self.duplicate_groups)


class ScanSettings(BaseModel):
    """Model representing settings for a scan operation."""
    directory: Path
    extensions: Optional[List[str]] = None
    use_hash: bool = True
    use_filename: bool = True
    use_size: bool = True
    use_patterns: bool = True
    use_custom_rules: bool = False
    use_advanced_grouping: bool = False
    min_file_size_mb: Optional[float] = None
    max_file_size_mb: Optional[float] = None
    image_similarity_threshold: int = Field(ge=0, le=20, default=10)
    suffix_rules: Optional[List[str]] = []
    prefix_rules: Optional[List[str]] = []
    containing_rules: Optional[List[str]] = []
    regex_rules: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    
    @validator('image_similarity_threshold')
    def similarity_threshold_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Similarity threshold must be between 0 and 20')
        return v
    
    @validator('min_file_size_mb', 'max_file_size_mb')
    def size_values_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('File size limits must be non-negative')
        return v
    
    @validator('directory')
    def directory_must_exist(cls, v):
        if not v.exists() or not v.is_dir():
            raise ValueError(f'Directory does not exist or is not a directory: {v}')
        return v


class FileHash(BaseModel):
    """Model representing a file hash for duplicate detection."""
    hash_value: str
    file_paths: List[Path] = Field(min_items=1)
    
    @validator('hash_value')
    def hash_value_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Hash value cannot be empty')
        return v
    
    @validator('file_paths')
    def file_paths_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError('File paths list cannot be empty')
        return v


class DuplicateFinderConfig(BaseModel):
    """Model representing the application configuration."""
    auto_select_strategy: str = Field(default='oldest', pattern=r'^(oldest|newest|lowest_res)$')
    image_similarity_threshold: int = Field(ge=0, le=20, default=10)
    default_extensions: List[str] = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.pdf',
        '.doc', '.docx', '.xls', '.xlsx'
    ]
    last_scan_directory: Optional[Path] = None
    min_file_size_mb: Optional[float] = None
    max_file_size_mb: Optional[float] = None
    use_custom_rules: bool = False
    use_advanced_grouping: bool = False
    
    @validator('image_similarity_threshold')
    def similarity_threshold_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Similarity threshold must be between 0 and 20')
        return v
