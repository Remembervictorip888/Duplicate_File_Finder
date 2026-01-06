import tempfile
import os
from pathlib import Path
from core.filename_comparison import normalize_filename, compare_filenames, find_duplicates_by_filename

# Create temporary files for testing
with tempfile.TemporaryDirectory() as tmp_dir:
    # Create test files with similar names
    test_files = [
        'photo.jpg',
        'photo_1.jpg',
        'photo_2.jpg',
        'image.png',
        'image copy.png',
        'image (copy).png',
        'document.pdf',
        'document (1).pdf',
        'unique_file.txt'
    ]
    
    file_paths = []
    for filename in test_files:
        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
        file_paths.append(file_path)
    
    print('Test files created:')
    for path in file_paths:
        print(f'  {Path(path).name}')
    
    print('\nTesting filename duplicate detection...')
    duplicates = find_duplicates_by_filename(file_paths)
    
    print(f'Found {len(duplicates)} groups of duplicates:')
    for normalized_name, file_group in duplicates.items():
        print(f'  Group "{normalized_name}":')
        for file_path in file_group:
            print(f'    - {Path(file_path).name}')