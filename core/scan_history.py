"""
Scan history module for duplicate detection.

This module provides functions to record and manage previous scan sessions,
including metadata about each scan and its results.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ScanHistory:
    """
    A class to manage scan history records.
    """
    
    def __init__(self, history_file_path: str = None):
        """
        Initialize the scan history manager.
        
        Args:
            history_file_path: Path to the history file. If None, uses default location.
        """
        self.history_file_path = history_file_path or os.path.join(
            os.path.expanduser("~"), 
            ".duplicate_file_finder", 
            "scan_history.json"
        )
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.history_file_path), exist_ok=True)
        
        # Load existing history
        self.history = self.load_history()
    
    def add_scan_record(self, directory: str, results: Dict, 
                       file_count: int = 0, duplicate_groups: int = 0) -> str:
        """
        Add a new scan record to the history.
        
        Args:
            directory: The directory that was scanned
            results: The results of the scan
            file_count: Number of files scanned
            duplicate_groups: Number of duplicate groups found
            
        Returns:
            The ID of the newly created record
        """
        record_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        record = {
            'id': record_id,
            'timestamp': datetime.now().isoformat(),
            'directory': directory,
            'file_count': file_count,
            'duplicate_groups': duplicate_groups,
            'results_summary': self._summarize_results(results)
        }
        
        self.history.append(record)
        self.save_history()
        
        logger.info(f"Added scan record: {record_id} for directory {directory}")
        return record_id
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent scan records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent scan records
        """
        return sorted(self.history, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_scan_by_id(self, scan_id: str) -> Optional[Dict]:
        """
        Get a specific scan record by its ID.
        
        Args:
            scan_id: The ID of the scan record
            
        Returns:
            The scan record or None if not found
        """
        for record in self.history:
            if record['id'] == scan_id:
                return record
        return None
    
    def get_scans_by_directory(self, directory: str) -> List[Dict]:
        """
        Get all scan records for a specific directory.
        
        Args:
            directory: The directory to search for
            
        Returns:
            List of scan records for the directory
        """
        return [record for record in self.history if record['directory'] == directory]
    
    def clear_history(self):
        """
        Clear all scan history records.
        """
        self.history = []
        self.save_history()
        logger.info("Cleared scan history")
    
    def load_history(self) -> List[Dict]:
        """
        Load scan history from the file.
        
        Returns:
            List of scan records
        """
        if not os.path.exists(self.history_file_path):
            return []
        
        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    logger.warning(f"Invalid history file format, returning empty list")
                    return []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading scan history from {self.history_file_path}: {e}")
            return []
    
    def save_history(self):
        """
        Save scan history to the file.
        """
        try:
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving scan history to {self.history_file_path}: {e}")
    
    def _summarize_results(self, results: Dict) -> Dict:
        """
        Create a summary of scan results.
        
        Args:
            results: Full scan results
            
        Returns:
            Summary of the results
        """
        summary = {}
        for method, groups in results.items():
            summary[method] = len(groups)
        return summary


def get_scan_history(history_file_path: str = None) -> ScanHistory:
    """
    Get a scan history instance.
    
    Args:
        history_file_path: Path to the history file
        
    Returns:
        ScanHistory instance
    """
    return ScanHistory(history_file_path)