"""
File scanning module for duplicate file detection.

This module provides functions to scan directories for files efficiently.
"""
import os
from pathlib import Path
from typing import List, Generator, Tuple
import logging
from utils.path_helper import is_valid_file_type

logger = logging.getLogger(__name__)


def scan_directory_for_files(directory_path: str, extensions: List[str] = None) -> Generator[str, None, None]:
    """
    Scan a directory recursively for files with specified extensions.
    
    Args:
        directory_path: Path to the directory to scan
        extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
        
    Yields:
        File paths matching the specified extensions
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', 
                      '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.pdf', 
                      '.doc', '.docx', '.xls', '.xlsx']
    
    extensions = [ext.lower() for ext in extensions]
    
    try:
        with os.scandir(directory_path) as scan_iter:
            for entry in scan_iter:
                if entry.is_file():
                    if Path(entry.path).suffix.lower() in extensions:
                        yield entry.path
                elif entry.is_dir():
                    # Recursively scan subdirectories
                    yield from scan_directory_for_files(entry.path, extensions)
    except PermissionError as e:
        logger.warning(f"Permission denied when scanning directory {directory_path}: {e}")
    except OSError as e:
        logger.error(f"Error scanning directory {directory_path}: {e}")


def scan_directory_for_duplicates(directory_path: str) -> Tuple[List[str], int]:
    """
    Scan a directory for files that could be duplicates.
    
    Args:
        directory_path: Path to the directory to scan
        
    Returns:
        Tuple of (list of file paths, total count of files found)
    """
    file_paths = []
    total_files = 0
    
    logger.info(f"Starting scan of directory: {directory_path}")
    
    for file_path in scan_directory_for_files(directory_path):
        file_paths.append(file_path)
        total_files += 1
        
        # Log progress every 5000 files
        if total_files % 5000 == 0:
            logger.info(f"Discovered {total_files} files so far...")
    
    logger.info(f"Completed scan. Found {total_files} files in total")
    return file_paths, total_files


def get_file_metadata(file_path: str) -> dict:
    """
    Get metadata for a file including size, creation time, and modification time.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file metadata
    """
    try:
        stat = Path(file_path).stat()
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime
        }
    except (OSError, IOError) as e:
        logger.error(f"Error getting metadata for {file_path}: {e}")
        return {}