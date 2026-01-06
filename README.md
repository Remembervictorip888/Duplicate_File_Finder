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

2. Build the executable:
```bash
pyinstaller --onefile --windowed main.py
```

The executable will be created in the `dist/` folder.

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
