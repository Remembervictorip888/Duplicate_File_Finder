"""
File operations module for safe file management.

PURPOSE:
This module provides functions for safely managing files, particularly for deleting duplicate
files in a safe manner using the Recycle Bin/Trash. It also includes functionality for
automatically selecting which duplicate files to delete based on various strategies such as
file age or resolution (for images).

RELATIONSHIPS:
- Used by: Main application flow when deleting duplicate files
- Uses: send2trash library for safe deletion, PIL for image resolution comparison
- Provides: Safe file deletion and auto-selection of files for deletion
- Called when: User confirms deletion of duplicate files

DEPENDENCIES:
- send2trash: For safe deletion to Recycle Bin/Trash
- pathlib: For path manipulation
- typing: For type hints (List, Tuple)
- PIL (Pillow): For image resolution comparison in 'lowest_res' strategy
- logging: For logging operations

USAGE:
Use the main functions to perform safe file operations:
    from core.file_operations import safe_delete_files, auto_select_duplicates_for_deletion
    
    # Safely delete files to Recycle Bin
    successful, failed = safe_delete_files(['/path/to/file1.jpg', '/path/to/file2.jpg'])
    
    # Auto-select duplicates for deletion based on strategy
    duplicate_groups = [['file1.jpg', 'file2.jpg'], ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']]
    files_to_delete = auto_select_duplicates_for_deletion(duplicate_groups, strategy='oldest')
    
The module provides safe operations that prevent accidental permanent data loss.
"""
from send2trash import send2trash
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def safe_delete_files(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """
    Move files to the Recycle Bin (safe delete).
    
    Args:
        file_paths: List of file paths to delete safely
        
    Returns:
        Tuple of (successful_deletions, failed_deletions)
    """
    successful = []
    failed = []
    
    for file_path in file_paths:
        try:
            send2trash(file_path)
            successful.append(file_path)
            logger.info(f"Moved file to Recycle Bin: {file_path}")
        except Exception as e:
            logger.error(f"Failed to move file to Recycle Bin: {file_path}, Error: {e}")
            failed.append(file_path)
    
    return successful, failed


def auto_select_duplicates_for_deletion(duplicate_groups: List[List[str]], strategy: str = 'oldest') -> List[str]:
    """
    Auto-select duplicates for deletion based on a strategy.
    
    Args:
        duplicate_groups: List of duplicate file groups (each group is a list of file paths)
        strategy: Selection strategy ('oldest', 'newest', 'lowest_res')
        
    Returns:
        List of file paths selected for deletion
    """
    files_to_delete = []
    
    for group in duplicate_groups:
        if len(group) <= 1:
            continue  # No duplicates to select from
            
        if strategy == 'oldest':
            # Find the oldest file in the group
            oldest_file = min(group, key=lambda f: Path(f).stat().st_mtime)
            files_to_delete.append(oldest_file)
        elif strategy == 'newest':
            # Find the newest file in the group
            newest_file = max(group, key=lambda f: Path(f).stat().st_mtime)
            files_to_delete.append(newest_file)
        elif strategy == 'lowest_res':
            # For image files, find the one with the lowest resolution
            image_files = [f for f in group if Path(f).suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']]
            if image_files:
                try:
                    from PIL import Image
                    lowest_res_file = min(
                        image_files,
                        key=lambda f: Image.open(f).size[0] * Image.open(f).size[1]  # width * height
                    )
                    files_to_delete.append(lowest_res_file)
                except Exception as e:
                    logger.error(f"Error determining image resolution: {e}")
                    # Fallback to oldest if resolution check fails
                    oldest_file = min(group, key=lambda f: Path(f).stat().st_mtime)
                    files_to_delete.append(oldest_file)
            else:
                # For non-image files, default to oldest
                oldest_file = min(group, key=lambda f: Path(f).stat().st_mtime)
                files_to_delete.append(oldest_file)
    
    logger.info(f"Auto-selected {len(files_to_delete)} files for deletion using '{strategy}' strategy")
    return files_to_delete