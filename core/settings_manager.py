"""
Settings manager module for duplicate detection app.

PURPOSE:
This module provides functions to export and import application settings,
allowing users to save and restore their configuration preferences. It manages
user preferences such as scan options, file extensions, ignore lists, and
custom rules, making it easy to transfer settings between installations
or share configurations.

RELATIONSHIPS:
- Used by: Main application flow for configuration management
- Uses: json, os, pathlib, typing, logging standard libraries
- Provides: Settings export/import and persistence functionality
- Called when: Loading/saving application configuration

DEPENDENCIES:
- json: For settings serialization/deserialization
- os: For file system operations
- pathlib: For path manipulation
- typing: For type hints (Dict, Any, Optional)
- logging: For logging operations

USAGE:
Use the SettingsManager class to manage application settings:
    from core.settings_manager import SettingsManager
    
    # Initialize settings manager
    settings_manager = SettingsManager(settings_file_path="my_settings.json")
    
    # Get a setting value
    strategy = settings_manager.get_setting("auto_select_strategy", "oldest")
    
    # Set a setting value
    settings_manager.set_setting("image_similarity_threshold", 15)
    
    # Export settings to a file
    success = settings_manager.export_settings("/path/to/export.json")
    
    # Import settings from a file
    success = settings_manager.import_settings("/path/to/import.json")
    
    # Save settings to default location
    settings_manager.save_settings()
    
    # Reset to default settings
    settings_manager.reset_to_defaults()

This module enables persistent configuration management across application sessions.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    A class to manage application settings export/import.
    """
    
    def __init__(self, settings_file_path: str = None):
        """
        Initialize the settings manager.
        
        Args:
            settings_file_path: Path to the settings file. If None, uses default location.
        """
        self.settings_file_path = settings_file_path or os.path.join(
            os.path.expanduser("~"), 
            ".duplicate_file_finder", 
            "app_settings.json"
        )
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        
        # Load existing settings
        self.settings = self.load_settings()
    
    def export_settings(self, export_path: str = None) -> bool:
        """
        Export current settings to a file.
        
        Args:
            export_path: Path to export settings to. If None, uses default path.
            
        Returns:
            True if successful, False otherwise
        """
        path = export_path or self.settings_file_path
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings exported to: {path}")
            return True
        except IOError as e:
            logger.error(f"Error exporting settings to {path}: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """
        Import settings from a file.
        
        Args:
            import_path: Path to import settings from
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(import_path):
            logger.error(f"Settings file does not exist: {import_path}")
            return False
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate that it's a dictionary
            if not isinstance(imported_settings, dict):
                logger.error(f"Invalid settings format in {import_path}")
                return False
            
            self.settings = imported_settings
            logger.info(f"Settings imported from: {import_path}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error importing settings from {import_path}: {e}")
            return False
    
    def save_settings(self):
        """
        Save current settings to the default file.
        """
        try:
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings saved to: {self.settings_file_path}")
        except IOError as e:
            logger.error(f"Error saving settings to {self.settings_file_path}: {e}")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the file.
        
        Returns:
            Dictionary of settings
        """
        if not os.path.exists(self.settings_file_path):
            return self.get_default_settings()
        
        try:
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Merge with defaults to ensure all keys are present
                    defaults = self.get_default_settings()
                    defaults.update(data)
                    return defaults
                else:
                    logger.warning(f"Invalid settings file format, using defaults")
                    return self.get_default_settings()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading settings from {self.settings_file_path}: {e}")
            return self.get_default_settings()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            key: The setting key
            default: Default value if key doesn't exist
            
        Returns:
            The setting value or default
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """
        Set a specific setting value.
        
        Args:
            key: The setting key
            value: The setting value
        """
        self.settings[key] = value
    
    def get_default_settings(self) -> Dict[str, Any]:
        """
        Get the default application settings.
        
        Returns:
            Dictionary of default settings
        """
        return {
            "auto_select_strategy": "oldest",
            "image_similarity_threshold": 10,
            "last_scan_directory": ".",
            "default_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".avi", ".mov"],
            "min_file_size_mb": 0.1,
            "max_file_size_mb": 1000.0,
            "use_custom_rules": False,
            "use_advanced_grouping": False,
            "suffix_rules": ["_copy", "_duplicate"],
            "prefix_rules": [],
            "containing_rules": ["copy", "duplicate"],
            "regex_rules": [r".*_[0-9]+$", r".*\([0-9]+\)$"],
            "keywords": [],
            "ignore_list": {
                "files": [],
                "directories": ["$RECYCLE.BIN", ".git", ".svn", "__pycache__", "node_modules", ".vscode", ".idea"],
                "patterns": [r"\.tmp$", r"\.log$", r"\.cache$"],
                "extensions": [".tmp", ".log", ".cache", ".bak", ".DS_Store"],
                "size_ranges": []  # List of tuples (min_mb, max_mb)
            }
        }
    
    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        """
        self.settings = self.get_default_settings()
        logger.info("Settings reset to defaults")


def get_settings_manager(settings_file_path: str = None) -> SettingsManager:
    """
    Get a settings manager instance.
    
    Args:
        settings_file_path: Path to the settings file
        
    Returns:
        SettingsManager instance
    """
    return SettingsManager(settings_file_path)