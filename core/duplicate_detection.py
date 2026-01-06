"""
Main duplicate detection module.

This module provides functions to find duplicate files using multiple methods:
- Hash comparison
- Filename comparison
- Size comparison
- Pattern matching
- Custom rules
- Advanced grouping
- Size filtering
- Ignore list filtering
"""
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from core.hashing import find_duplicates_by_hash
from core.filename_comparison import (
    find_duplicates_by_filename,
    find_duplicates_by_patterns,
    find_duplicates_by_keywords,
    compare_filenames
)
from core.custom_rules import (
    find_duplicates_by_custom_rules,
    find_duplicates_by_advanced_patterns,
    find_duplicates_by_keyword_groups,
    create_custom_rule_set
)
from core.advanced_grouping import (
    group_by_advanced_patterns,
    group_by_filename_similarity,
    group_files_by_relationships,
    group_by_custom_rules
)
from core.size_filtering import filter_files_by_size
from core.ignore_list import IgnoreList, create_default_ignore_list
from core.scanning import scan_directory_for_files

logger = logging.getLogger(__name__)


def find_duplicates_by_size(file_paths: List[str]) -> Dict[int, List[str]]:
    """
    Find duplicate files by comparing their sizes.
    
    Args:
        file_paths: List of file paths to check for duplicates
        
    Returns:
        Dictionary mapping file sizes to lists of duplicate file paths
    """
    size_map: Dict[int, List[str]] = {}
    
    for file_path in file_paths:
        try:
            size = os.path.getsize(file_path)
            if size not in size_map:
                size_map[size] = []
            size_map[size].append(file_path)
        except (OSError, IOError) as e:
            logger.error(f"Error getting size for file {file_path}: {e}")
    
    # Filter out groups with only one file (no duplicates)
    duplicates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    logger.info(f"Found {len(duplicates)} groups of duplicate files by size")
    
    return duplicates


def find_all_duplicates(
    directory_path: str, 
    extensions: List[str] = None,
    use_hash: bool = True,
    use_filename: bool = True,
    use_size: bool = True,
    use_patterns: bool = True,
    use_custom_rules: bool = False,
    use_advanced_grouping: bool = False,
    min_file_size_mb: float = None,
    max_file_size_mb: float = None,
    ignore_list: IgnoreList = None,
    custom_patterns: List[str] = None,
    keywords: List[str] = None,
    suffix_rules: List[str] = None,
    prefix_rules: List[str] = None,
    containing_rules: List[str] = None,
    regex_rules: List[str] = None,
    image_similarity_threshold: int = 10
) -> Dict[str, Dict[str, List[str]]]:
    """
    Find duplicate files using all available methods.
    
    Args:
        directory_path: Path to the directory to scan
        extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
        use_hash: Whether to use hash-based duplicate detection
        use_filename: Whether to use filename-based duplicate detection
        use_size: Whether to use size-based duplicate detection
        use_patterns: Whether to use pattern-based duplicate detection
        use_custom_rules: Whether to use custom rule-based detection
        use_advanced_grouping: Whether to use advanced grouping methods
        min_file_size_mb: Minimum file size in MB to include (files smaller will be excluded)
        max_file_size_mb: Maximum file size in MB to include (files larger will be excluded)
        ignore_list: IgnoreList instance to filter out files/directories/patterns
        custom_patterns: Custom regex patterns to use for detection
        keywords: Keywords to use for keyword-based detection
        suffix_rules: Filename suffixes to match
        prefix_rules: Filename prefixes to match
        containing_rules: Substrings to look for in filenames
        regex_rules: Regex patterns to match
        image_similarity_threshold: Threshold for image similarity detection (not used in this module)
        
    Returns:
        Dictionary mapping detection method names to their results
    """
    logger.info(f"Starting comprehensive duplicate scan of: {directory_path}")
    
    # First, scan for all files
    all_file_paths = list(scan_directory_for_files(directory_path, extensions))
    logger.info(f"Found {len(all_file_paths)} files before filtering")
    
    # Apply ignore list filtering if provided
    if ignore_list:
        logger.info("Applying ignore list filtering...")
        file_paths = ignore_list.filter_paths(all_file_paths)
        logger.info(f"Files after ignore list filtering: {len(file_paths)}")
    else:
        file_paths = all_file_paths
    
    # Apply size filtering if thresholds are provided
    if min_file_size_mb is not None or max_file_size_mb is not None:
        logger.info(f"Applying size filtering (min: {min_file_size_mb}, max: {max_file_size_mb})")
        file_paths, excluded_by_size = filter_files_by_size(
            file_paths, 
            min_size_mb=min_file_size_mb, 
            max_size_mb=max_file_size_mb
        )
        logger.info(f"Files after size filtering: {len(file_paths)}")
    
    results = {}
    
    if use_hash and file_paths:
        logger.info("Starting hash-based duplicate detection...")
        results['hash'] = find_duplicates_by_hash(file_paths)
    
    if use_size and file_paths:
        logger.info("Starting size-based duplicate detection...")
        results['size'] = find_duplicates_by_size(file_paths)
    
    if use_filename and file_paths:
        logger.info("Starting filename-based duplicate detection...")
        results['filename'] = find_duplicates_by_filename(file_paths)
    
    if use_patterns and file_paths:
        logger.info("Starting pattern-based duplicate detection...")
        results['patterns'] = find_duplicates_by_patterns(file_paths, custom_patterns)
    
    if use_custom_rules and file_paths:
        logger.info("Starting custom rule-based duplicate detection...")
        
        # Create custom rule set
        custom_rules, rule_names = create_custom_rule_set(
            suffix_rules=suffix_rules,
            prefix_rules=prefix_rules,
            containing_rules=containing_rules,
            regex_rules=regex_rules,
            keywords=keywords
        )
        
        results['custom_rules'] = find_duplicates_by_custom_rules(file_paths, custom_rules, rule_names)
        
        # Also add keyword-based groups if keywords were provided
        if keywords:
            keyword_results = find_duplicates_by_keyword_groups(file_paths, keywords)
            # Merge with existing custom rules results
            for key, value in keyword_results.items():
                results['custom_rules'][f'keyword_{key}'] = value
    
    # Additional keyword search (if provided but not using custom rules)
    if keywords and not use_custom_rules and file_paths:
        logger.info("Starting keyword-based duplicate detection...")
        results['keywords'] = find_duplicates_by_keywords(file_paths, keywords)
    
    # Advanced grouping
    if use_advanced_grouping and file_paths:
        logger.info("Starting advanced grouping...")
        results['advanced_grouping'] = group_by_advanced_patterns(file_paths)
        results['advanced_relationships'] = {f"rel_group_{i}": group 
                                            for i, group in enumerate(group_files_by_relationships(file_paths))}
        results['advanced_custom_rules'] = group_by_custom_rules(file_paths)
    
    total_groups = sum(len(groups) for groups in results.values())
    logger.info(f"Completed duplicate detection. Found {total_groups} groups total across all methods")
    
    return results


