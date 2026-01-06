"""
File name comparison module for duplicate detection.

This module provides functions to detect duplicate files based on their names,
ignoring case and extension, and handling common naming patterns.
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple, Callable, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_filename(filename: str) -> str:
    """
    Normalize a filename by removing common duplicate indicators and converting to lowercase.
    
    Args:
        filename: Original filename
        
    Returns:
        Normalized filename with common patterns removed
    """
    # Get the stem (name without extension)
    path = Path(filename)
    stem = path.stem.lower()
    
    # Remove common duplicate indicators:
    # - Numbers with underscores like "_1", "_2", etc.
    # - Numbers in parentheses like "(1)", "(2)", etc.
    # - "copy" in various forms
    # - "duplicate" in various forms
    
    # Remove patterns like _1, _2, _copy, _duplicate
    stem = re.sub(r'_[0-9]+$', '', stem)
    stem = re.sub(r'_copy$', '', stem)
    stem = re.sub(r'_duplicate$', '', stem)
    stem = re.sub(r'_duplicates$', '', stem)
    
    # Remove patterns like (1), (2), (copy), (duplicate)
    stem = re.sub(r'\([0-9]+\)$', '', stem)
    stem = re.sub(r'\(copy\)$', '', stem)
    stem = re.sub(r'\(duplicate\)$', '', stem)
    
    # Remove common variations of "copy" and "duplicate"
    stem = re.sub(r' copy$', '', stem)
    stem = re.sub(r' duplicate$', '', stem)
    stem = re.sub(r' \([Cc]opy\)$', '', stem)
    stem = re.sub(r' \([Dd]uplicate\)$', '', stem)
    
    return stem


def compare_filenames(name1: str, name2: str) -> bool:
    """
    Compare two filenames to check if they are potential duplicates.
    
    Args:
        name1: First filename
        name2: Second filename
        
    Returns:
        True if the filenames are potential duplicates, False otherwise
    """
    normalized1 = normalize_filename(name1)
    normalized2 = normalize_filename(name2)
    
    # Check if they are identical after normalization
    if normalized1 == normalized2:
        return True
    
    # Check if one is a substring of the other after normalization
    # This handles cases like "photo.jpg" vs "photo copy.jpg"
    if normalized1 in normalized2 or normalized2 in normalized1:
        return True
    
    return False


def find_duplicates_by_filename(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Find duplicate files by comparing their filenames.
    
    Args:
        file_paths: List of file paths to check for duplicates
        
    Returns:
        Dictionary mapping normalized names to lists of duplicate file paths
    """
    # Group files by their normalized names
    name_groups: Dict[str, List[str]] = {}
    
    for file_path in file_paths:
        try:
            normalized_name = normalize_filename(file_path)
            
            if normalized_name not in name_groups:
                name_groups[normalized_name] = []
            name_groups[normalized_name].append(file_path)
            
            # Log progress every 1000 files
            if len(name_groups) % 1000 == 0:
                logger.info(f"Processed {len(name_groups)} unique normalized names for filename comparison")
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    # Filter out groups with only one file (no duplicates)
    duplicates = {name: paths for name, paths in name_groups.items() if len(paths) > 1}
    logger.info(f"Found {len(duplicates)} groups of potential duplicate files by filename")
    
    return duplicates


def find_duplicates_by_patterns(file_paths: List[str], custom_patterns: List[str] = None) -> Dict[str, List[str]]:
    """
    Find duplicate files using custom patterns.
    
    Args:
        file_paths: List of file paths to check for duplicates
        custom_patterns: List of custom regex patterns to match against filenames
        
    Returns:
        Dictionary mapping pattern groups to lists of matching file paths
    """
    pattern_groups: Dict[str, List[str]] = {}
    
    # Default patterns for common duplicate naming conventions
    default_patterns = [
        r'(.+?)_[0-9]+$',           # matches "name_1", "name_2", etc.
        r'(.+?)\([0-9]+\)$',        # matches "name(1)", "name(2)", etc.
        r'(.+?) \([0-9]+\)$',       # matches "name (1)", "name (2)", etc.
        r'(.+?) copy$',             # matches "name copy"
        r'(.+?) \([Cc]opy\)$',      # matches "name (Copy)"
        r'(.+?) duplicate$',        # matches "name duplicate"
    ]
    
    # Add custom patterns if provided
    all_patterns = default_patterns + (custom_patterns or [])
    
    for file_path in file_paths:
        try:
            path_obj = Path(file_path)
            stem = path_obj.stem
            
            for pattern in all_patterns:
                match = re.match(pattern, stem, re.IGNORECASE)
                if match:
                    # Use the pattern as a key for grouping
                    pattern_key = f"pattern:{pattern}"
                    if pattern_key not in pattern_groups:
                        pattern_groups[pattern_key] = []
                    pattern_groups[pattern_key].append(file_path)
                    break  # Only match one pattern per file to avoid duplication
        except Exception as e:
            logger.error(f"Error processing file {file_path} with patterns: {e}")
    
    logger.info(f"Applied {len(all_patterns)} patterns and found {len(pattern_groups)} pattern groups")
    
    return pattern_groups


