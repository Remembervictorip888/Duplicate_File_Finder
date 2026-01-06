"""
Logging module for the duplicate finder application.

PURPOSE:
This module configures logging to both console and file, providing a centralized
logging mechanism for the application. It ensures all components of the application
can log messages consistently to both console output and persistent log files,
which is essential for debugging and monitoring application behavior.

RELATIONSHIPS:
- Used by: All core modules and main application for logging
- Uses: logging, os, pathlib standard libraries
- Provides: Standardized logging setup across the application
- Called when: Logging is needed in any module

DEPENDENCIES:
- logging: For logging functionality
- os: For file system operations
- pathlib: For path manipulation
- Creates log files in the 'logs' directory as per project specification

USAGE:
Use the setup_logger function to create loggers throughout the application:
    from utils.logger import setup_logger
    import logging
    
    # Create a logger for a module
    logger = setup_logger('my_module', 'my_module.log', logging.INFO)
    
    # Use the logger
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")

This module implements the application-wide logging standard as specified in the project requirements.
"""
import logging
import os
from pathlib import Path


def setup_logger(name: str = __name__, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to the log file (if None, uses default location in logs folder)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Create logs directory in the app root if not exists
    app_root = Path(__file__).parent.parent  # Go up one level from utils to app root
    logs_dir = app_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Use default log file name if not provided
    if log_file is None:
        log_file = logs_dir / "app.log"
    else:
        # If a specific log file is provided, ensure it's in the logs directory
        if not Path(log_file).is_absolute():
            log_file = logs_dir / log_file
        else:
            # If absolute path is provided, use it as is
            log_file = Path(log_file)
            # Create parent directories if they don't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger