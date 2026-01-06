"""
Size filtering module for duplicate detection.

This module provides functions to filter files based on their size,
allowing users to exclude files smaller or larger than specified thresholds.
"""
import os
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def filter_files_by_size(
    file_paths: List[str], 
    min_size_mb: float = None, 
    max_size_mb: float = None
) -> Tuple[List[str], List[str]]:
    """
    Filter files based on size thresholds.
    
    Args:
        file_paths: List of file paths to filter
        min_size_mb: Minimum file size in MB (files smaller will be excluded)
        max_size_mb: Maximum file size in MB (files larger will be excluded)
        
    Returns:
        Tuple of (filtered_file_paths, excluded_file_paths)
    """
    filtered_files = []
    excluded_files = []
    
    min_size_bytes = int(min_size_mb * 1024 * 1024) if min_size_mb is not None else 0
    max_size_bytes = int(max_size_mb * 1024 * 1024) if max_size_mb is not None else float('inf')
    
    for file_path in file_paths:
        try:
            size_bytes = os.path.getsize(file_path)
            
            # Check if file size is within the allowed range
            if (min_size_bytes <= size_bytes <= max_size_bytes):
                filtered_files.append(file_path)
            else:
                excluded_files.append(file_path)
                
        except (OSError, IOError) as e:
            logger.error(f"Error getting size for file {file_path}: {e}")
            excluded_files.append(file_path)
    
    logger.info(f"Size filtering: {len(filtered_files)} files passed, {len(excluded_files)} files excluded")
    return filtered_files, excluded_files


def get_file_size_mb(file_path: str) -> float:
    """
    Get the size of a file in MB.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size in MB as a float
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (OSError, IOError) as e:
        logger.error(f"Error getting size for file {file_path}: {e}")
        return 0.0


def get_size_stats(file_paths: List[str]) -> Tuple[float, float, float]:
    """
    Get size statistics for a list of files.
    
    Args:
        file_paths: List of file paths to analyze
        
    Returns:
        Tuple of (min_size_mb, max_size_mb, avg_size_mb)
    """
    if not file_paths:
        return 0.0, 0.0, 0.0
    
    sizes = []
    for file_path in file_paths:
        try:
            size_bytes = os.path.getsize(file_path)
            sizes.append(size_bytes / (1024 * 1024))
        except (OSError, IOError) as e:
            logger.error(f"Error getting size for file {file_path}: {e}")
    
    if not sizes:
        return 0.0, 0.0, 0.0
    
    return min(sizes), max(sizes), sum(sizes) / len(sizes)