def find_duplicates_by_keywords(file_paths: List[str], keywords: List[str]) -> Dict[str, List[str]]:
    """
    Find duplicate files based on keywords in their names.
    
    Args:
        file_paths: List of file paths to check
        keywords: List of keywords to search for in filenames
        
    Returns:
        Dictionary mapping keywords to lists of matching file paths
    """
    keyword_groups: Dict[str, List[str]] = {}
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        matching_files = []
        
        for file_path in file_paths:
            try:
                path_obj = Path(file_path)
                if keyword_lower in path_obj.name.lower():
                    matching_files.append(file_path)
            except Exception as e:
                logger.error(f"Error checking keyword {keyword} in file {file_path}: {e}")
        
        if len(matching_files) > 1:  # Only include groups with potential duplicates
            keyword_groups[keyword] = matching_files
    
    logger.info(f"Checked {len(keywords)} keywords and found {len(keyword_groups)} keyword groups")
    
    return keyword_groups


def find_duplicates_by_custom_rules(
    file_paths: List[str],
    custom_rules: List[Callable[[str], bool]] = None,
    custom_grouping: List[Callable[[List[str]], Dict[str, List[str]]]] = None
) -> Dict[str, List[str]]:
    """
    Find duplicate files using custom rules defined by the user.
    
    Args:
        file_paths: List of file paths to check for duplicates
        custom_rules: List of functions that take a filename and return True if it matches the rule
        custom_grouping: List of functions that take a list of file paths and group them based on custom logic
        
    Returns:
        Dictionary mapping rule names to lists of matching file paths
    """
    rule_groups: Dict[str, List[str]] = {}
    
    if custom_rules:
        for i, rule in enumerate(custom_rules):
            matching_files = []
            rule_name = f"custom_rule_{i}"
            
            for file_path in file_paths:
                try:
                    if rule(Path(file_path).name):
                        matching_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error applying custom rule {rule_name} to file {file_path}: {e}")
            
            if len(matching_files) > 1:  # Only include groups with potential duplicates
                rule_groups[rule_name] = matching_files
    
    if custom_grouping:
        for i, grouping_func in enumerate(custom_grouping):
            try:
                groups = grouping_func(file_paths)
                for group_name, group_files in groups.items():
                    if len(group_files) > 1:  # Only include groups with potential duplicates
                        full_group_name = f"custom_grouping_{i}_{group_name}"
                        rule_groups[full_group_name] = group_files
            except Exception as e:
                logger.error(f"Error applying custom grouping function {i}: {e}")
    
    logger.info(f"Applied custom rules and found {len(rule_groups)} rule groups")
    
    return rule_groups


def create_filename_ending_rule(ending: str) -> Callable[[str], bool]:
    """
    Create a custom rule function that checks if a filename ends with a specific string.
    
    Args:
        ending: The string that the filename should end with (case-insensitive)
        
    Returns:
        A function that takes a filename and returns True if it ends with the specified string
    """
    def rule(filename: str) -> bool:
        return filename.lower().endswith(ending.lower())
    
    return rule


def create_filename_containing_rule(contains: str) -> Callable[[str], bool]:
    """
    Create a custom rule function that checks if a filename contains a specific string.
    
    Args:
        contains: The string that the filename should contain (case-insensitive)
        
    Returns:
        A function that takes a filename and returns True if it contains the specified string
    """
    def rule(filename: str) -> bool:
        return contains.lower() in filename.lower()
    
    return rule


def create_filename_starting_rule(starting: str) -> Callable[[str], bool]:
    """
    Create a custom rule function that checks if a filename starts with a specific string.
    
    Args:
        starting: The string that the filename should start with (case-insensitive)
        
    Returns:
        A function that takes a filename and returns True if it starts with the specified string
    """
    def rule(filename: str) -> bool:
        return filename.lower().startswith(starting.lower())
    
    return rule


def create_custom_regex_rule(pattern: str) -> Callable[[str], bool]:
    """
    Create a custom rule function using a regex pattern.
    
    Args:
        pattern: The regex pattern to match against the filename
        
    Returns:
        A function that takes a filename and returns True if it matches the pattern
    """
    compiled_pattern = re.compile(pattern, re.IGNORECASE)
    
    def rule(filename: str) -> bool:
        return bool(compiled_pattern.search(filename))
    
    return rule


def group_by_custom_logic(file_paths: List[str], 
                         grouping_func: Callable[[str], str]) -> Dict[str, List[str]]:
    """
    Group files using a custom grouping logic function.
    
    Args:
        file_paths: List of file paths to group
        grouping_func: A function that takes a filename and returns a group key
        
    Returns:
        Dictionary mapping group keys to lists of file paths
    """
    groups: Dict[str, List[str]] = {}
    
    for file_path in file_paths:
        try:
            group_key = grouping_func(Path(file_path).name)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(file_path)
        except Exception as e:
            logger.error(f"Error applying grouping function to file {file_path}: {e}")
    
    return groups