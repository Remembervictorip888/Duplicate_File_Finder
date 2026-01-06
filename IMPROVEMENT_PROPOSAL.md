# Improving the Duplicate File Finder Architecture

This document outlines how to enhance the current Duplicate File Finder application to better align with modern Python application architecture principles.

## Current State Analysis

The current application is well-structured in many ways:
- ✅ Good separation of concerns in the Python backend
- ✅ Proper use of xxhash for performance
- ✅ Good error handling and logging
- ✅ Type hints throughout
- ✅ Safe deletion using send2trash

## Areas for Improvement

### 1. Add Pydantic Models for Data Validation

Create a data layer using Pydantic models to validate data:

```python
# core/models.py
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class FileInfo(BaseModel):
    path: Path
    size: int = Field(ge=0)
    hash_value: Optional[str] = None
    created_time: datetime
    modified_time: datetime
    extension: str

class DuplicateGroup(BaseModel):
    id: str
    files: List[FileInfo]
    primary_file: Optional[FileInfo] = None
```

### 2. Implement Data Persistence Layer

Create a data persistence layer using SQLite:

```python
# core/data/database.py
import sqlite3
from pathlib import Path
from typing import List, Optional
from core.models import DuplicateGroup

class DuplicateDatabase:
    def __init__(self, db_path: Path = Path("duplicates.db")):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        # Create tables for storing scan results
        pass
    
    def save_scan_results(self, groups: List[DuplicateGroup]):
        # Save scan results to database
        pass
    
    def get_previous_scan_results(self) -> List[DuplicateGroup]:
        # Retrieve previous scan results
        pass
```

### 3. Implement Concurrency

Update the scanning module to use concurrent processing:

```python
# core/scanner.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool
import xxhash

class ConcurrentScanner:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def scan_files_concurrent(self, file_paths: List[str]) -> List[FileInfo]:
        # Use ThreadPoolExecutor for I/O bound operations
        pass
    
    def hash_files_concurrent(self, file_paths: List[str]) -> Dict[str, List[str]]:
        # Use multiprocessing for CPU-bound hashing
        pass
```

### 4. Enhance Error Handling

Implement more robust error handling with retry mechanisms:

```python
# utils/error_handler.py
from typing import Callable, Any
import time
import logging

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (PermissionError, OSError) as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            
            logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
            raise last_exception
        return wrapper
    return decorator
```

### 5. Add Progress Tracking and Cancellation

Implement progress tracking and cancellation support:

```python
# core/progress_tracker.py
from typing import Protocol
from dataclasses import dataclass
import threading

@dataclass
class ProgressUpdate:
    current: int
    total: int
    message: str
    cancelled: bool = False

class ProgressCallback(Protocol):
    def update(self, progress: ProgressUpdate) -> None: ...

class CancellableScanner:
    def __init__(self):
        self.cancel_event = threading.Event()
    
    def cancel(self):
        self.cancel_event.set()
    
    def scan_with_progress(self, directory: str, callback: ProgressCallback):
        # Implementation with progress updates and cancellation support
        pass
```

### 6. Improved Project Structure

The project should be restructured to better match the recommended structure:

```
/duplicate-file-finder
├── /app
│   ├── /core           # Business Logic
│   │   ├── /models     # Pydantic models
│   │   ├── /services   # Core logic (scanner, hasher, etc.)
│   │   └── /dtos       # Data transfer objects
│   ├── /data           # Data Layer
│   │   ├── /database   # Database operations
│   │   └── /schemas    # Database schemas
│   ├── /ui             # UI Layer (Electron/React)
│   │   ├── /assets     # Icons, themes, images
│   │   ├── main_window.py  # If using Python UI framework
│   │   └── widgets.py
│   └── /utils          # Shared utilities
│       ├── logger.py
│       └── helpers.py
├── /tests
├── main.py             # Entry point
├── requirements.txt
├── README.md
└── .cursorrules        # AI coding standards
```

### 7. Add Configuration Management

Enhance the configuration system:

```python
# app/core/config.py
from pydantic import BaseSettings
from typing import List

class AppSettings(BaseSettings):
    # Performance settings
    max_workers: int = 4
    chunk_size: int = 131072  # 128KB
    max_file_size: int = 104857600  # 100MB
    
    # File settings
    default_extensions: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
        ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".txt", ".pdf",
        ".doc", ".docx", ".xls", ".xlsx"
    ]
    
    # UI settings
    preview_thumbnail_size: int = 200
    
    class Config:
        env_file = ".env"
```

## Implementation Priority

1. **High Priority**: Add Pydantic models and data persistence
2. **Medium Priority**: Implement concurrency and progress tracking
3. **Low Priority**: Restructure project directories (refactoring)

## Benefits of These Improvements

1. **Better Type Safety**: Pydantic models provide runtime validation
2. **Improved Performance**: Concurrency will speed up processing
3. **Better UX**: Progress tracking and cancellation improve user experience
4. **Maintainability**: Clearer separation of concerns
5. **Reliability**: Better error handling and recovery mechanisms