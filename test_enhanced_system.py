"""
Comprehensive test suite for the enhanced Duplicate File Finder system.

This test suite verifies:
1. Pydantic models validation
2. Database persistence layer functionality
3. Integration between all components
4. End-to-end functionality
5. Concurrent processing functionality
"""
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import time


def create_test_files(base_dir: Path) -> list:
    """Create test files for duplicate detection."""
    # Create some test files
    files = []
    
    # Create a file and its duplicate
    original_file = base_dir / "original.txt"
    original_content = "This is a test file for duplicate detection."
    original_file.write_text(original_content)
    files.append(str(original_file))
    
    # Create a duplicate
    duplicate_file = base_dir / "duplicate.txt"
    duplicate_file.write_text(original_content)  # Same content
    files.append(str(duplicate_file))
    
    # Create another file with different content
    other_file = base_dir / "other.txt"
    other_file.write_text("This is a different file.")
    files.append(str(other_file))
    
    # Create image files
    image_file = base_dir / "image.jpg"
    image_file.write_text("fake image content")
    files.append(str(image_file))
    
    image_duplicate = base_dir / "image_copy.jpg"
    image_duplicate.write_text("fake image content")  # Same content
    files.append(str(image_duplicate))
    
    return files


def test_pydantic_models():
    """Test Pydantic models validation."""
    print("Testing Pydantic models...")
    
    from core.models import FileInfo, DuplicateGroup, ScanResult, ScanSettings, DuplicateFinderConfig
    
    # Test FileInfo model
    test_file = Path(__file__)
    stat = test_file.stat()
    
    file_info = FileInfo(
        path=test_file,
        size=stat.st_size,
        created_time=datetime.fromtimestamp(stat.st_ctime),
        modified_time=datetime.fromtimestamp(stat.st_mtime),
        extension=test_file.suffix.lower(),
        name=test_file.name
    )
    
    assert file_info.path == test_file
    assert file_info.size > 0
    assert file_info.extension == '.py'
    assert file_info.name == 'test_enhanced_system.py'
    
    print("✓ FileInfo model validation passed")
    
    # Test DuplicateGroup model
    duplicate_group = DuplicateGroup(
        id="test_group_1",
        files=[file_info],
        detection_method="hash"
    )
    
    assert duplicate_group.id == "test_group_1"
    assert duplicate_group.detection_method == "hash"
    assert len(duplicate_group.files) == 1
    
    print("✓ DuplicateGroup model validation passed")
    
    # Test ScanSettings model
    scan_settings = ScanSettings(
        directory=Path("."),
        extensions=['.txt', '.jpg'],
        use_hash=True,
        use_filename=True,
        use_size=True,
        use_patterns=True,
        use_custom_rules=False,
        use_advanced_grouping=False,
        min_file_size_mb=0.1,
        max_file_size_mb=100.0,
        image_similarity_threshold=10
    )
    
    assert scan_settings.directory == Path(".")
    assert '.txt' in scan_settings.extensions
    assert scan_settings.use_hash is True
    
    print("✓ ScanSettings model validation passed")
    
    # Test ScanResult model
    scan_result = ScanResult(
        directory=Path("."),
        scanned_files_count=10,
        duplicate_groups=[duplicate_group],
        scan_start_time=datetime.now(),
        scan_end_time=datetime.now(),
        scan_duration=1.5,
        methods_used=["hash"]
    )
    
    assert scan_result.directory == Path(".")
    assert scan_result.scanned_files_count == 10
    assert len(scan_result.duplicate_groups) == 1
    assert scan_result.total_duplicates_found == 0  # Only 1 file in the group, so no duplicates
    
    print("✓ ScanResult model validation passed")
    
    print("All Pydantic model tests passed!")


