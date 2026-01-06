"""
Configuration module for the duplicate finder application.

PURPOSE:
This module handles application settings and configuration. It provides a centralized
way to manage application preferences, defaults, and user settings that persist
between application runs. The configuration is stored in a JSON file and validated
using Pydantic models.

RELATIONSHIPS:
- Uses: core.models.DuplicateFinderConfig for validation
- Provides: Application configuration management to main application
- Called by: Main application to get/set configuration values
- Depends on: json, os, pathlib, typing

DEPENDENCIES:
- json: For config serialization/deserialization
- os: For file system operations
- pathlib: For path manipulation
- typing: For type hints (Dict, Any, Optional)
- core.models: For DuplicateFinderConfig model

USAGE:
Use the Config class to manage application configuration:
    from utils.config import Config
    
    # Initialize config
    config = Config()
    
    # Get a configuration value
    value = config.get('setting_name', 'default_value')
    
    # Set a configuration value
    config.set('setting_name', 'new_value')
    
    # Update multiple configuration values
    config.update({'setting1': 'value1', 'setting2': 'value2'})
    
    # Save configuration to file
    config.save_config()

This module ensures application settings are persisted and validated across sessions.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from core.models import DuplicateFinderConfig

# Define the config file path
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


class Config:
    """Configuration class to manage application settings."""
    
    def __init__(self):
        """Initialize the configuration with default values."""
        self.config_file = CONFIG_FILE
        self._config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        # Use the Pydantic model for default config
        default_config = DuplicateFinderConfig()
        return default_config.model_dump()
    
    def save_config(self):
        """Save the current configuration to file."""
        try:
            # Validate the config before saving
            config_model = DuplicateFinderConfig(**self._config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        # Validate the value against the model if it's a known key
        try:
            current_config = self._config.copy()
            current_config[key] = value
            
            # Validate the updated config
            validated_config = DuplicateFinderConfig(**current_config)
            self._config = validated_config.model_dump()
        except Exception as e:
            print(f"Invalid value for {key}: {e}. Keeping original value.")
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values at once."""
        try:
            # Create a new config with the updates
            new_config = self._config.copy()
            new_config.update(updates)
            
            # Validate the new config
            validated_config = DuplicateFinderConfig(**new_config)
            self._config = validated_config.model_dump()
        except Exception as e:
            print(f"Error updating config: {e}. Changes not applied.")