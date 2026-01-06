import tempfile
import os
from pathlib import Path
from core.size_filtering import filter_files_by_size, get_size_stats
from core.ignore_list import IgnoreList, create_default_ignore_list


def test_size_filtering():
    print("--- Testing Size Filtering ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files with different sizes
        test_files = [
            ('small_file.txt', b'a' * 512),  # ~0.5KB
            ('medium_file.txt', b'b' * (1024 * 1024)),  # 1MB
            ('large_file.txt', b'c' * (5 * 1024 * 1024)),  # 5MB
            ('xlarge_file.txt', b'd' * (10 * 1024 * 1024)),  # 10MB
        ]
        
        file_paths = []
        for filename, content in test_files:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(content)
            file_paths.append(file_path)
        
        print('Test files created:')
        for path in file_paths:
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f'  {Path(path).name} ({size_mb:.2f} MB)')
        
        # Test size filtering: only files between 0.5MB and 6MB
        filtered, excluded = filter_files_by_size(file_paths, min_size_mb=0.5, max_size_mb=6.0)
        
        print(f'\nAfter filtering (0.5MB to 6MB):')
        print(f'  Included: {[Path(f).name for f in filtered]}')
        print(f'  Excluded: {[Path(f).name for f in excluded]}')
        
        # Get size stats
        min_size, max_size, avg_size = get_size_stats(file_paths)
        print(f'\nSize stats: min={min_size:.2f}MB, max={max_size:.2f}MB, avg={avg_size:.2f}MB')


def test_ignore_list():
    print('\n--- Testing Ignore List ---')
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a directory structure
        subdir = os.path.join(tmp_dir, 'subdir')
        os.makedirs(subdir)
        
        # Create test files
        test_files = [
            'normal_file.txt',
            'ignored_file.tmp',
            'log_file.log',
            os.path.join('subdir', 'nested_file.txt'),
            os.path.join('subdir', 'ignored_nested.tmp')
        ]
        
        file_paths = []
        for filename in test_files:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f'content of {filename}')
            file_paths.append(file_path)
        
        print('Test files created:')
        for path in file_paths:
            print(f'  {Path(path).relative_to(tmp_dir)}')
        
        # Create ignore list and add some rules
        ignore_list = IgnoreList()
        ignore_list.add_extension('.tmp')
        ignore_list.add_extension('.log')
        ignore_list.add_pattern(r'_temp$')  # Files ending with _temp
        
        # Test filtering
        filtered_paths = ignore_list.filter_paths(file_paths)
        
        print(f'\nAfter applying ignore rules:')
        print(f'  Included: {[str(Path(f).relative_to(tmp_dir)) for f in filtered_paths]}')
        print(f'  Excluded by ignore list: {len(file_paths) - len(filtered_paths)} files')
        
        # Test creating default ignore list
        print(f'\nTesting default ignore list:')
        default_ignore = create_default_ignore_list()
        print(f'  Default ignore list has {len(default_ignore.ignored_dirs)} directories, '
              f'{len(default_ignore.ignored_extensions)} extensions, '
              f'{len(default_ignore.ignored_patterns)} patterns')


def test_ignore_list_with_file():
    print('\n--- Testing Ignore List with File ---')
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        test_files = [
            'file1.jpg',
            'file2.png',
            'temp_file.tmp',
            'log_file.log'
        ]
        
        file_paths = []
        for filename in test_files:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f'content of {filename}')
            file_paths.append(file_path)
        
        # Create an ignore list file
        ignore_file_path = os.path.join(tmp_dir, 'ignore_list.txt')
        with open(ignore_file_path, 'w') as f:
            f.write("# Test ignore list\n")
            f.write("EXT:.tmp\n")
            f.write("EXT:.log\n")
            f.write("PATTERN:temp_\n")
        
        # Test loading from file
        ignore_list = IgnoreList()
        ignore_list.load_from_file(ignore_file_path)
        
        filtered = ignore_list.filter_paths(file_paths)
        
        print(f'Original files: {[Path(f).name for f in file_paths]}')
        print(f'After applying ignore list from file: {[Path(f).name for f in filtered]}')
        
        # Test saving to file
        save_file_path = os.path.join(tmp_dir, 'saved_ignore_list.txt')
        ignore_list.add_extension('.bak')
        ignore_list.save_to_file(save_file_path)
        
        print(f'Ignore list saved to: {save_file_path}')
        
        # Verify saved file exists and has content
        if os.path.exists(save_file_path):
            with open(save_file_path, 'r') as f:
                content = f.read()
                print(f'Saved file has {len(content)} characters')


if __name__ == "__main__":
    test_size_filtering()
    test_ignore_list()
    test_ignore_list_with_file()
    print('\n--- All Tests Complete ---')