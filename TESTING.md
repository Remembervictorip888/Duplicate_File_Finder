# Testing Framework for Duplicate File Finder

This project includes an automated testing framework that allows you to verify all core functions work correctly without needing to use the UI.

## Test Components

### 1. Self-Test Engine (`test_engine.py`)

- Basic functionality tests for core modules
- Tests scanning, hashing, image similarity, and file operations
- Creates temporary test files to validate functionality
- Runs quickly to verify basic operations

### 2. Comprehensive Test Suite (`test_suite.py`)

- Advanced testing with multiple scenarios
- Edge case testing (empty directories, non-existent paths, etc.)
- Various file type and directory structure tests
- Nested directory scanning tests

### 3. Test Runner (`test_runner.py`)

- Orchestrates running of tests
- Provides configuration options
- Generates detailed logs
- Reports test results

## How to Run Tests

### Run all tests:

```bash
python test_runner.py --all
```

### Run only basic tests:

```bash
python test_runner.py --basic
```

### Run only comprehensive tests:

```bash
python test_runner.py --comprehensive
```

## Test Results and Logs

All test results are logged in the `logs/` directory with timestamped files:

- `test_run_YYYYMMDD_HHMMSS.log` - Basic test results
- `comprehensive_test_YYYYMMDD_HHMMSS.log` - Comprehensive test results
- `test_runner_YYYYMMDD_HHMMSS.log` - Overall test runner logs

## Test Coverage

The testing framework covers:

- **Scanning Module**: Directory traversal and file discovery
- **Hashing Module**: Duplicate detection using hash algorithms
- **Image Similarity**: Exact and approximate duplicate detection
- **File Operations**: Safe deletion and auto-selection strategies

## Auto-Testing Capability

The framework runs without UI interaction, making it suitable for:

- Continuous Integration (CI) pipelines
- Regression testing
- Pre-deployment validation
- Function verification without UI dependencies

## Test Scenarios

The comprehensive suite includes tests for:

- Multiple sets of duplicate files
- Different file types (images, text files)
- Nested directory structures
- Edge cases (empty directories, non-existent paths)
- Auto-selection strategies (oldest, newest, lowest resolution)