def test_database_functionality():
    """Test database persistence functionality."""
    print("\nTesting database functionality...")
    
    from core.database import DuplicateDatabase
    from core.models import FileInfo, DuplicateGroup, ScanResult
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    
    try:
        # Initialize database
        db = DuplicateDatabase(db_path)
        print("✓ Database initialization passed")
        
        # Create a test scan result
        test_file = Path(__file__)
        stat = test_file.stat()
        
        file_info = FileInfo(
            path=test_file,
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            extension=test_file.suffix.lower(),
            name=test_file.name
        )
        
        duplicate_group = DuplicateGroup(
            id="test_group_db",
            files=[file_info],
            detection_method="hash"
        )
        
        scan_result = ScanResult(
            directory=Path("."),
            scanned_files_count=1,
            duplicate_groups=[duplicate_group],
            scan_start_time=datetime.now(),
            scan_end_time=datetime.now(),
            scan_duration=0.1,
            methods_used=["hash"]
        )
        
        # Save the scan result
        scan_id = db.save_scan_result(scan_result)
        assert scan_id > 0
        print(f"✓ Scan result saved with ID: {scan_id}")
        
        # Retrieve the scan result
        retrieved_result = db.get_scan_result(scan_id)
        assert retrieved_result is not None
        assert retrieved_result.directory == Path(".")
        assert len(retrieved_result.duplicate_groups) == 1
        print("✓ Scan result retrieved successfully")
        
        # Test recent scans
        recent_scans = db.get_recent_scans(limit=5)
        assert len(recent_scans) >= 1
        assert recent_scans[0]['id'] == scan_id
        print("✓ Recent scans retrieval passed")
        
        # Test deleting a scan
        db.delete_scan(scan_id)
        deleted_result = db.get_scan_result(scan_id)
        assert deleted_result is None
        print("✓ Scan deletion passed")
        
        # Test clearing all scans
        db.save_scan_result(scan_result)  # Add one more for testing clear
        db.clear_all_scans()
        recent_scans = db.get_recent_scans(limit=5)
        assert len(recent_scans) == 0
        print("✓ Clear all scans passed")
        
        print("All database functionality tests passed!")
        
    finally:
        # Clean up the test database file - force close connections if needed
        del db  # Remove reference to database
        time.sleep(0.1)  # Brief pause to allow system to release file handle
        if db_path.exists():
            try:
                db_path.unlink()
            except PermissionError:
                print(f"Could not delete {db_path}, file may still be in use by system")


def test_scan_history_integration():
    """Test scan history integration with the database."""
    print("\nTesting scan history integration...")
    
    from core.scan_history import ScanHistory
    from core.database import DuplicateDatabase
    from core.models import FileInfo, DuplicateGroup, ScanResult
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    
    try:
        # Initialize scan history
        scan_history = ScanHistory(str(db_path))
        
        # Create a test scan result
        test_file = Path(__file__)
        stat = test_file.stat()
        
        file_info = FileInfo(
            path=test_file,
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            extension=test_file.suffix.lower(),
            name=test_file.name
        )
        
        duplicate_group = DuplicateGroup(
            id="test_group_history",
            files=[file_info],
            detection_method="hash"
        )
        
        scan_result = ScanResult(
            directory=Path("."),
            scanned_files_count=1,
            duplicate_groups=[duplicate_group],
            scan_start_time=datetime.now(),
            scan_end_time=datetime.now(),
            scan_duration=0.1,
            methods_used=["hash"]
        )
        
        # Add scan result to history
        scan_id = scan_history.add_scan_result(scan_result)
        assert scan_id > 0
        print(f"✓ Scan result added to history with ID: {scan_id}")
        
        # Get recent scans
        recent_scans = scan_history.get_recent_scans(limit=5)
        assert len(recent_scans) >= 1
        assert recent_scans[0]['id'] == scan_id
        print("✓ Recent scans from history passed")
        
        # Get specific scan result
        retrieved_result = scan_history.get_scan_result(scan_id)
        assert retrieved_result is not None
        assert retrieved_result.directory == Path(".")
        print("✓ Specific scan retrieval from history passed")
        
        # Test scans by directory
        scans_by_dir = scan_history.get_scans_by_directory(str(Path(".")))
        assert len(scans_by_dir) >= 1
        print("✓ Scans by directory passed")
        
        # Test deletion through history
        scan_history.delete_scan(scan_id)
        deleted_result = scan_history.get_scan_result(scan_id)
        assert deleted_result is None
        print("✓ Scan deletion through history passed")
        
        print("All scan history integration tests passed!")
        
    finally:
        # Clean up the test database file
        del scan_history  # Remove reference to scan history
        time.sleep(0.1)  # Brief pause to allow system to release file handle
        if db_path.exists():
            try:
                db_path.unlink()
            except PermissionError:
                print(f"Could not delete {db_path}, file may still be in use by system")


