"""
Hashing module for duplicate file detection.

PURPOSE:
This module provides functions to calculate file hashes using xxhash for fast performance.
It implements memory-efficient file reading and hash calculation, which is crucial for
detecting exact duplicate files. The module also provides functions to get file
information and group files by hash values.

RELATIONSHIPS:
- Used by: core.duplicate_detection, main application flow
- Uses: core.concurrency for concurrent hash calculation
- Depends on: xxhash, pathlib, typing, logging
- Provides: Core duplicate detection capability based on hash comparison

DEPENDENCIES:
- xxhash: For fast hash calculation (faster than MD5/SHA)
- pathlib: For path manipulation
- core.concurrency: For concurrent hash calculation
- core.models: For FileInfo and FileHash models

USAGE:
Use the main functions to calculate hashes and find duplicates:
    from core.hashing import get_hash, find_duplicates_by_hash, find_duplicates_by_hash_models
    
    # Calculate hash for a single file
    file_hash = get_hash("/path/to/file.txt")
    
    # Find duplicates by hash from a list of files
    duplicates = find_duplicates_by_hash(["/path/to/file1.txt", "/path/to/file2.txt"])
    
    # Get duplicates as Pydantic models
    duplicates_models = find_duplicates_by_hash_models(file_paths)

The module uses memory-efficient chunked reading for large files and handles errors gracefully.
"""
import xxhash
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime
from core.models import FileInfo, FileHash

# Import concurrent processing functions
from core.concurrency import find_duplicates_by_hash_concurrent, calculate_hashes_concurrent

logger = logging.getLogger(__name__)


def get_hash(filepath: str) -> str:
    """
    Calculate xxhash for a file using memory-efficient chunked reading.
    
    Args:
        filepath: Path to the file to hash
        
    Returns:
        Hex digest of the file's hash
    """
    h = xxhash.xxh64()
    b = bytearray(128 * 1024)  # 128KB chunks
    mv = memoryview(b)
    
    try:
        with open(filepath, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        return h.hexdigest()
    except (OSError, IOError) as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return ""


def get_file_info(filepath: str) -> FileInfo:
    """
    Get detailed information about a file and return as a FileInfo model.
    
    Args:
        filepath: Path to the file
        
    Returns:
        FileInfo model with file details
    """
    path_obj = Path(filepath)
    
    try:
        stat = path_obj.stat()
        return FileInfo(
            path=path_obj,
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            extension=path_obj.suffix.lower(),
            name=path_obj.name
        )
    except (OSError, IOError) as e:
        logger.error(f"Error getting info for file {filepath}: {e}")
        raise ValueError(f"Could not get file info for {filepath}")


def get_file_size(filepath: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Size of the file in bytes, or -1 if error
    """
    try:
        return Path(filepath).stat().st_size
    except (OSError, IOError) as e:
        logger.error(f"Error getting size of file {filepath}: {e}")
        return -1


def find_duplicates_by_hash(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Find duplicate files by comparing their hashes.
    
    Args:
        file_paths: List of file paths to check for duplicates
        
    Returns:
        Dictionary mapping hash values to lists of duplicate file paths
    """
    # Use concurrent processing for better performance
    return find_duplicates_by_hash_concurrent(file_paths)


def find_duplicates_by_hash_models(file_paths: List[str]) -> List[FileHash]:
    """
    Find duplicate files by comparing their hashes, returning Pydantic models.
    
    Args:
        file_paths: List of file paths to check for duplicates
        
    Returns:
        List of FileHash models containing hash values and their duplicate file paths
    """
    # Use concurrent processing to calculate hashes
    path_to_hash = calculate_hashes_concurrent(file_paths)
    
    # Group files by hash
    hash_map: Dict[str, List[Path]] = {}
    for filepath, file_hash in path_to_hash.items():
        if file_hash:  # Only process files that were successfully hashed
            path_obj = Path(filepath)
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(path_obj)
    
    # Filter out unique files (those with only one path for a hash)
    duplicate_hashes = [FileHash(hash_value=h, file_paths=paths) 
                        for h, paths in hash_map.items() if len(paths) > 1]
    
    logger.info(f"Found {len(duplicate_hashes)} groups of duplicate files")
    
    return duplicate_hashes
