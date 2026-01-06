"""
Configuration module for the duplicate finder application.

This module handles application configuration and settings.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration class to manage application settings.
    """
    
    def __init__(self, config_path: str = "app_config.json"):
        self.config_path = Path(config_path)
        self.default_config = {
            "last_scan_directory": "",
            "image_similarity_threshold": 5,
            "hash_chunk_size": 131072,  # 128KB
            "max_file_size_for_hashing": 104857600,  # 100MB
            "file_extensions": [
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
                ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".txt", ".pdf",
                ".doc", ".docx", ".xls", ".xlsx"
            ],
            "auto_select_strategy": "oldest"  # oldest, newest, lowest_res
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, or create default if file doesn't exist.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
        
        # Return default config if file doesn't exist or loading failed
        logger.info("Using default configuration")
        return self.default_config.copy()
    
    def save_config(self):
        """
        Save current configuration to file.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config to {self.config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value