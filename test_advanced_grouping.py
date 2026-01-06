import tempfile
import os
from pathlib import Path
from core.advanced_grouping import (
    group_by_advanced_patterns,
    group_files_by_relationships,
    group_by_custom_rules,
    extract_base_name_with_pattern,
    normalize_for_grouping
)

# Create temporary files for testing
with tempfile.TemporaryDirectory() as tmp_dir:
    # Create test files with various naming patterns that should be grouped
    test_files = [
        'abc.jpg',
        'abc_1.jpg',
        'abc_2.jpg',
        'abc (1).jpg',
        'abc (2).jpg',
        'photo.png',
        'photo_1.png',
        'photo (copy).png',
        'document.pdf',
        'document_v1.pdf',
        'document_v2.pdf',
        'image copy.jpg',
        'image (copy).jpg',
        'special_001.jpg',
        'special_002.jpg',
        'unique_file.txt'
    ]
    
    file_paths = []
    for filename in test_files:
        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, 'w') as f:
            # Write content based on the file type to create actual duplicates where needed
            if 'abc' in filename:
                f.write('abc content')
            elif 'photo' in filename:
                f.write('photo content')
            elif 'document' in filename:
                f.write('document content')
            elif 'image' in filename:
                f.write('image content')
            elif 'special' in filename:
                f.write('special content')
            else:
                f.write('unique content')
        file_paths.append(file_path)
    
    print('Test files created:')
    for path in file_paths:
        print(f'  {Path(path).name}')
    
    # Test advanced grouping functionality
    print('\n--- Testing Advanced Grouping ---')
    
    # Test 1: Advanced pattern grouping
    print('\n1. Testing advanced pattern grouping:')
    results = group_by_advanced_patterns(file_paths)
    for base_name, matches in results.items():
        if matches:
            print(f'  {base_name}: {[Path(f).name for f in matches]}')
    
    # Test 2: Relationship-based grouping
    print('\n2. Testing relationship-based grouping:')
    relationship_results = group_files_by_relationships(file_paths)
    for i, group in enumerate(relationship_results, 1):
        if group:
            print(f'  Group {i}: {[Path(f).name for f in group]}')
    
    # Test 3: Custom rule-based grouping
    print('\n3. Testing custom rule-based grouping:')
    custom_results = group_by_custom_rules(file_paths)
    for rule_name, matches in custom_results.items():
        if matches:
            print(f'  {rule_name}: {[Path(f).name for f in matches]}')
    
    # Test 4: Extract base name with pattern
    print('\n4. Testing base name extraction:')
    for filename in test_files[:6]:  # Test with first few files
        base_name, pattern_type = extract_base_name_with_pattern(filename)
        print(f'  {filename} -> Base: {base_name}, Pattern: {pattern_type}')
    
    # Test 5: Normalize for grouping
    print('\n5. Testing normalization for grouping:')
    for filename in test_files[:6]:  # Test with first few files
        normalized = normalize_for_grouping(filename)
        print(f'  {filename} -> Normalized: {normalized}')

print('\n--- Advanced Grouping Test Complete ---')