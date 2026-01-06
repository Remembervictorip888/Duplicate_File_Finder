"""
Duplicate File Finder Application.

This application finds and manages duplicate files based on content and visual similarity.
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
import logging
import argparse

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from utils.config import Config
from core.scanning import scan_directory_for_duplicates
from core.hashing import find_duplicates_by_hash
from core.image_similarity import find_similar_images, find_exact_duplicate_images
from core.file_operations import safe_delete_files, auto_select_duplicates_for_deletion


def main():
    """
    Main entry point for the duplicate file finder application.
    """
    # Setup logging
    logger = setup_logger('duplicate_finder', 'app.log', logging.INFO)
    logger.info("Starting Duplicate File Finder Application")
    
    # Load configuration
    config = Config()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Find and manage duplicate files')
    parser.add_argument('directory', nargs='?', help='Directory to scan for duplicates')
    parser.add_argument('--strategy', choices=['oldest', 'newest', 'lowest_res'], 
                       default=config.get('auto_select_strategy', 'oldest'),
                       help='Auto-selection strategy for duplicates')
    parser.add_argument('--delete', action='store_true', 
                       help='Actually delete the selected duplicates')
    parser.add_argument('--similarity', type=int, default=config.get('image_similarity_threshold', 5),
                       help='Threshold for image similarity (0-20, lower = more similar)')
    
    args = parser.parse_args()
    
    # If no directory provided, use the last scanned directory or current directory
    scan_directory = args.directory
    if not scan_directory:
        scan_directory = config.get('last_scan_directory', '.')
    
    # Validate directory
    if not Path(scan_directory).is_dir():
        logger.error(f"Directory does not exist: {scan_directory}")
        sys.exit(1)
    
    # Update config with the current directory
    config.set('last_scan_directory', scan_directory)
    config.save_config()
    
    logger.info(f"Scanning directory: {scan_directory}")
    
    # Scan for files
    file_paths, total_files = scan_directory_for_duplicates(scan_directory)
    logger.info(f"Found {total_files} files to process")
    
    # Separate image files from other files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    image_files = [f for f in file_paths if Path(f).suffix.lower() in image_extensions]
    other_files = [f for f in file_paths if Path(f).suffix.lower() not in image_extensions]
    
    logger.info(f"Processing {len(image_files)} images and {len(other_files)} other files")
    
    # Find duplicates by hash for non-image files
    hash_duplicates = {}
    if other_files:
        logger.info("Finding duplicates by hash for non-image files...")
        hash_duplicates = find_duplicates_by_hash(other_files)
        logger.info(f"Found {len(hash_duplicates)} groups of hash duplicates")
    
    # Find exact duplicate images
    image_duplicates = {}
    if image_files:
        logger.info("Finding exact duplicate images...")
        image_duplicates = find_exact_duplicate_images(image_files)
        logger.info(f"Found {len(image_duplicates)} groups of exact image duplicates")
        
        # Find similar images (visual similarity)
        logger.info(f"Finding visually similar images (threshold: {args.similarity})...")
        similar_image_groups = find_similar_images(image_files, args.similarity)
        logger.info(f"Found {len(similar_image_groups)} groups of visually similar images")
    
    # Combine all duplicate groups
    all_duplicate_groups = []
    
    # Add hash duplicates
    for hash_val, file_list in hash_duplicates.items():
        if len(file_list) > 1:
            all_duplicate_groups.append(file_list)
    
    # Add image duplicates
    for hash_val, file_list in image_duplicates.items():
        if len(file_list) > 1:
            all_duplicate_groups.append(file_list)
    
    # Add visually similar images
    for group in similar_image_groups:
        if len(group) > 1:
            all_duplicate_groups.append(group)
    
    # Print results
    print(f"\n--- Duplicate File Analysis Results ---")
    print(f"Total files scanned: {total_files}")
    print(f"Non-image duplicates: {len(hash_duplicates)} groups")
    print(f"Exact image duplicates: {len(image_duplicates)} groups")
    print(f"Visually similar images: {len(similar_image_groups)} groups")
    print(f"Total duplicate groups: {len(all_duplicate_groups)}")
    
    # Auto-select files for deletion based on strategy
    if all_duplicate_groups:
        files_to_delete = auto_select_duplicates_for_deletion(all_duplicate_groups, args.strategy)
        print(f"Auto-selected {len(files_to_delete)} files for deletion using '{args.strategy}' strategy")
        
        # Show the files that would be deleted (without actually deleting)
        print("\nFiles that would be deleted:")
        for i, file_path in enumerate(files_to_delete[:10]):  # Show first 10
            print(f"  {i+1}. {file_path}")
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
    
    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()