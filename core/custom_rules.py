"""
Custom Rules module for duplicate detection.

This module provides functions to create and apply custom rules for detecting duplicate files
based on user-defined patterns, keywords, and naming conventions.
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple, Callable, Any
import logging

logger = logging.getLogger(__name__)


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


def find_duplicates_by_custom_rules(
    file_paths: List[str],
    custom_rules: List[Callable[[str], bool]] = None,
    rule_names: List[str] = None
) -> Dict[str, List[str]]:
    """
    Find duplicate files using custom rules defined by the user.
    
    Args:
        file_paths: List of file paths to check for duplicates
        custom_rules: List of functions that take a filename and return True if it matches the rule
        rule_names: Optional names for the rules to use as keys in the result dictionary
        
    Returns:
        Dictionary mapping rule names to lists of matching file paths
    """
    rule_groups: Dict[str, List[str]] = {}
    
    if not custom_rules:
        return rule_groups
    
    # If rule names aren't provided, create default names
    if not rule_names:
        rule_names = [f"custom_rule_{i}" for i in range(len(custom_rules))]
    
    # Apply each rule to the file paths
    for rule, rule_name in zip(custom_rules, rule_names):
        matching_files = []
        
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                if rule(filename):
                    matching_files.append(file_path)
            except Exception as e:
                logger.error(f"Error applying custom rule {rule_name} to file {file_path}: {e}")
        
        if len(matching_files) > 1:  # Only include groups with potential duplicates
            rule_groups[rule_name] = matching_files
    
    logger.info(f"Applied {len(custom_rules)} custom rules and found {len(rule_groups)} rule groups")
    
    return rule_groups


def create_advanced_pattern_rule(
    pattern_type: str,
    pattern_value: str,
    match_case: bool = False,
    whole_name: bool = True
) -> Callable[[str], bool]:
    """
    Create an advanced pattern matching rule.
    
    Args:
        pattern_type: Type of pattern ('suffix', 'prefix', 'contains', 'regex', 'exact')
        pattern_value: The pattern value to match
        match_case: Whether to match case sensitively
        whole_name: Whether to match against the whole filename or just the stem
        
    Returns:
        A function that takes a filename and returns True if it matches the pattern
    """
    if pattern_type == 'suffix':
        def rule(filename: str) -> bool:
            name = filename if whole_name else Path(filename).stem
            return name.lower().endswith(pattern_value.lower()) if not match_case else name.endswith(pattern_value)
        return rule
    
    elif pattern_type == 'prefix':
        def rule(filename: str) -> bool:
            name = filename if whole_name else Path(filename).stem
            return name.lower().startswith(pattern_value.lower()) if not match_case else name.startswith(pattern_value)
        return rule
    
    elif pattern_type == 'contains':
        def rule(filename: str) -> bool:
            name = filename if whole_name else Path(filename).stem
            return pattern_value.lower() in name.lower() if not match_case else pattern_value in name
        return rule
    
    elif pattern_type == 'regex':
        flags = 0 if match_case else re.IGNORECASE
        compiled_pattern = re.compile(pattern_value, flags)
        
        def rule(filename: str) -> bool:
            name = filename if whole_name else Path(filename).stem
            return bool(compiled_pattern.search(name))
        return rule
    
    elif pattern_type == 'exact':
        def rule(filename: str) -> bool:
            name = filename if whole_name else Path(filename).stem
            return name.lower() == pattern_value.lower() if not match_case else name == pattern_value
        return rule
    
    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")


def find_duplicates_by_advanced_patterns(
    file_paths: List[str],
    patterns: List[Tuple[str, str]]  # List of (pattern_type, pattern_value) tuples
) -> Dict[str, List[str]]:
    """
    Find duplicate files using advanced pattern matching.
    
    Args:
        file_paths: List of file paths to check for duplicates
        patterns: List of (pattern_type, pattern_value) tuples
        
    Returns:
        Dictionary mapping pattern names to lists of matching file paths
    """
    pattern_groups: Dict[str, List[str]] = {}
    
    for i, (pattern_type, pattern_value) in enumerate(patterns):
        try:
            rule = create_advanced_pattern_rule(pattern_type, pattern_value)
            matching_files = []
            
            for file_path in file_paths:
                try:
                    filename = Path(file_path).name
                    if rule(filename):
                        matching_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error applying pattern {pattern_type}:{pattern_value} to file {file_path}: {e}")
            
            if len(matching_files) > 1:  # Only include groups with potential duplicates
                pattern_name = f"pattern_{i}_{pattern_type}_{pattern_value}"
                pattern_groups[pattern_name] = matching_files
                
        except Exception as e:
            logger.error(f"Error creating pattern rule for {pattern_type}:{pattern_value}: {e}")
    
    logger.info(f"Applied {len(patterns)} advanced patterns and found {len(pattern_groups)} pattern groups")
    
    return pattern_groups


def create_keyword_based_grouping(
    keywords: List[str],
    match_case: bool = False
) -> Callable[[List[str]], Dict[str, List[str]]]:
    """
    Create a function that groups files based on keywords in their names.
    
    Args:
        keywords: List of keywords to search for in filenames
        match_case: Whether to match case sensitively
        
    Returns:
        A function that takes a list of file paths and returns a dictionary of keyword groups
    """
    def grouping_function(file_paths: List[str]) -> Dict[str, List[str]]:
        keyword_groups: Dict[str, List[str]] = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            matching_files = []
            
            for file_path in file_paths:
                try:
                    path_obj = Path(file_path)
                    name = path_obj.name
                    if (keyword_lower in name.lower()) if not match_case else (keyword in name):
                        matching_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error checking keyword {keyword} in file {file_path}: {e}")
            
            if len(matching_files) > 1:  # Only include groups with potential duplicates
                keyword_groups[keyword] = matching_files
        
        return keyword_groups
    
    return grouping_function


def find_duplicates_by_keyword_groups(
    file_paths: List[str],
    keywords: List[str],
    match_case: bool = False
) -> Dict[str, List[str]]:
    """
    Find duplicate files based on keywords in their names.
    
    Args:
        file_paths: List of file paths to check
        keywords: List of keywords to search for in filenames
        match_case: Whether to match case sensitively
        
    Returns:
        Dictionary mapping keywords to lists of matching file paths
    """
    grouping_function = create_keyword_based_grouping(keywords, match_case)
    return grouping_function(file_paths)


def create_custom_grouping_function(
    grouping_logic: Callable[[str], str]
) -> Callable[[List[str]], Dict[str, List[str]]]:
    """
    Create a custom grouping function using custom logic.
    
    Args:
        grouping_logic: A function that takes a filename and returns a group key
        
    Returns:
        A function that takes a list of file paths and returns grouped results
    """
    def grouping_function(file_paths: List[str]) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                group_key = grouping_logic(filename)
                
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(file_path)
            except Exception as e:
                logger.error(f"Error applying grouping logic to file {file_path}: {e}")
        
        # Filter out groups with only one file
        return {key: value for key, value in groups.items() if len(value) > 1}
    
    return grouping_function


def apply_custom_grouping(
    file_paths: List[str],
    grouping_function: Callable[[List[str]], Dict[str, List[str]]]
) -> Dict[str, List[str]]:
    """
    Apply a custom grouping function to file paths.
    
    Args:
        file_paths: List of file paths to group
        grouping_function: A function that groups file paths
        
    Returns:
        Dictionary of grouped file paths
    """
    try:
        return grouping_function(file_paths)
    except Exception as e:
        logger.error(f"Error applying custom grouping function: {e}")
        return {}


def create_custom_rule_set(
    suffix_rules: List[str] = None,
    prefix_rules: List[str] = None,
    containing_rules: List[str] = None,
    regex_rules: List[str] = None,
    keywords: List[str] = None
) -> Tuple[List[Callable[[str], bool]], List[str]]:
    """
    Create a comprehensive set of custom rules based on different criteria.
    
    Args:
        suffix_rules: List of filename suffixes to match
        prefix_rules: List of filename prefixes to match
        containing_rules: List of substrings to look for in filenames
        regex_rules: List of regex patterns to match
        keywords: List of keywords to search for
        
    Returns:
        Tuple of (list of rule functions, list of rule names)
    """
    rules = []
    rule_names = []
    
    # Add suffix rules
    if suffix_rules:
        for i, suffix in enumerate(suffix_rules):
            rules.append(create_filename_ending_rule(suffix))
            rule_names.append(f"suffix_rule_{i}_{suffix}")
    
    # Add prefix rules
    if prefix_rules:
        for i, prefix in enumerate(prefix_rules):
            rules.append(create_filename_starting_rule(prefix))
            rule_names.append(f"prefix_rule_{i}_{prefix}")
    
    # Add containing rules
    if containing_rules:
        for i, contains in enumerate(containing_rules):
            rules.append(create_filename_containing_rule(contains))
            rule_names.append(f"contains_rule_{i}_{contains}")
    
    # Add regex rules
    if regex_rules:
        for i, pattern in enumerate(regex_rules):
            rules.append(create_custom_regex_rule(pattern))
            rule_names.append(f"regex_rule_{i}_{pattern}")
    
    # Add keyword rules
    if keywords:
        for i, keyword in enumerate(keywords):
            rules.append(create_filename_containing_rule(keyword))
            rule_names.append(f"keyword_rule_{i}_{keyword}")
    
    return rules, rule_names