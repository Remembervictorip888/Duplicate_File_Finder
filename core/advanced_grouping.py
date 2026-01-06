"""
Advanced duplicate grouping module.

PURPOSE:
This module provides functions to group potential duplicate files based on advanced
naming patterns and relationships. It implements sophisticated algorithms to detect
files that may be duplicates based on naming conventions, such as files with
incremental numbers, copy indicators, or other common patterns that indicate
duplicate content with slight name variations.

RELATIONSHIPS:
- Used by: core.duplicate_detection for advanced duplicate detection
- Uses: re, pathlib, typing, logging standard libraries
- Provides: Advanced grouping functionality for potential duplicates
- Called when: Advanced grouping is enabled in scan settings

DEPENDENCIES:
- re: For regular expression pattern matching
- pathlib: For path manipulation
- typing: For type hints (List, Dict, Tuple)
- logging: For logging operations

USAGE:
Use the main functions to group files by advanced patterns:
    from core.advanced_grouping import group_by_advanced_patterns, group_by_filename_similarity, group_files_by_relationships, group_by_custom_rules
    
    # Group files by advanced naming patterns
    pattern_groups = group_by_advanced_patterns(file_paths)
    
    # Group files by filename similarity
    similarity_groups = group_by_filename_similarity(file_paths, similarity_threshold=0.8)
    
    # Group files by naming relationships
    relationship_groups = group_files_by_relationships(file_paths)
    
    # Group files by custom rules
    custom_groups = group_by_custom_rules(file_paths)

This module is particularly useful for identifying duplicates that don't have identical content
but follow naming conventions that suggest they are duplicates (e.g., image_1.jpg, image_2.jpg).
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def normalize_for_grouping(filename: str) -> str:
    """
    Normalize a filename for grouping purposes by removing common duplicate indicators
    while preserving the base name.
    
    Args:
        filename: Original filename
        
    Returns:
        Normalized filename with common duplicate indicators removed
    """
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


def extract_base_name_with_pattern(filename: str) -> Tuple[str, str]:
    """
    Extract the base name and pattern type from a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Tuple of (base_name, pattern_type) where pattern_type indicates the duplicate pattern
    """
    path = Path(filename)
    stem = path.stem.lower()
    
    # Pattern for _1, _2, etc.
    match = re.match(r'^(.+?)_([0-9]+)$', stem)
    if match:
        return match.group(1), f"underscore_number_{match.group(2)}"
    
    # Pattern for (1), (2), etc.
    match = re.match(r'^(.+?)\(([0-9]+)\)$', stem)
    if match:
        return match.group(1), f"parentheses_number_{match.group(2)}"
    
    # Pattern for (copy), (duplicate), etc.
    match = re.match(r'^(.+?)\(([Cc]opy|[Dd]uplicate)\)$', stem)
    if match:
        return match.group(1), f"parentheses_{match.group(2).lower()}"
    
    # Pattern for copy, duplicate at the end
    match = re.match(r'^(.+?) (copy|duplicate)$', stem)
    if match:
        return match.group(1), f"suffix_{match.group(2)}"
    
    # If no pattern detected, return the stem as base name
    return stem, "original"


def group_by_advanced_patterns(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Group files using advanced naming patterns to identify potential duplicates.
    
    Args:
        file_paths: List of file paths to group
        
    Returns:
        Dictionary mapping base names to lists of potential duplicate file paths
    """
    # Dictionary to hold groups of files
    pattern_groups: Dict[str, List[str]] = {}
    
    for file_path in file_paths:
        try:
            # Extract base name and pattern type
            base_name, pattern_type = extract_base_name_with_pattern(file_path)
            
            # Create a group key that combines the base name with the pattern type
            group_key = base_name
            
            if group_key not in pattern_groups:
                pattern_groups[group_key] = []
            pattern_groups[group_key].append(file_path)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path} for advanced grouping: {e}")
    
    # Filter out groups with only one file (no duplicates)
    result = {key: paths for key, paths in pattern_groups.items() if len(paths) > 1}
    
    logger.info(f"Advanced grouping found {len(result)} groups of potential duplicates")
    return result


