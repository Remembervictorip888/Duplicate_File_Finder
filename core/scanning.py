"""
File scanning module for duplicate file detection.

PURPOSE:
This module provides functions to scan directories for files efficiently.
It recursively traverses directory trees and filters files based on extensions
and other criteria. This is the foundational module for finding files that
will be analyzed for duplicates.

RELATIONSHIPS:
- Used by: main application flow, UI controllers, duplicate detection modules
- Uses: core.concurrency for concurrent scanning, utils.path_helper for file type validation
- Depends on: os, pathlib, typing, logging
- Provides file lists to: core.hashing, core.image_similarity, core.duplicate_detection

DEPENDENCIES:
- os: For directory traversal
- pathlib: For path manipulation
- core.concurrency: For concurrent file scanning (performance optimization)
- core.models: For ScanSettings and ScanResult models
- utils.path_helper: For file type validation

USAGE:
Use the main functions to scan directories for files:
    from core.scanning import scan_directory_for_duplicates, scan_with_models
    from core.models import ScanSettings
    
    # Basic file scanning
    files, count = scan_directory_for_duplicates("/path/to/directory")
    
    # Scanning with settings
    settings = ScanSettings(directory=Path("/path/to/directory"), extensions=['.jpg', '.png'])
    result = scan_with_models(settings)

The module handles errors gracefully and provides progress logging.
"""
import os
from pathlib import Path
from typing import List, Generator, Tuple
import logging
from utils.path_helper import is_valid_file_type
from core.models import FileInfo, ScanResult, ScanSettings
from datetime import datetime

# Import concurrent processing functions
from core.concurrency import scan_directory_concurrent, get_file_info_concurrent_batch

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


def scan_with_models(settings: ScanSettings) -> ScanResult:
    """
    Perform a scan using Pydantic models for structured data handling.
    
    Args:
        settings: ScanSettings model containing all scan parameters
        
    Returns:
        ScanResult model containing the scan results
    """
    start_time = datetime.now()
    logger.info(f"Starting scan with models for directory: {settings.directory}")
    
    # Get all files based on settings
    extensions = settings.extensions or [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.pdf',
        '.doc', '.docx', '.xls', '.xlsx'
    ]
    
    # Use concurrent scanning if available
    file_paths = scan_directory_concurrent(str(settings.directory), extensions)
    scanned_files_count = len(file_paths)
    
    logger.info(f"Found {scanned_files_count} files to scan")
    
    # Apply size filters if specified
    if settings.min_file_size_mb is not None or settings.max_file_size_mb is not None:
        # Use concurrent processing to get file info
        path_to_info = get_file_info_concurrent_batch(file_paths)
        
        filtered_paths = []
        min_size_bytes = (settings.min_file_size_mb or 0) * 1024 * 1024
        max_size_bytes = (settings.max_file_size_mb or float('inf')) * 1024 * 1024
        
        for path in file_paths:
            if path in path_to_info and path_to_info[path]:
                size = path_to_info[path].size
                if min_size_bytes <= size <= max_size_bytes:
                    filtered_paths.append(path)
            else:
                # If we couldn't get file info, try direct size check
                try:
                    size = Path(path).stat().st_size
                    if min_size_bytes <= size <= max_size_bytes:
                        filtered_paths.append(path)
                except (OSError, IOError) as e:
                    logger.warning(f"Could not access file {path} for size filtering: {e}")
        
        file_paths = filtered_paths
        logger.info(f"After size filtering: {len(file_paths)} files to scan")
    
    # In a real implementation, we would process the files using various methods
    # and return proper duplicate groups. For now, we'll return an empty result.
    from core.models import DuplicateGroup
    end_time = datetime.now()
    
    result = ScanResult(
        directory=settings.directory,
        scanned_files_count=scanned_files_count,
        duplicate_groups=[],  # Placeholder - in a real implementation this would contain actual groups
        scan_start_time=start_time,
        scan_end_time=end_time,
        scan_duration=(end_time - start_time).total_seconds(),
        methods_used=[]
    )
    
    logger.info(f"Scan completed in {result.scan_duration:.2f} seconds")
    return result