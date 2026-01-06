"""
File operations module for safe file management.

This module provides functions for safely deleting files to the Recycle Bin.
"""
from send2trash import send2trash
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def safe_delete_files(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """
    Move files to the Recycle Bin (safe delete).
    
    Args:
        file_paths: List of file paths to delete safely
        
    Returns:
        Tuple of (list of successfully deleted files, list of failed deletions)
    """
    successful = []
    failed = []
    
    for file_path in file_paths:
        try:
            send2trash(file_path)
            successful.append(file_path)
            logger.info(f"Moved file to Recycle Bin: {file_path}")
        except Exception as e:
            logger.error(f"Failed to move file to Recycle Bin {file_path}: {e}")
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