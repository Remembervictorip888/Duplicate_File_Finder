import tempfile
import os
from pathlib import Path
from core.duplicate_detection import find_all_duplicates

# Create temporary files for testing
with tempfile.TemporaryDirectory() as tmp_dir:
    # Create test files with similar names and some actual duplicates (same content)
    test_files = [
        'photo.jpg',
        'photo_1.jpg',
        'photo_2.jpg',
        'image.png',
        'image copy.png',
        'document.pdf',
        'document (1).pdf',
        'unique_file.txt'
    ]
    
    file_paths = []
    for filename in test_files:
        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, 'w') as f:
            # Write the same content to related files to test hash detection too
            if 'photo' in filename:
                f.write('photo content')
            elif 'image' in filename:
                f.write('image content')
            elif 'document' in filename:
                f.write('document content')
            else:
                f.write('unique content')
        file_paths.append(file_path)
    
    print('Test files created:')
    for path in file_paths:
        print(f'  {Path(path).name}')
    
    print('\nTesting full duplicate detection...')
    results = find_all_duplicates(
        tmp_dir,
        use_hash=True,
        use_filename=True,
        use_size=True,
        use_patterns=True
    )
    
    for method, groups in results.items():
        print(f'\n{method.capitalize()} method found {len(groups)} groups:')
        for group_key, file_list in groups.items():
            print(f'  Group {group_key}: {[Path(f).name for f in file_list]}')