def merge_duplicate_groups(results: Dict[str, Dict[str, List[str]]]) -> List[List[str]]:
    """
    Merge duplicate groups from different detection methods into unified groups.
    
    Args:
        results: Dictionary of results from different detection methods
        
    Returns:
        List of lists, where each inner list contains paths that are potentially duplicates
    """
    # Create a mapping of file path to the groups it belongs to
    file_to_groups: Dict[str, List[str]] = {}
    
    for method, groups in results.items():
        for group_key, file_list in groups.items():
            for file_path in file_list:
                if file_path not in file_to_groups:
                    file_to_groups[file_path] = []
                # Use method and group key to identify the specific group
                file_to_groups[file_path].append(f"{method}:{group_key}")
    
    # Create a mapping of group ID to files
    group_mapping: Dict[str, List[str]] = {}
    
    # For each file, check which other files share at least one group with it
    for file_path, group_ids in file_to_groups.items():
        # Create a key based on all the groups this file belongs to
        group_key = tuple(sorted(group_ids))
        
        if group_key not in group_mapping:
            group_mapping[group_key] = []
        group_mapping[group_key].append(file_path)
    
    # Return only groups with more than one file
    merged_groups = [group for group in group_mapping.values() if len(group) > 1]
    
    logger.info(f"Merged duplicate detection results into {len(merged_groups)} unified groups")
    return merged_groups


def find_similar_filenames(file_path: str, all_file_paths: List[str]) -> List[str]:
    """
    Find files with similar names to the given file path.
    
    Args:
        file_path: Path of the reference file
        all_file_paths: List of all file paths to compare against
        
    Returns:
        List of similar file paths
    """
    similar_files = []
    ref_filename = Path(file_path).name
    
    for other_path in all_file_paths:
        if file_path == other_path:
            continue
            
        other_filename = Path(other_path).name
        if compare_filenames(ref_filename, other_filename):
            similar_files.append(other_path)
    
    return similar_files