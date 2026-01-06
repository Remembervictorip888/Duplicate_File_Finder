"""
Path helper utilities for the duplicate finder application.

This module provides utility functions for working with file paths.
"""
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def is_valid_file_type(file_path: str, extensions: List[str] = None) -> bool:
    """
    Check if a file has a valid extension for processing.
    
    Args:
        file_path: Path to the file
        extensions: List of valid extensions (with dots, e.g., ['.jpg', '.png'])
        
    Returns:
        True if the file extension is valid, False otherwise
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
                      '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.pdf',
                      '.doc', '.docx', '.xls', '.xlsx']
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in [ext.lower() for ext in extensions]


def normalize_path(path: str) -> str:
    """
    Normalize a file path to handle different formats consistently.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path string
    """
    try:
        return str(Path(path).resolve())
    except Exception as e:
        logger.error(f"Error normalizing path {path}: {e}")
        return path


def get_common_parent_path(file_paths: List[str]) -> str:
    """
    Find the common parent directory for a list of file paths.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        Common parent directory path
    """
    if not file_paths:
        return ""
    
    paths = [Path(path) for path in file_paths]
    common_path = Path(paths[0]).parent
    
    for path in paths[1:]:
        # Find common parts of the path
        path_parts = list(path.parts)
        common_parts = list(common_path.parts)
        
        # Compare parts until they differ
        min_len = min(len(path_parts), len(common_parts))
        new_common_parts = []
        
        for i in range(min_len):
            if path_parts[i] == common_parts[i]:
                new_common_parts.append(path_parts[i])
            else:
                break
        
        common_path = Path(*new_common_parts)
    
    return str(common_path)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.2 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"