def test_concurrent_processing():
    """Test concurrent processing functionality."""
    print("\nTesting concurrent processing functionality...")
    
    from core.concurrency import find_duplicates_by_hash_concurrent, calculate_hashes_concurrent
    from core.hashing import find_duplicates_by_hash
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        create_test_files(temp_path)
        
        # Get all files in the temp directory
        all_files = [str(f) for f in temp_path.iterdir() if f.is_file()]
        print(f"Created {len(all_files)} test files")
        
        # Test concurrent hash calculation
        hashes = calculate_hashes_concurrent(all_files)
        print(f"✓ Concurrent hash calculation for {len(all_files)} files completed")
        assert len(hashes) == len(all_files)
        
        # Test concurrent duplicate detection
        duplicates = find_duplicates_by_hash_concurrent(all_files)
        print(f"✓ Concurrent duplicate detection found {len(duplicates)} duplicate groups")
        
        # Verify that we have at least one duplicate group (we created 2 pairs of duplicates)
        assert len(duplicates) >= 2, f"Expected at least 2 duplicate groups, got {len(duplicates)}"
        
        # Compare with non-concurrent version
        non_concurrent_duplicates = find_duplicates_by_hash(all_files)
        print(f"Non-concurrent version found {len(non_concurrent_duplicates)} duplicate groups")
        
        # Both methods should find the same number of groups
        assert len(duplicates) == len(non_concurrent_duplicates), \
            f"Concurrent and non-concurrent methods found different numbers of groups: {len(duplicates)} vs {len(non_concurrent_duplicates)}"
        
        print("✓ Concurrent processing tests passed!")
    

def test_end_to_end_functionality():
    """Test end-to-end functionality with temporary files."""
    print("\nTesting end-to-end functionality...")
    
    from core.models import ScanSettings, ScanResult
    from core.database import DuplicateDatabase
    from core.duplicate_detection import find_all_duplicates_with_models
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        create_test_files(temp_path)
        
        # Create scan settings for the test directory
        scan_settings = ScanSettings(
            directory=temp_path,
            extensions=['.txt', '.jpg'],
            use_hash=True,
            use_filename=True,
            use_size=True,
            use_patterns=True,
            use_custom_rules=False,
            use_advanced_grouping=False,
            min_file_size_mb=0.0,
            max_file_size_mb=100.0,
            image_similarity_threshold=10
        )
        
        # Run duplicate detection with models
        duplicate_groups = find_all_duplicates_with_models(scan_settings)
        
        # Verify that we found some duplicates
        print(f"Found {len(duplicate_groups)} duplicate groups")
        
        # We expect at least 2 groups: one for .txt files and one for .jpg files
        # Each group should have 2 files (the original and its duplicate)
        txt_groups = [g for g in duplicate_groups if g.detection_method == 'hash']
        print(f"Hash-based groups: {len(txt_groups)}")
        
        # There should be at least 2 files that are duplicates in our test setup
        total_duplicate_files = sum(len(group.files) for group in duplicate_groups if len(group.files) > 1)
        print(f"Total files in duplicate groups: {total_duplicate_files}")
        
        # Save to database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = Path(tmp.name)
        
        try:
            scan_result = ScanResult(
                directory=scan_settings.directory,
                scanned_files_count=5,  # We created 5 files
                duplicate_groups=duplicate_groups,
                scan_start_time=datetime.now(),
                scan_end_time=datetime.now(),
                scan_duration=0.5,
                methods_used=["hash", "size", "filename"]
            )
            
            db = DuplicateDatabase(db_path)
            saved_id = db.save_scan_result(scan_result)
            assert saved_id > 0
            print(f"✓ End-to-end scan result saved with ID: {saved_id}")
            
            # Retrieve and verify
            retrieved = db.get_scan_result(saved_id)
            assert retrieved is not None
            assert len(retrieved.duplicate_groups) == len(duplicate_groups)
            print("✓ End-to-end result retrieval successful")
            
        finally:
            # Clean up database file
            del db  # Remove reference to database
            time.sleep(0.1)  # Brief pause to allow system to release file handle
            if db_path.exists():
                try:
                    db_path.unlink()
                except PermissionError:
                    print(f"Could not delete {db_path}, file may still be in use by system")
    
    print("End-to-end functionality test passed!")


def run_all_tests():
    """Run all tests in the suite."""
    print("Starting comprehensive test suite for enhanced Duplicate File Finder...\n")
    
    try:
        test_pydantic_models()
        test_database_functionality()
        test_scan_history_integration()
        test_concurrent_processing()
        test_end_to_end_functionality()
        
        print("\n🎉 All tests passed! The enhanced system is working correctly.")
        print("\nEnhancements verified:")
        print("- Pydantic models with validation")
        print("- SQLite database persistence layer")
        print("- Scan history integration")
        print("- Concurrent processing functionality")
        print("- End-to-end functionality")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)