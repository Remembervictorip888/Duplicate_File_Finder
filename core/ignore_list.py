"""
Ignore list module for duplicate detection.

PURPOSE:
This module provides functions to maintain and use an ignore list
to exclude specific files, folders, or patterns from scanning. It allows users
to specify files, directories, file extensions, size ranges, and patterns
that should be excluded from duplicate detection, improving scan performance
and preventing unwanted files from being processed.

RELATIONSHIPS:
- Used by: core.duplicate_detection, main application flow for filtering
- Uses: os, re, pathlib, typing, logging standard libraries
- Provides: Path filtering and ignore functionality
- Called when: Scanning directories to exclude unwanted files/directories

DEPENDENCIES:
- os: For path normalization and file system operations
- re: For pattern matching with regular expressions
- pathlib: For path manipulation
- typing: For type hints (List, Set, Pattern, Union, Tuple)
- logging: For logging operations

USAGE:
Use the IgnoreList class to manage ignore patterns:
    from core.ignore_list import IgnoreList, create_default_ignore_list
    
    # Create a new ignore list
    ignore_list = IgnoreList()
    
    # Add specific files to ignore
    ignore_list.add_file("/path/to/file.txt")
    
    # Add directories to ignore
    ignore_list.add_directory("/path/to/ignore")
    
    # Add patterns to ignore (regex)
    ignore_list.add_pattern(r'\.tmp$')
    
    # Add extensions to ignore
    ignore_list.add_extension('.tmp')
    
    # Add size ranges to ignore (in MB)
    ignore_list.add_size_range(0.0, 0.1)  # Ignore files smaller than 0.1 MB
    
    # Check if a path should be ignored
    should_ignore = ignore_list.is_ignored("/path/to/file.txt")
    
    # Filter a list of paths
    filtered_paths = ignore_list.filter_paths(file_paths)
    
    # Or create a default ignore list
    default_ignore_list = create_default_ignore_list()

This module helps optimize scanning by excluding unnecessary files and directories.
"""
import os
import re
from pathlib import Path
from typing import List, Set, Pattern, Union, Tuple
import logging

logger = logging.getLogger(__name__)


