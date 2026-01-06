"""
Image similarity module for visual duplicate detection.

PURPOSE:
This module provides functions to find visually similar images using perceptual hashing.
It implements algorithms that can detect images that look similar but may have different
file content (e.g., different formats, compression levels, or minor edits) by using
perceptual hashing techniques that are robust to minor changes.

RELATIONSHIPS:
- Used by: core.duplicate_detection for image similarity detection
- Uses: imagehash, PIL (Pillow), core.hashing for file size checks
- Provides: Visual similarity detection for image files
- Called when: Image similarity detection is enabled in scan settings

DEPENDENCIES:
- imagehash: For perceptual hashing algorithms
- PIL (Pillow): For image processing
- pathlib: For path manipulation
- typing: For type hints (List, Dict, Tuple)
- logging: For logging operations
- core.hashing: For file size checks

USAGE:
Use the main functions to detect similar images:
    from core.image_similarity import calculate_image_hash, find_similar_images, find_exact_duplicate_images
    
    # Calculate perceptual hash for an image
    img_hash = calculate_image_hash("/path/to/image.jpg")
    
    # Find visually similar images
    similar_groups = find_similar_images(image_paths, threshold=5)
    
    # Find exact duplicate images
    exact_duplicates = find_exact_duplicate_images(image_paths)

This module is particularly useful for finding image duplicates that may have different
file content but visually appear the same or very similar.
"""
import imagehash
from PIL import Image
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from .hashing import get_file_size

logger = logging.getLogger(__name__)


def calculate_image_hash(image_path: str, hash_size: int = 8) -> str:
    """
    Calculate perceptual hash for an image.
    
    Args:
        image_path: Path to the image file
        hash_size: Size of the hash (default 8 for 64-bit hash)
        
    Returns:
        Hex digest of the image's perceptual hash, or empty string if error
    """
    try:
        # Only process if it's a valid image file
        with Image.open(image_path) as img:
            # Calculate the perceptual hash
            hash_value = imagehash.average_hash(img, hash_size)
            return str(hash_value)
    except Exception as e:
        logger.error(f"Error calculating hash for image {image_path}: {e}")
        return ""


def find_similar_images(image_paths: List[str], threshold: int = 5) -> List[List[str]]:
    """
    Find visually similar images based on perceptual hashing.
    
    Args:
        image_paths: List of image file paths to compare
        threshold: Maximum hamming distance to consider images similar (default 5)
        
    Returns:
        List of lists, where each inner list contains paths to similar images
    """
    # Calculate hashes for all images
    image_hashes = []
    
    for i, img_path in enumerate(image_paths):
        img_hash = calculate_image_hash(img_path)
        if img_hash:
            image_hashes.append((img_path, img_hash))
            
        # Log progress every 100 images
        if (i + 1) % 100 == 0:
            logger.info(f"Calculated hashes for {i + 1}/{len(image_paths)} images")
    
    logger.info(f"Calculated {len(image_hashes)} image hashes")
    
    # Group similar images
    similar_groups = []
    processed = set()
    
    for i, (img1_path, img1_hash) in enumerate(image_hashes):
        if img1_path in processed:
            continue
            
        current_group = [img1_path]
        processed.add(img1_path)
        
        # Compare with remaining images
        for j in range(i + 1, len(image_hashes)):
            img2_path, img2_hash = image_hashes[j]
            
            if img2_path in processed:
                continue
                
            # Calculate hamming distance between hashes
            try:
                hash1 = imagehash.hex_to_hash(img1_hash)
                hash2 = imagehash.hex_to_hash(img2_hash)
                distance = hash1 - hash2  # Hamming distance
                
                if distance <= threshold:
                    current_group.append(img2_path)
                    processed.add(img2_path)
            except Exception as e:
                logger.error(f"Error comparing hashes for {img1_path} and {img2_path}: {e}")
        
        # Only add groups with more than one image
        if len(current_group) > 1:
            similar_groups.append(current_group)
    
    logger.info(f"Found {len(similar_groups)} groups of similar images")
    return similar_groups


def find_exact_duplicate_images(image_paths: List[str]) -> Dict[str, List[str]]:
    """
    Find exact duplicate images by comparing their hashes.
    
    Args:
        image_paths: List of image file paths to check for duplicates
        
    Returns:
        Dictionary mapping hash values to lists of duplicate image paths
    """
    hash_map = {}
    
    for i, img_path in enumerate(image_paths):
        # First check file size - if it's 0, skip it
        size = get_file_size(img_path)
        if size == 0:
            continue
            
        img_hash = calculate_image_hash(img_path)
        if img_hash:
            if img_hash not in hash_map:
                hash_map[img_hash] = []
            hash_map[img_hash].append(img_path)
            
            # Log progress every 1000 images
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1}/{len(image_paths)} images for hashing")
    
    # Filter out unique images (those with only one path for a hash)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    logger.info(f"Found {len(duplicates)} groups of exact duplicate images")
    
    return duplicates