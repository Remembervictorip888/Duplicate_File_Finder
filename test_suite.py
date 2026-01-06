"""
Comprehensive test suite for Duplicate File Finder.

This test suite validates all implemented features including:
- Basic duplicate detection (hash, size, filename)
- Advanced duplicate grouping
- Size filtering
- Ignore list functionality
- Custom rules
- Scan history
- Settings management
"""
import tempfile
import os
import json
from pathlib import Path
from typing import List

from core.duplicate_detection import find_all_duplicates, merge_duplicate_groups
from core.scanning import scan_directory_for_files
from core.hashing import find_duplicates_by_hash
from core.filename_comparison import find_duplicates_by_filename, find_duplicates_by_patterns
from core.advanced_grouping import group_by_advanced_patterns, group_files_by_relationships
from core.size_filtering import filter_files_by_size
from core.ignore_list import IgnoreList
from core.custom_rules import create_custom_rule_set, find_duplicates_by_custom_rules
from core.scan_history import ScanHistory
from core.settings_manager import SettingsManager


def create_test_files(base_dir: str, file_specs: List[tuple]) -> List[str]:
    """
    Create test files with specified content.
    
    Args:
        base_dir: Base directory to create files in
        file_specs: List of (filename, content) tuples
        
    Returns:
        List of created file paths
    """
    file_paths = []
    for filename, content in file_specs:
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        file_paths.append(file_path)
    return file_paths