class IgnoreList:
    """
    A class to manage the ignore list functionality.
    """
    
    def __init__(self):
        self.ignored_files: Set[str] = set()
        self.ignored_dirs: Set[str] = set()
        self.ignored_patterns: List[Pattern] = []
        self.ignored_extensions: Set[str] = set()
        self.ignored_sizes: List[Tuple[int, int]] = []  # (min_size, max_size) in bytes
    
    def add_file(self, file_path: str):
        """Add a specific file to the ignore list."""
        self.ignored_files.add(os.path.normpath(file_path))
        logger.info(f"Added file to ignore list: {file_path}")
    
    def add_directory(self, dir_path: str):
        """Add a directory to the ignore list."""
        self.ignored_dirs.add(os.path.normpath(dir_path))
        logger.info(f"Added directory to ignore list: {dir_path}")
    
    def add_pattern(self, pattern: str):
        """Add a regex pattern to the ignore list."""
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.ignored_patterns.append(compiled_pattern)
            logger.info(f"Added pattern to ignore list: {pattern}")
        except re.error as e:
            logger.error(f"Invalid regex pattern: {pattern}, Error: {e}")
    
    def add_extension(self, extension: str):
        """Add a file extension to the ignore list."""
        if not extension.startswith('.'):
            extension = '.' + extension
        self.ignored_extensions.add(extension.lower())
        logger.info(f"Added extension to ignore list: {extension}")
    
    def add_size_range(self, min_size_mb: float, max_size_mb: float):
        """Add a size range to the ignore list (in MB)."""
        min_bytes = int(min_size_mb * 1024 * 1024)
        max_bytes = int(max_size_mb * 1024 * 1024)
        self.ignored_sizes.append((min_bytes, max_bytes))
        logger.info(f"Added size range to ignore list: {min_size_mb}MB - {max_size_mb}MB")
    
    def is_ignored(self, path: str) -> bool:
        """
        Check if a path should be ignored based on the ignore list.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be ignored, False otherwise
        """
        path_obj = Path(path)
        norm_path = os.path.normpath(path)
        
        # Check if it's an exact file match
        if norm_path in self.ignored_files:
            return True
        
        # Check if it's in an ignored directory
        for ignored_dir in self.ignored_dirs:
            try:
                if path_obj.is_relative_to(Path(ignored_dir)):
                    return True
            except ValueError:
                # is_relative_to raises ValueError if paths are on different drives (Windows)
                continue
        
        # Check if the extension is ignored
        if path_obj.suffix.lower() in self.ignored_extensions:
            return True
        
        # Check if it matches any ignored patterns
        for pattern in self.ignored_patterns:
            if pattern.search(path_obj.name):
                return True
        
        # Check if it matches any ignored size ranges
        try:
            file_size = os.path.getsize(path)
            for min_size, max_size in self.ignored_sizes:
                if min_size <= file_size <= max_size:
                    return True
        except (OSError, IOError):
            # If we can't get the file size, we can't ignore based on size
            pass
        
        return False
    
    def filter_paths(self, file_paths: List[str]) -> List[str]:
        """
        Filter a list of paths, removing those that should be ignored.
        
        Args:
            file_paths: List of file paths to filter
            
        Returns:
            List of file paths that are not in the ignore list
        """
        filtered_paths = []
        
        for path in file_paths:
            if not self.is_ignored(path):
                filtered_paths.append(path)
            else:
                logger.debug(f"Ignoring file: {path}")
        
        logger.info(f"Ignore list filtered out {len(file_paths) - len(filtered_paths)} files")
        return filtered_paths
    
    def load_from_file(self, file_path: str):
        """
        Load ignore list from a file.
        
        Args:
            file_path: Path to the ignore list file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('FILE:'):
                            self.add_file(line[5:])
                        elif line.startswith('DIR:'):
                            self.add_directory(line[4:])
                        elif line.startswith('PATTERN:'):
                            self.add_pattern(line[8:])
                        elif line.startswith('EXT:'):
                            self.add_extension(line[4:])
                        elif line.startswith('SIZE:'):
                            parts = line[5:].split('-')
                            if len(parts) == 2:
                                try:
                                    min_mb = float(parts[0])
                                    max_mb = float(parts[1])
                                    self.add_size_range(min_mb, max_mb)
                                except ValueError:
                                    logger.error(f"Invalid size range format: {line}")
                        else:
                            # Default to treating as a pattern
                            self.add_pattern(line)
        except FileNotFoundError:
            logger.warning(f"Ignore list file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading ignore list from {file_path}: {e}")
    
    def save_to_file(self, file_path: str):
        """
        Save ignore list to a file.
        
        Args:
            file_path: Path to save the ignore list file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Ignore List File\n")
                f.write("# Format: FILE:<path>, DIR:<path>, PATTERN:<regex>, EXT:<ext>, SIZE:<min>-<max>\n")
                
                for file_path in self.ignored_files:
                    f.write(f"FILE:{file_path}\n")
                
                for dir_path in self.ignored_dirs:
                    f.write(f"DIR:{dir_path}\n")
                
                for pattern in self.ignored_patterns:
                    f.write(f"PATTERN:{pattern.pattern}\n")
                
                for ext in self.ignored_extensions:
                    f.write(f"EXT:{ext}\n")
                
                for min_size, max_size in self.ignored_sizes:
                    min_mb = min_size / (1024 * 1024)
                    max_mb = max_size / (1024 * 1024)
                    f.write(f"SIZE:{min_mb}-{max_mb}\n")
        except Exception as e:
            logger.error(f"Error saving ignore list to {file_path}: {e}")


def create_default_ignore_list() -> IgnoreList:
    """
    Create a default ignore list with common system files and directories.
    
    Returns:
        An IgnoreList instance with default entries
    """
    ignore_list = IgnoreList()
    
    # Common system directories
    ignore_list.add_directory('$RECYCLE.BIN')
    ignore_list.add_directory('.git')
    ignore_list.add_directory('.svn')
    ignore_list.add_directory('__pycache__')
    ignore_list.add_directory('node_modules')
    ignore_list.add_directory('.vscode')
    ignore_list.add_directory('.idea')
    
    # Common system files
    ignore_list.add_pattern(r'\.tmp$')
    ignore_list.add_pattern(r'\.log$')
    ignore_list.add_pattern(r'\.cache$')
    
    # Common extensions to ignore
    ignore_list.add_extension('.tmp')
    ignore_list.add_extension('.log')
    ignore_list.add_extension('.cache')
    ignore_list.add_extension('.bak')
    
    return ignore_list