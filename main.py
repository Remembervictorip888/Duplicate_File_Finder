"""
Duplicate File Finder - Main Application

This script provides a command-line interface for finding and managing duplicate files.
"""
import sys
import os
from pathlib import Path
from typing import List, Dict
import logging
import argparse
import datetime

from utils.logger import setup_logger
from utils.config import Config
from core.duplicate_detection import find_all_duplicates, merge_duplicate_groups, find_all_duplicates_with_models
from core.file_operations import safe_delete_files, auto_select_duplicates_for_deletion
from core.ignore_list import IgnoreList, create_default_ignore_list
from core.scan_history import ScanHistory
from core.settings_manager import SettingsManager
from core.models import ScanResult, ScanSettings
from datetime import datetime as dt


def main():
    """
    Main entry point for the duplicate file finder application.
    """
    # Generate a timestamped log filename for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"scan_run_{timestamp}.log"
    
    # Setup logging
    logger = setup_logger('duplicate_finder', log_filename, logging.INFO)
    logger.info("Starting Duplicate File Finder Application")
    
    # Load configuration
    config = Config()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Find and manage duplicate files')
    parser.add_argument('directory', nargs='?', help='Directory to scan for duplicates')
    parser.add_argument('--strategy', choices=['oldest', 'newest', 'lowest_res'], 
                       default=config.get('auto_select_strategy', 'oldest'),
                       help='Strategy for auto-selecting duplicates for deletion')
    parser.add_argument('--delete', action='store_true', 
                       help='Actually delete the auto-selected duplicates (moves to Recycle Bin)')
    parser.add_argument('--similarity', type=int, default=config.get('image_similarity_threshold', 10), 
                       help='Similarity threshold for images (0-20, lower = more similar)')
    parser.add_argument('--extensions', nargs='+', 
                       help='File extensions to include in the scan (e.g., .jpg .png .mp4)')
    parser.add_argument('--method', choices=['hash', 'filename', 'size', 'all'], 
                       default='all',
                       help='Method to use for duplicate detection')
    parser.add_argument('--use-custom-rules', action='store_true',
                       help='Enable custom rule-based duplicate detection')
    parser.add_argument('--use-advanced-grouping', action='store_true',
                       help='Enable advanced grouping of potential duplicates based on naming patterns')
    parser.add_argument('--min-size', type=float,
                       help='Minimum file size in MB to include in scan')
    parser.add_argument('--max-size', type=float,
                       help='Maximum file size in MB to include in scan')
    parser.add_argument('--ignore-list-file', 
                       help='Path to a file containing ignore patterns')
    parser.add_argument('--export-settings', 
                       help='Export current settings to a file')
    parser.add_argument('--import-settings', 
                       help='Import settings from a file')
    parser.add_argument('--suffix-rules', nargs='+', 
                       help='Filename suffixes to match (e.g., _1 _copy)')
    parser.add_argument('--prefix-rules', nargs='+', 
                       help='Filename prefixes to match')
    parser.add_argument('--containing-rules', nargs='+', 
                       help='Substrings to look for in filenames')
    parser.add_argument('--regex-rules', nargs='+', 
                       help='Regex patterns to match in filenames')
    parser.add_argument('--keywords', nargs='+', 
                       help='Keywords to search for in filenames')
    
    args = parser.parse_args()
    
    # Handle settings import/export before loading config
    settings_manager = SettingsManager()
    
    if args.import_settings:
        if settings_manager.import_settings(args.import_settings):
            settings_manager.save_settings()
            print(f"Settings imported from {args.import_settings}")
            return 0
        else:
            print(f"Failed to import settings from {args.import_settings}")
            return 1
    
    if args.export_settings:
        if settings_manager.export_settings(args.export_settings):
            print(f"Settings exported to {args.export_settings}")
            return 0
        else:
            print(f"Failed to export settings to {args.export_settings}")
            return 1
    
    # If no directory provided, use the last scanned directory or current directory
    scan_directory = args.directory
    if not scan_directory:
        scan_directory = config.get('last_scan_directory', '.')
    
    # Validate directory
    if not Path(scan_directory).is_dir():
        logger.error(f"Directory does not exist: {scan_directory}")
        return 1
    
    # Update config with the current directory
    config.set('last_scan_directory', scan_directory)
    config.save_config()
    
    # Set up ignore list
    ignore_list = create_default_ignore_list()
    if args.ignore_list_file and os.path.exists(args.ignore_list_file):
        ignore_list.load_from_file(args.ignore_list_file)
        logger.info(f"Loaded ignore list from: {args.ignore_list_file}")
    
    logger.info(f"Scanning directory: {scan_directory}")
    
    # Convert method argument to boolean flags
    use_hash = args.method in ['hash', 'all']
    use_filename = args.method in ['filename', 'all']
    use_size = args.method in ['size', 'all']
    use_patterns = args.method in ['all']  # Patterns are used with 'all' method
    use_custom_rules = args.use_custom_rules
    use_advanced_grouping = args.use_advanced_grouping
    
    # Use settings or command line arguments for configuration
    min_size = args.min_size if args.min_size is not None else settings_manager.get_setting('min_file_size_mb')
    max_size = args.max_size if args.max_size is not None else settings_manager.get_setting('max_file_size_mb')
    
    # Use settings for rules if not provided via command line
    suffix_rules = args.suffix_rules or settings_manager.get_setting('suffix_rules', [])
    prefix_rules = args.prefix_rules or settings_manager.get_setting('prefix_rules', [])
    containing_rules = args.containing_rules or settings_manager.get_setting('containing_rules', [])
    regex_rules = args.regex_rules or settings_manager.get_setting('regex_rules', [])
    keywords = args.keywords or settings_manager.get_setting('keywords', [])
    
    # Create scan settings model
    scan_settings = ScanSettings(
        directory=Path(scan_directory),
        extensions=args.extensions or settings_manager.get_setting('default_extensions'),
        use_hash=use_hash,
        use_filename=use_filename,
        use_size=use_size,
        use_patterns=use_patterns,
        use_custom_rules=use_custom_rules or settings_manager.get_setting('use_custom_rules', False),
        use_advanced_grouping=use_advanced_grouping or settings_manager.get_setting('use_advanced_grouping', False),
        min_file_size_mb=min_size,
        max_file_size_mb=max_size,
        suffix_rules=suffix_rules,
        prefix_rules=prefix_rules,
        containing_rules=containing_rules,
        regex_rules=regex_rules,
        keywords=keywords,
        image_similarity_threshold=args.similarity
    )
    
    # Run duplicate detection with models
    start_time = dt.now()
    duplicate_groups = find_all_duplicates_with_models(scan_settings)
    end_time = dt.now()
    
    # Create scan result model
    scanned_files_count = len(list(Path(scan_directory).rglob('*')))
    methods_used = []
    if use_hash: methods_used.append('hash')
    if use_size: methods_used.append('size')
    if use_filename: methods_used.append('filename')
    if use_custom_rules: methods_used.append('custom_rules')
    if use_advanced_grouping: methods_used.append('advanced_grouping')
    
    scan_result = ScanResult(
        directory=scan_settings.directory,
        scanned_files_count=scanned_files_count,
        duplicate_groups=duplicate_groups,
        scan_start_time=start_time,
        scan_end_time=end_time,
        scan_duration=(end_time - start_time).total_seconds(),
        methods_used=methods_used
    )
    
    # Create scan history record using the new database
    scan_history = ScanHistory()
    scan_id = scan_history.add_scan_result(scan_result)
    
    print(f"\nScan Results:")
    print(f"Found {len(duplicate_groups)} groups of duplicate files")
    
    # Show summary of results by method
    method_counts = {}
    for group in duplicate_groups:
        method = group.detection_method
        if method not in method_counts:
            method_counts[method] = 0
        method_counts[method] += 1
    
    for method, count in method_counts.items():
        print(f"{method.capitalize()} method: {count} groups")
    
    if duplicate_groups:
        print(f"\nDetailed Results:")
        for i, group in enumerate(duplicate_groups, 1):
            if len(group.files) > 1:  # Only show groups with actual duplicates
                print(f"\nGroup {i} (Method: {group.detection_method}):")
                for file_info in sorted(group.files, key=lambda f: str(f.path)):  # Sort files for consistent output
                    print(f"  - {file_info.path} ({file_info.size} bytes)")
    
    # Auto-select files for deletion based on the chosen strategy
    if duplicate_groups:
        # Convert DuplicateGroup models to the format expected by auto_select_duplicates_for_deletion
        duplicate_groups_paths = [[str(file_info.path) for file_info in group.files] 
                                  for group in duplicate_groups if len(group.files) > 1]
        
        files_to_delete = auto_select_duplicates_for_deletion(duplicate_groups_paths, strategy=args.strategy)
        
        if files_to_delete:
            print(f"\nAuto-selected {len(files_to_delete)} files for deletion using '{args.strategy}' strategy:")
            for i, filepath in enumerate(sorted(files_to_delete)[:10]):  # Show first 10, sorted
                print(f"  {i+1}. {filepath}")
            if len(files_to_delete) > 10:
                print(f"  ... and {len(files_to_delete) - 10} more")
            
            # Actually delete if requested
            if args.delete:
                print(f"\nMoving {len(files_to_delete)} files to Recycle Bin...")
                successful, failed = safe_delete_files(files_to_delete)
                print(f"Successfully moved {len(successful)} files to Recycle Bin")
                if failed:
                    print(f"Failed to move {len(failed)} files: {failed}")
            else:
                print(f"\nUse --delete flag to actually move these files to Recycle Bin")
        else:
            print(f"\nNo files were selected for deletion using '{args.strategy}' strategy.")
    
    logger.info("Application completed successfully")
    return 0


if __name__ == "__main__":
    exit(main())