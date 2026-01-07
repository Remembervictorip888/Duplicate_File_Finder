# Debugging Guide for Duplicate File Finder

## Overview

This document outlines common issues encountered with the Duplicate File Finder application and how to troubleshoot them effectively.

## Common Issues and Solutions

### Issue 1: No Duplicates Detected

#### Symptom
The application reports "Found 0 groups of duplicate files" even when identical files are present in the target directory.

#### Root Cause
There are several potential causes:
1. **File Extensions**: The application by default scans only media files (.jpg, .png, .gif, .mp4, etc.) and ignores other file types.
2. **Size Filtering**: The default minimum file size is 0.1 MB, which excludes smaller files.
3. **Configuration Settings**: Various filters may be preventing detection.

#### Solution
1. Specify the correct file extensions using `--extensions`:
   ```bash
   python main.py /path/to/directory --method all --extensions .txt .doc .pdf
   ```
2. Adjust size filtering if needed:
   ```bash
   python main.py /path/to/directory --method all --min-size 0
   ```
3. Use both options together for small text files:
   ```bash
   python main.py /path/to/directory --method all --extensions .txt --min-size 0
   ```

### Issue 2: Insufficient Debugging Information

#### Symptom
The application completes without providing enough information to understand what happened during the scan.

#### Root Cause
Default logging level was set to INFO, which didn't provide detailed information about the scanning process and results.

#### Solution
Enhanced logging was added to provide more visibility into:
- Scan parameters and settings used
- Number of potential duplicate groups found
- Details about each group including detection method
- Information about files processed
- Content hashes for debugging

## Using Enhanced Logging

The application now logs detailed information at the DEBUG level, which helps identify issues like:

- What file extensions are being scanned
- What size filters are applied
- How many files were processed
- Content hashes for verification
- Which detection methods found duplicates

Example of detailed logging output:
```
2026-01-07 09:28:05 - duplicate_finder - DEBUG - Scan settings: directory=WindowsPath('test_scan_dir') extensions=['.txt'] use_hash=True use_filename=True use_size=True use_patterns=True use_custom_rules=False use_advanced_grouping=False min_file_size_mb=0.0 max_file_size_mb=1000.0
2026-01-07 09:28:05 - duplicate_finder - DEBUG - Found 2 potential duplicate groups
2026-01-07 09:28:05 - duplicate_finder - DEBUG - Group 1: 3 files detected by hash
```

## Verification Steps

To verify the application is working correctly:

1. Create test files with known duplicates:
   ```bash
   mkdir test_dir
   echo "test content" > test_dir/file1.txt
   echo "test content" > test_dir/file2.txt  # duplicate of file1
   echo "different content" > test_dir/file3.txt
   ```

2. Run the application with appropriate settings:
   ```bash
   python main.py test_dir --method all --extensions .txt --min-size 0
   ```

3. Check the logs in the `logs/` directory for detailed information about the scan.

## Key Takeaways

- Always specify the correct file extensions when scanning
- Be aware of default size filters (0.1 MB minimum by default)
- Use enhanced logging to troubleshoot detection issues
- The application works correctly when properly configured for the target file types