def group_by_filename_similarity(file_paths: List[str], similarity_threshold: float = 0.8) -> Dict[str, List[str]]:
    """
    Group files based on filename similarity.
    
    Args:
        file_paths: List of file paths to group
        similarity_threshold: Threshold for considering filenames similar (0.0 to 1.0)
        
    Returns:
        Dictionary mapping base names to lists of similar file paths
    """
    # Group files by their normalized names first
    name_groups: Dict[str, List[str]] = {}
    
    for file_path in file_paths:
        try:
            normalized_name = normalize_for_grouping(file_path)
            
            if normalized_name not in name_groups:
                name_groups[normalized_name] = []
            name_groups[normalized_name].append(file_path)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path} for similarity grouping: {e}")
    
    # Filter out groups with only one file
    result = {key: paths for key, paths in name_groups.items() if len(paths) > 1}
    
    logger.info(f"Similarity-based grouping found {len(result)} groups")
    return result


def find_related_files(file_path: str, all_file_paths: List[str]) -> List[str]:
    """
    Find files that are related to the given file based on naming patterns.
    
    Args:
        file_path: Path of the reference file
        all_file_paths: List of all file paths to compare against
        
    Returns:
        List of related file paths
    """
    related_files = []
    ref_base_name, _ = extract_base_name_with_pattern(file_path)
    
    for other_path in all_file_paths:
        if file_path == other_path:
            continue
            
        other_base_name, _ = extract_base_name_with_pattern(other_path)
        
        # Check if the base names match after normalization
        if ref_base_name == other_base_name:
            related_files.append(other_path)
    
    return related_files


def group_files_by_relationships(file_paths: List[str]) -> List[List[str]]:
    """
    Group files based on their naming relationships into lists of potential duplicates.
    
    Args:
        file_paths: List of file paths to group
        
    Returns:
        List of lists, where each inner list contains related file paths
    """
    groups = []
    processed_files = set()
    
    for file_path in file_paths:
        if file_path in processed_files:
            continue
            
        # Find related files for the current file
        related = find_related_files(file_path, file_paths)
        
        # Create a group with the current file and its related files
        group = [file_path] + [f for f in related if f not in processed_files]
        
        if len(group) > 1:  # Only add groups with more than one file
            groups.append(group)
            for f in group:
                processed_files.add(f)
    
    logger.info(f"Relationship-based grouping created {len(groups)} groups")
    return groups


def create_custom_grouping_rules() -> List[Tuple[str, re.Pattern]]:
    """
    Define custom grouping rules using regex patterns.
    
    Returns:
        List of tuples containing (rule_name, compiled_regex_pattern)
    """
    rules = [
        # Rule for files with underscore numbers: abc_1.jpg, abc_2.jpg
        ("underscore_number", re.compile(r'^(.+?)_[0-9]+\.(.+)$')),
        
        # Rule for files with parentheses numbers: abc (1).jpg, abc (2).jpg
        ("parentheses_number", re.compile(r'^(.+?)\([0-9]+\)\.(.+)$')),
        
        # Rule for files with copy/duplicate suffixes: abc copy.jpg, abc (copy).jpg
        ("copy_suffix", re.compile(r'^(.+?)( copy|\(copy\)| duplicate|\(duplicate\))\.(.+)$')),
        
        # Rule for files with version numbers: abc_v1.jpg, abc_v2.jpg
        ("version_number", re.compile(r'^(.+?)_v[0-9]+\.(.+)$')),
        
        # Rule for files with date suffixes: abc_20230101.jpg
        ("date_suffix", re.compile(r'^(.+?)_[0-9]{8}\.(.+)$')),
    ]
    
    return rules


def group_by_custom_rules(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Group files using custom regex rules.
    
    Args:
        file_paths: List of file paths to group
        
    Returns:
        Dictionary mapping rule names and base names to lists of matching file paths
    """
    rules = create_custom_grouping_rules()
    result: Dict[str, List[str]] = {}
    
    for rule_name, pattern in rules:
        # Create a temporary mapping for this rule
        rule_groups: Dict[str, List[str]] = {}
        
        for file_path in file_paths:
            try:
                match = pattern.match(Path(file_path).name)
                if match:
                    # Use the first captured group as the base name
                    base_name = match.group(1)
                    group_key = f"{rule_name}:{base_name}"
                    
                    if group_key not in rule_groups:
                        rule_groups[group_key] = []
                    rule_groups[group_key].append(file_path)
            except Exception as e:
                logger.error(f"Error applying rule {rule_name} to file {file_path}: {e}")
        
        # Add groups with more than one file to the result
        for group_key, group_files in rule_groups.items():
            if len(group_files) > 1:
                result[group_key] = group_files
    
    logger.info(f"Custom rule-based grouping found {len(result)} groups")
    return result