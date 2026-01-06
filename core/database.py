"""
Database module for the Duplicate File Finder application.

This module provides functions to store and retrieve scan results using SQLite.
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging
from core.models import ScanResult, DuplicateGroup, FileInfo

logger = logging.getLogger(__name__)


class DuplicateDatabase:
    """Class for managing the SQLite database for duplicate file scan results."""
    
    def __init__(self, db_path: Path = Path("duplicates.db")):
        """
        Initialize the database connection and create tables if they don't exist.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create scans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    directory TEXT NOT NULL,
                    scanned_files_count INTEGER,
                    scan_start_time TEXT,
                    scan_end_time TEXT,
                    scan_duration REAL,
                    methods_used TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create duplicate_groups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    group_id TEXT,
                    detection_method TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                )
            """)
            
            # Create files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    path TEXT NOT NULL,
                    size INTEGER,
                    hash_value TEXT,
                    created_time TEXT,
                    modified_time TEXT,
                    extension TEXT,
                    name TEXT,
                    FOREIGN KEY (group_id) REFERENCES duplicate_groups (id)
                )
            """)
            
            conn.commit()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_scan_result(self, scan_result: ScanResult) -> int:
        """
        Save a scan result to the database.
        
        Args:
            scan_result: ScanResult model containing the scan results
            
        Returns:
            ID of the saved scan record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert scan record
            cursor.execute("""
                INSERT INTO scans (
                    directory,
                    scanned_files_count,
                    scan_start_time,
                    scan_end_time,
                    scan_duration,
                    methods_used
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(scan_result.directory),
                scan_result.scanned_files_count,
                scan_result.scan_start_time.isoformat(),
                scan_result.scan_end_time.isoformat(),
                scan_result.scan_duration,
                json.dumps(scan_result.methods_used)
            ))
            
            scan_id = cursor.lastrowid
            
            # Insert duplicate groups and their files
            for group in scan_result.duplicate_groups:
                cursor.execute("""
                    INSERT INTO duplicate_groups (
                        scan_id,
                        group_id,
                        detection_method
                    ) VALUES (?, ?, ?)
                """, (scan_id, group.id, group.detection_method))
                
                group_db_id = cursor.lastrowid
                
                # Insert files in the group
                for file_info in group.files:
                    cursor.execute("""
                        INSERT INTO files (
                            group_id,
                            path,
                            size,
                            hash_value,
                            created_time,
                            modified_time,
                            extension,
                            name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        group_db_id,
                        str(file_info.path),
                        file_info.size,
                        file_info.hash_value,
                        file_info.created_time.isoformat() if file_info.created_time else None,
                        file_info.modified_time.isoformat() if file_info.modified_time else None,
                        file_info.extension,
                        file_info.name
                    ))
            
            conn.commit()
            logger.info(f"Saved scan result with ID {scan_id} to database")
            return scan_id
    
    def get_scan_result(self, scan_id: int) -> Optional[ScanResult]:
        """
        Retrieve a scan result from the database.
        
        Args:
            scan_id: ID of the scan to retrieve
            
        Returns:
            ScanResult model or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get scan record
            cursor.execute("""
                SELECT * FROM scans WHERE id = ?
            """, (scan_id,))
            
            scan_row = cursor.fetchone()
            if not scan_row:
                return None
            
            # Parse the scan record
            (
                id_val, directory, scanned_files_count, scan_start_time_str, 
                scan_end_time_str, scan_duration, methods_used_str, created_at
            ) = scan_row
            
            scan_start_time = datetime.fromisoformat(scan_start_time_str)
            scan_end_time = datetime.fromisoformat(scan_end_time_str)
            methods_used = json.loads(methods_used_str)
            
            # Get duplicate groups for this scan
            cursor.execute("""
                SELECT * FROM duplicate_groups WHERE scan_id = ?
            """, (scan_id,))
            
            group_rows = cursor.fetchall()
            duplicate_groups = []
            
            for group_row in group_rows:
                (
                    group_id, scan_id_ref, group_id_str, detection_method
                ) = group_row
                
                # Get files for this group
                cursor.execute("""
                    SELECT * FROM files WHERE group_id = ?
                """, (group_id,))
                
                file_rows = cursor.fetchall()
                files = []
                
                for file_row in file_rows:
                    (
                        file_id, group_id_ref, path, size, hash_value,
                        created_time_str, modified_time_str, extension, name
                    ) = file_row
                    
                    file_info = FileInfo(
                        path=Path(path),
                        size=size,
                        hash_value=hash_value,
                        created_time=datetime.fromisoformat(created_time_str) if created_time_str else None,
                        modified_time=datetime.fromisoformat(modified_time_str) if modified_time_str else None,
                        extension=extension,
                        name=name
                    )
                    files.append(file_info)
                
                duplicate_group = DuplicateGroup(
                    id=group_id_str,
                    files=files,
                    detection_method=detection_method
                )
                duplicate_groups.append(duplicate_group)
            
            scan_result = ScanResult(
                directory=Path(directory),
                scanned_files_count=scanned_files_count,
                duplicate_groups=duplicate_groups,
                scan_start_time=scan_start_time,
                scan_end_time=scan_end_time,
                scan_duration=scan_duration,
                methods_used=methods_used
            )
            
            return scan_result
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of recent scan records (without full results for performance).
        
        Args:
            limit: Maximum number of scans to return
            
        Returns:
            List of dictionaries containing basic scan information
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, 
                    directory, 
                    scanned_files_count, 
                    scan_start_time, 
                    scan_end_time, 
                    scan_duration,
                    methods_used,
                    created_at
                FROM scans 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            scans = []
            for row in rows:
                (
                    id_val, directory, scanned_files_count, scan_start_time_str, 
                    scan_end_time_str, scan_duration, methods_used_str, created_at
                ) = row
                
                scan_info = {
                    'id': id_val,
                    'directory': directory,
                    'scanned_files_count': scanned_files_count,
                    'scan_start_time': datetime.fromisoformat(scan_start_time_str),
                    'scan_end_time': datetime.fromisoformat(scan_end_time_str),
                    'scan_duration': scan_duration,
                    'methods_used': json.loads(methods_used_str),
                    'created_at': datetime.fromisoformat(created_at)
                }
                scans.append(scan_info)
            
            return scans
    
    def delete_scan(self, scan_id: int):
        """
        Delete a scan and all related data from the database.
        
        Args:
            scan_id: ID of the scan to delete
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete files in groups associated with this scan
            cursor.execute("""
                DELETE FROM files 
                WHERE group_id IN (
                    SELECT id FROM duplicate_groups WHERE scan_id = ?
                )
            """, (scan_id,))
            
            # Delete duplicate groups for this scan
            cursor.execute("""
                DELETE FROM duplicate_groups WHERE scan_id = ?
            """, (scan_id,))
            
            # Delete the scan itself
            cursor.execute("""
                DELETE FROM scans WHERE id = ?
            """, (scan_id,))
            
            conn.commit()
            logger.info(f"Deleted scan result with ID {scan_id} from database")
    
    def clear_all_scans(self):
        """
        Delete all scan records and related data from the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM duplicate_groups")
            cursor.execute("DELETE FROM scans")
            
            conn.commit()
            logger.info("Cleared all scan results from database")