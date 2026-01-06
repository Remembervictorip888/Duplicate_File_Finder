"""
Scan history module for duplicate detection.

This module provides functions to record and manage previous scan sessions,
including metadata about each scan and its results using SQLite database.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from core.database import DuplicateDatabase

# Import models at the module level to avoid circular import issues
from core.models import ScanResult

logger = logging.getLogger(__name__)


class ScanHistory:
    """
    A class to manage scan history records using SQLite database.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the scan history manager.
        
        Args:
            db_path: Path to the database file. If None, uses default location.
        """
        self.db_path = Path(db_path) if db_path else Path("duplicates.db")
        self.database = DuplicateDatabase(self.db_path)
    
    def add_scan_result(self, scan_result: ScanResult) -> int:
        """
        Add a new scan result to the history.
        
        Args:
            scan_result: ScanResult model containing the scan results
            
        Returns:
            The ID of the newly created record
        """
        scan_id = self.database.save_scan_result(scan_result)
        logger.info(f"Added scan result: {scan_id} for directory {scan_result.directory}")
        return scan_id
    
    def add_scan_record(self, directory: str, results: Dict, 
                       file_count: int = 0, duplicate_groups: int = 0) -> str:
        """
        Add a new scan record to the history (compatibility method).
        
        Args:
            directory: The directory that was scanned
            results: The results of the scan (not stored in the new system)
            file_count: Number of files scanned
            duplicate_groups: Number of duplicate groups found
            
        Returns:
            The ID of the newly created record
        """
        # This method is kept for compatibility but doesn't store detailed results
        # The new system stores full ScanResult objects instead
        logger.warning("add_scan_record is deprecated. Use add_scan_result with ScanResult model instead.")
        return "deprecated"
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent scan records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent scan records
        """
        return self.database.get_recent_scans(limit)
    
    def get_scan_result(self, scan_id: int) -> Optional[ScanResult]:
        """
        Get a specific scan result by its ID.
        
        Args:
            scan_id: The ID of the scan result
            
        Returns:
            The scan result or None if not found
        """
        return self.database.get_scan_result(scan_id)
    
    def get_scans_by_directory(self, directory: str) -> List[Dict]:
        """
        Get all scan records for a specific directory.
        
        Args:
            directory: The directory to search for
            
        Returns:
            List of scan records for the directory
        """
        # Filter recent scans by directory
        all_scans = self.database.get_recent_scans(limit=100)  # Get more scans to ensure we find matches
        return [scan for scan in all_scans if str(scan['directory']) == directory]
    
    def delete_scan(self, scan_id: int):
        """
        Delete a scan record by its ID.
        
        Args:
            scan_id: The ID of the scan record to delete
        """
        self.database.delete_scan(scan_id)
        logger.info(f"Deleted scan record: {scan_id}")
    
    def clear_history(self):
        """
        Clear all scan history records.
        """
        self.database.clear_all_scans()
        logger.info("Cleared scan history")


def get_scan_history(db_path: str = None) -> ScanHistory:
    """
    Get a scan history instance.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        ScanHistory instance
    """
    return ScanHistory(db_path)