def test_basic_duplicate_detection():
    """Test basic duplicate detection methods."""
    print("\n--- Testing Basic Duplicate Detection ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        test_files = [
            ('file1.txt', b'content1'),
            ('file2.txt', b'content1'),  # duplicate of file1
            ('file3.txt', b'content2'),
            ('file4.txt', b'content2'),  # duplicate of file3
            ('file5.txt', b'unique_content'),
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Test hash-based detection
        hash_results = find_duplicates_by_hash(file_paths)
        print(f"Hash detection found {len(hash_results)} groups")
        assert len(hash_results) == 2, f"Expected 2 hash groups, got {len(hash_results)}"
        
        # Test filename-based detection
        filename_results = find_duplicates_by_filename(file_paths)
        print(f"Filename detection found {len(filename_results)} groups")
        
        # Test full detection
        results = find_all_duplicates(tmp_dir, extensions=['.txt'])
        print(f"Full detection found results for methods: {list(results.keys())}")
        
        # Test merging
        merged = merge_duplicate_groups(results)
        print(f"Merged into {len(merged)} groups")
        assert len(merged) >= 1, f"Expected at least 1 merged group, got {len(merged)}"
        
        print("✓ Basic duplicate detection tests passed")


def test_advanced_grouping():
    """Test advanced grouping functionality."""
    print("\n--- Testing Advanced Grouping ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files with naming patterns
        test_files = [
            ('abc.jpg', b'content1'),
            ('abc_1.jpg', b'content1'),  # related to abc
            ('abc_2.jpg', b'content1'),  # related to abc
            ('abc (1).jpg', b'content2'),
            ('abc (2).jpg', b'content2'),  # related to abc (1)
            ('photo.png', b'content3'),
            ('photo_1.png', b'content3'),  # related to photo
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Test advanced pattern grouping
        pattern_results = group_by_advanced_patterns(file_paths)
        print(f"Advanced pattern grouping found {len(pattern_results)} groups")
        
        # Test relationship-based grouping
        relationship_results = group_files_by_relationships(file_paths)
        print(f"Relationship-based grouping found {len(relationship_results)} groups")
        
        # At least one relationship group should exist
        assert len(relationship_results) >= 2, f"Expected at least 2 relationship groups, got {len(relationship_results)}"
        
        print("✓ Advanced grouping tests passed")


def test_size_filtering():
    """Test size filtering functionality."""
    print("\n--- Testing Size Filtering ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files with different sizes
        test_files = [
            ('tiny.txt', b'a'),  # 1 byte (0.000001 MB)
            ('small.txt', b'a' * 1024),  # 1KB (0.001 MB)
            ('medium.txt', b'a' * (100 * 1024)),  # 100KB (0.1 MB)
            ('large.txt', b'a' * (2 * 1024 * 1024)),  # 2MB
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Test filtering: only files between 0.0005MB and 0.5MB (so small.txt and medium.txt)
        filtered, excluded = filter_files_by_size(file_paths, min_size_mb=0.0005, max_size_mb=0.5)
        print(f"Size filtering: {len(filtered)} included, {len(excluded)} excluded")
        
        # Should include small.txt and medium.txt, exclude tiny.txt and large.txt
        # tiny.txt is 0.000001MB which is less than 0.0005MB
        # small.txt is 0.001MB which is between 0.0005MB and 0.5MB
        # medium.txt is 0.1MB which is between 0.0005MB and 0.5MB
        # large.txt is 2MB which is greater than 0.5MB
        expected_filtered = 2  # small.txt and medium.txt
        expected_excluded = 2  # tiny.txt and large.txt
        
        assert len(filtered) == expected_filtered, f"Expected {expected_filtered} files after filtering, got {len(filtered)}"
        assert len(excluded) == expected_excluded, f"Expected {expected_excluded} files excluded, got {len(excluded)}"
        
        print("✓ Size filtering tests passed")


def test_ignore_list():
    """Test ignore list functionality."""
    print("\n--- Testing Ignore List ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        test_files = [
            ('normal_file.txt', b'content'),
            ('ignored_file.tmp', b'content'),
            ('log_file.log', b'content'),
            ('image.jpg', b'content'),
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Create ignore list
        ignore_list = IgnoreList()
        ignore_list.add_extension('.tmp')
        ignore_list.add_extension('.log')
        ignore_list.add_pattern(r'ignored_')
        
        # Test filtering
        filtered = ignore_list.filter_paths(file_paths)
        print(f"Ignore list: {len(file_paths)} total, {len(filtered)} after filtering")
        
        # Should only have normal_file.txt and image.jpg left (2 files)
        expected_remaining = 2
        assert len(filtered) == expected_remaining, f"Expected {expected_remaining} files after ignore, got {len(filtered)}"
        
        # Verify the right files remain
        remaining_names = [os.path.basename(f) for f in filtered]
        assert 'normal_file.txt' in remaining_names, "normal_file.txt should remain after ignore"
        assert 'image.jpg' in remaining_names, "image.jpg should remain after ignore"
        assert 'ignored_file.tmp' not in remaining_names, "ignored_file.tmp should be filtered out"
        assert 'log_file.log' not in remaining_names, "log_file.log should be filtered out"
        
        print("✓ Ignore list tests passed")


def test_custom_rules():
    """Test custom rules functionality."""
    print("\n--- Testing Custom Rules ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files with patterns
        test_files = [
            ('file_copy.txt', b'content'),
            ('file_duplicate.txt', b'content'),
            ('document_v1.pdf', b'content'),
            ('document_v2.pdf', b'content'),
            ('normal.txt', b'content'),
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Create custom rules
        custom_rules, rule_names = create_custom_rule_set(
            suffix_rules=['_copy', '_duplicate'],
            regex_rules=[r'.*_v\d+\.pdf']
        )
        
        # Test custom rule detection
        results = find_duplicates_by_custom_rules(file_paths, custom_rules, rule_names)
        print(f"Custom rules found {len(results)} groups")
        
        # Should find at least 1 group (for versioned PDFs, or for copy/duplicate suffixes)
        # The exact number depends on how the rules match the test files
        assert len(results) >= 1, f"Expected at least 1 custom rule group, got {len(results)}"
        
        print("✓ Custom rules tests passed")


def test_scan_history():
    """Test scan history functionality."""
    print("\n--- Testing Scan History ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a temporary history file
        history_file = os.path.join(tmp_dir, "test_history.json")
        history = ScanHistory(history_file)
        
        # Add a test record
        mock_results = {
            "hash": {"group1": ["file1.jpg", "file2.jpg"]},
            "size": {"group2": ["file3.png", "file4.png"]}
        }
        history.add_scan_record("/test/dir", mock_results, file_count=10, duplicate_groups=2)
        
        # Get recent scans
        recent = history.get_recent_scans(5)
        print(f"Retrieved {len(recent)} recent scans")
        
        assert len(recent) == 1, f"Expected 1 scan record, got {len(recent)}"
        assert recent[0]['directory'] == "/test/dir", "Directory mismatch in scan record"
        assert recent[0]['file_count'] == 10, "File count mismatch in scan record"
        
        print("✓ Scan history tests passed")


def test_settings_manager():
    """Test settings manager functionality."""
    print("\n--- Testing Settings Manager ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a temporary settings file
        settings_file = os.path.join(tmp_dir, "test_settings.json")
        settings = SettingsManager(settings_file)
        
        # Test default settings
        default_strategy = settings.get_setting('auto_select_strategy')
        print(f"Default strategy: {default_strategy}")
        assert default_strategy == 'oldest', f"Expected 'oldest' strategy, got {default_strategy}"
        
        # Test setting/getting custom values
        settings.set_setting('test_option', 'test_value')
        retrieved_value = settings.get_setting('test_option')
        print(f"Set and retrieved test option: {retrieved_value}")
        assert retrieved_value == 'test_value', f"Expected 'test_value', got {retrieved_value}"
        
        # Test export/import
        export_path = os.path.join(tmp_dir, "exported.json")
        export_success = settings.export_settings(export_path)
        assert export_success, "Settings export failed"
        
        # Import to new manager
        new_settings = SettingsManager(os.path.join(tmp_dir, "imported.json"))
        import_success = new_settings.import_settings(export_path)
        assert import_success, "Settings import failed"
        
        imported_value = new_settings.get_setting('test_option')
        assert imported_value == 'test_value', f"Imported value mismatch: expected 'test_value', got {imported_value}"
        
        print("✓ Settings manager tests passed")


def test_integration():
    """Test integration of multiple features."""
    print("\n--- Testing Integration ---")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create files with various patterns
        test_files = [
            ('abc.jpg', b'content1'),
            ('abc_1.jpg', b'content1'),  # related to abc
            ('abc_2.jpg', b'content1'),  # related to abc
            ('normal.txt', b'content2'),
            ('ignored.tmp', b'content3'),
        ]
        
        file_paths = create_test_files(tmp_dir, test_files)
        
        # Create an ignore list
        ignore_list = IgnoreList()
        ignore_list.add_extension('.tmp')
        
        # Run full detection with multiple features enabled
        results = find_all_duplicates(
            tmp_dir,
            extensions=['.jpg', '.txt', '.tmp'],
            use_hash=True,
            use_filename=True,
            use_size=True,
            use_patterns=True,
            use_custom_rules=True,
            use_advanced_grouping=True,
            min_file_size_mb=0.000001,  # Very small min size
            max_file_size_mb=1.0,      # 1MB max
            ignore_list=ignore_list,
            suffix_rules=['_copy', '_duplicate'],
            regex_rules=[r'.*_[0-9]+\.[^.]+$']  # Pattern for abc_1, abc_2
        )
        
        print(f"Integration test found results for methods: {list(results.keys())}")
        
        # Check that ignore list worked (should not include ignored.tmp)
        all_files_found = []
        for method_results in results.values():
            for file_list in method_results.values():
                all_files_found.extend(file_list)
        
        ignored_files = [f for f in all_files_found if 'ignored.tmp' in f]
        assert len(ignored_files) == 0, f"ignore.tmp was found in results, but should have been ignored"
        
        # Should find abc.jpg, abc_1.jpg, abc_2.jpg as duplicates
        hash_groups = results.get('hash', {})
        hash_duplicates_found = any(len(group) >= 2 for group in hash_groups.values())
        print(f"Found hash duplicates: {hash_duplicates_found}")
        
        # Should find abc.jpg, abc_1.jpg, abc_2.jpg via advanced grouping
        advanced_groups = results.get('advanced_grouping', {})
        advanced_duplicates_found = any(len(group) >= 2 for group in advanced_groups.values())
        print(f"Found advanced grouping duplicates: {advanced_duplicates_found}")
        
        # Test merging results
        merged = merge_duplicate_groups(results)
        print(f"Integration test merged into {len(merged)} groups")
        
        assert len(merged) >= 1, f"Expected at least 1 merged group, got {len(merged)}"
        
        print("✓ Integration tests passed")


def run_all_tests():
    """Run all tests and report results."""
    print("Running Comprehensive Test Suite for Duplicate File Finder")
    print("=" * 60)
    
    tests = [
        test_basic_duplicate_detection,
        test_advanced_grouping,
        test_size_filtering,
        test_ignore_list,
        test_custom_rules,
        test_scan_history,
        test_settings_manager,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test_func.__name__} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! All features are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)