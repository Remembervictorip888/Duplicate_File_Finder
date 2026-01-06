# Duplicate File Finder

A high-performance local file processing application that finds duplicate files and images with visual similarity, with safe deletion to the Windows Recycle Bin.

## Features

- **Fast duplicate detection**: Uses xxhash for ultra-fast content-based file comparison
- **Visual similarity**: Finds similar images using perceptual hashing
- **Safe deletion**: Moves files to Recycle Bin (supports undo)
- **High performance**: Optimized to scan 100k+ files without UI freezing
- **Auto-selection**: Automatically selects duplicates based on rules (Oldest, Newest, Low Res)
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

1. Make sure you have Python 3.12+ installed

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Scan a directory for duplicates
python main.py /path/to/directory

# Scan with a specific strategy for auto-selecting duplicates
python main.py /path/to/directory --strategy oldest

# Actually delete the auto-selected duplicates (moves to Recycle Bin)
python main.py /path/to/directory --strategy oldest --delete

# Adjust the similarity threshold for images (0-20, lower = more similar)
python main.py /path/to/directory --similarity 3
```

### Available Strategies

- `oldest`: Selects the oldest file in each duplicate group for deletion
- `newest`: Selects the newest file in each duplicate group for deletion
- `lowest_res`: Selects the lowest resolution image in each duplicate group for deletion

## Building a Windows Executable

To create a standalone Windows .exe file:

1. Install PyInstaller:

```bash
pip install pyinstaller
```

1. Build the executable:

```bash
pyinstaller --onefile --windowed main.py
```

The executable will be created in the `dist/` folder.

## Enhanced User Requirements

### 1. Folder Selection
- Allow users to select a folder to search for duplicate files
- Support searching within subfolders (recursive scanning)
- Provide visual feedback during the scanning process

### 2. File Type Filtering
- Focus on searching for duplicate images and videos
- Support common image formats: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP, etc.
- Support common video formats: MP4, AVI, MOV, WMV, MKV, FLV, WEBM, etc.
- Allow users to select specific file types to include in the scan

### 3. Duplicate Detection Methods
Implement the following methods to detect duplicate files:

#### 3.1 File Name Comparison
- Compare file names (ignore case and file extension)
- Handle common naming patterns that indicate duplicates

#### 3.2 File Size Comparison
- Compare file sizes to identify potential duplicates
- Group files with identical sizes

#### 3.3 File Content (MD5 HASH)
- Compare file content using MD5 hash to identify exact duplicates
- Use efficient hashing algorithms for fast processing

#### 3.4 Manual Rules (Custom Patterns)
Allow users to set up custom rules to detect duplicates based on file name patterns:
- File names ending with "_1", "_2", "_copy", etc.
- File names containing "(1)", "(2)", "(Copy)", etc.
- Custom regular expressions for advanced pattern matching
- File names containing specific keywords or phrases
- Case-insensitive matching options

### 4. Duplicate File Grouping
- Group potential duplicate files together based on the selected method(s)
- Example groupings:
  - `abc.jpg` and `abc_1.jpg` should be grouped as potential duplicates
  - `abc (1).jpg`, `abc (2).jpg`, and `abc.jpg` should be grouped as potential duplicates
- Allow users to select which files in each group to keep or delete

### 5. Result Display
- Display the grouped duplicate files in a clear and easy-to-read format
- Show file name and path, file size, file type
- Provide preview thumbnails for images and videos (optional, user toggleable)
- Allow users to sort and filter results
- Enable quick selection of files to keep or delete

### 6. Performance Requirements
#### 6.1 Fast Scanning
- Optimize the scanning process to be fast and efficient, even for large folders with many files
- Implement multi-threading or parallel processing for faster scanning
- Provide progress indicators during scanning

#### 6.2 Size Filtering
- Allow users to exclude files from the scan based on size:
  - Files smaller than X MB
  - Files larger than X MB
- This helps in more effective scanning by focusing on relevant files

### 7. Clear Instructions
- Provide clear instructions and tooltips to help users understand the app features and options
- Include contextual help for each feature
- Offer a quick start guide for new users

### 8. Customizable Settings
Allow users to customize the app settings:
- Folder selection preferences
- File type filtering options
- File size filtering options
- Duplicate detection methods selection
- Interface language and theme preferences

### 9. Additional Features

#### 9.1 Ignore List
- Allow users to add files, folders, file names, or file sizes to an ignore list
- Exclude items on the ignore list from the scanning process
- Support both exact matches and pattern-based ignores

#### 9.2 Scan History
- Keep a record of previous scans, including:
  - Folder that was scanned
  - Date and time of the scan
  - Number of duplicate files found
  - Actions taken (files deleted, kept, etc.)
- Allow users to view and restore previous scan results

#### 9.3 Settings Export and Import
- Allow users to export and import the app settings
- Enable backup and transfer of preferences between installations
- Support sharing of common configurations

#### 9.4 Advanced Features
- Batch operations for managing multiple duplicate groups at once
- Preview before deletion to prevent accidental file removal
- Integration with cloud storage for scanning synced files
- Scheduled scanning for regular cleanup

## Architecture

The application follows the Model-View-Controller (MVC) pattern with clear separation of concerns:

- `/core`: Core functionality modules
  - `hashing.py`: File hashing using xxhash for fast duplicate detection
  - `scanning.py`: Directory scanning using os.scandir for fast iteration
  - `image_similarity.py`: Visual similarity detection using perceptual hashing
  - `file_operations.py`: Safe file operations using send2trash

- `/utils`: Utility modules
  - `logger.py`: Logging configuration
  - `path_helper.py`: Path manipulation utilities
  - `config.py`: Application configuration management

- `main.py`: Application entry point

## Performance Optimizations

- Uses 128KB chunks for memory-efficient file reading
- Implements generator-based directory scanning to handle large numbers of files
- Uses xxhash which is 10x faster than hashlib for content comparison
- Implements background processing to prevent UI freezing

## Safety Features

- All file deletions use `send2trash` to move files to Recycle Bin (supports undo)
- All file operations are wrapped in try/catch blocks
- Permission errors are handled gracefully
- Configurable maximum file size to prevent processing extremely large files

## Logging

The application logs to both console and `app.log` file with detailed information about the scanning and processing operations.

## License

This project is available as open source under the terms of the MIT License.
