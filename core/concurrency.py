"""
Concurrency module for the Duplicate File Finder application.

PURPOSE:
This module provides functions for concurrent file processing using ThreadPoolExecutor
for I/O-bound operations and multiprocessing for CPU-bound operations. It significantly
improves performance when processing large numbers of files by utilizing multiple
threads for operations like hashing and file information retrieval.

RELATIONSHIPS:
- Used by: core.hashing, core.scanning, core.duplicate_detection for performance optimization
- Uses: concurrent.futures, os, pathlib, xxhash and other standard libraries
- Provides: Concurrent processing capabilities to speed up file operations
- Called when: Processing large numbers of files to improve performance

DEPENDENCIES:
- concurrent.futures: For ThreadPoolExecutor and ProcessPoolExecutor
- os: For file system operations
- xxhash: For concurrent hash calculation
- pathlib: For path manipulation
- typing: For type hints
- functools: For partial function application

USAGE:
Use the main functions to process files concurrently:
    from core.concurrency import calculate_hashes_concurrent, get_file_info_concurrent_batch, 
                            find_duplicates_by_hash_concurrent, scan_directory_concurrent
    
    # Calculate hashes for files concurrently
    path_to_hash = calculate_hashes_concurrent(file_paths)
    
    # Get file info concurrently
    path_to_info = get_file_info_concurrent_batch(file_paths)
    
    # Find duplicates by hash using concurrent processing
    duplicates = find_duplicates_by_hash_concurrent(file_paths)
    
    # Scan directory concurrently
    files = scan_directory_concurrent(directory_path, extensions)

This module is essential for performance optimization when dealing with large datasets.
"""
import os
import xxhash
from pathlib import Path
from typing import List, Dict, Tuple, Callable, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import partial
import logging
from datetime import datetime

from core.models import FileInfo

logger = logging.getLogger(__name__)


def get_hash_concurrent(filepath: str) -> Tuple[str, str]:
    """
    Calculate xxhash for a file using memory-efficient chunked reading.
    
    Args:
        filepath: Path to the file to hash
        
    Returns:
        Tuple of (filepath, hash) or (filepath, "") if error
    """
    h = xxhash.xxh64()
    b = bytearray(128 * 1024)  # 128KB chunks
    mv = memoryview(b)
    
    try:
        with open(filepath, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        return filepath, h.hexdigest()
    except (OSError, IOError) as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return filepath, ""


def get_file_info_concurrent(filepath: str) -> Tuple[str, FileInfo]:
    """
    Get detailed information about a file and return as a FileInfo model.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Tuple of (filepath, FileInfo model with file details) or (filepath, None) if error
    """
    path_obj = Path(filepath)
    
    try:
        stat = path_obj.stat()
        file_info = FileInfo(
            path=path_obj,
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            extension=path_obj.suffix.lower(),
            name=path_obj.name
        )
        return filepath, file_info
    except (OSError, IOError) as e:
        logger.error(f"Error getting info for file {filepath}: {e}")
        return filepath, None


def process_files_concurrent(
    file_paths: List[str], 
    processor_func: Callable[[str], Tuple[str, Any]], 
    max_workers: int = None
) -> Dict[str, Any]:
    """
    Process a list of files concurrently using ThreadPoolExecutor.
    
    Args:
        file_paths: List of file paths to process
        processor_func: Function that takes a file path and returns (filepath, result)
        max_workers: Maximum number of worker threads (defaults to number of CPUs)
        
    Returns:
        Dictionary mapping file paths to their processed results
    """
    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 1) + 4)
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {executor.submit(processor_func, path): path for path in file_paths}
        
        # Collect results as they complete
        completed = 0
        total = len(file_paths)
        
        for future in as_completed(future_to_path):
            filepath, result = future.result()
            
            if result:  # Only store non-empty results
                results[filepath] = result
            
            completed += 1
            if completed % 1000 == 0:
                logger.info(f"Processed {completed}/{total} files concurrently")
    
    return results


def calculate_hashes_concurrent(file_paths: List[str], max_workers: int = None) -> Dict[str, str]:
    """
    Calculate hashes for a list of files concurrently.
    
    Args:
        file_paths: List of file paths to hash
        max_workers: Maximum number of worker threads (defaults to number of CPUs)
        
    Returns:
        Dictionary mapping file paths to their hash values
    """
    return process_files_concurrent(file_paths, get_hash_concurrent, max_workers)


def get_file_info_concurrent_batch(file_paths: List[str], max_workers: int = None) -> Dict[str, FileInfo]:
    """
    Get file info for a list of files concurrently.
    
    Args:
        file_paths: List of file paths to get info for
        max_workers: Maximum number of worker threads (defaults to number of CPUs)
        
    Returns:
        Dictionary mapping file paths to their FileInfo models
    """
    return process_files_concurrent(file_paths, get_file_info_concurrent, max_workers)


def find_duplicates_by_hash_concurrent(file_paths: List[str], max_workers: int = None) -> Dict[str, List[str]]:
    """
    Find duplicate files by comparing their hashes using concurrent processing.
    
    Args:
        file_paths: List of file paths to check for duplicates
        max_workers: Maximum number of worker threads (defaults to number of CPUs)
        
    Returns:
        Dictionary mapping hash values to lists of duplicate file paths
    """
    logger.info(f"Starting concurrent hash calculation for {len(file_paths)} files")
    
    # Calculate all hashes concurrently
    path_to_hash = calculate_hashes_concurrent(file_paths, max_workers)
    
    # Group files by hash
    hash_map: Dict[str, List[str]] = {}
    for filepath, file_hash in path_to_hash.items():
        if file_hash:  # Only process files that were successfully hashed
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(filepath)
    
    # Filter out unique files (those with only one path for a hash)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    logger.info(f"Found {len(duplicates)} groups of duplicate files")
    
    return duplicates


def scan_directory_concurrent(directory_path: str, extensions: List[str] = None, max_workers: int = None) -> List[str]:
    """
    Concurrently scan a directory for files with specified extensions.
    
    Args:
        directory_path: Path to the directory to scan
        extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
        max_workers: Maximum number of worker threads (defaults to number of CPUs)
        
    Returns:
        List of file paths matching the specified extensions
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', 
                      '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.pdf', 
                      '.doc', '.docx', '.xls', '.xlsx']
    
    extensions = [ext.lower() for ext in extensions]
    
    def is_valid_file(filepath: str) -> Tuple[str, bool]:
        """Check if a file has a valid extension."""
        return filepath, Path(filepath).suffix.lower() in extensions
    
    # First, collect all files (not concurrent since it's I/O bound to disk)
    all_files = []
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                filepath = os.path.join(root, file)
                all_files.append(filepath)
    except PermissionError as e:
        logger.warning(f"Permission denied when scanning directory {directory_path}: {e}")
    
    # Then check extensions concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(is_valid_file, all_files))
    
    # Filter files with valid extensions
    valid_files = [filepath for filepath, is_valid in results if is_valid]
    
    logger.info(f"Found {len(valid_files)} files with valid extensions")
    return valid_files