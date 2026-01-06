"""
Hashing module for duplicate file detection.

This module provides functions to calculate file hashes using xxhash for fast performance.
"""
import xxhash
from pathlib import Path
from typing import Dict, List, Tuple
import logging

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
    hash_map: Dict[str, List[str]] = {}
    
    for i, file_path in enumerate(file_paths):
        try:
            # First check file size - if it's 0, skip it
            size = get_file_size(file_path)
            if size == 0:
                continue
                
            file_hash = get_hash(file_path)
            if file_hash:
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_path)
                
                # Log progress every 1000 files
                if (i + 1) % 1000 == 0:
                    logger.info(f"Processed {i + 1}/{len(file_paths)} files for hashing")
                    
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            
    # Filter out unique files (those with only one path for a hash)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    logger.info(f"Found {len(duplicates)} groups of duplicate files")
    
    return duplicates