"""
Database Management for Traffic Data Storage
Handles SQLite database operations for storing and retrieving traffic data.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for traffic data storage."""
    
    def __init__(self, db_path: str = "traffic_data.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create traffic_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traffic_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    county TEXT NOT NULL,
                    station_id TEXT NOT NULL,
                    direction TEXT,
                    timestamp DATETIME NOT NULL,
                    volume INTEGER,
                    speed REAL,
                    occupancy REAL,
                    data_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(station_id, timestamp, direction)
                )
            """)
            
            # Create intersections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS intersections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intersection_id TEXT UNIQUE NOT NULL,
                    county TEXT NOT NULL,
                    name TEXT,
                    latitude REAL,
                    longitude REAL,
                    num_approaches INTEGER DEFAULT 4,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create signal_timings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signal_timings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intersection_id TEXT NOT NULL,
                    cycle_length INTEGER NOT NULL,
                    green_time_north REAL,
                    green_time_south REAL,
                    green_time_east REAL,
                    green_time_west REAL,
                    yellow_time REAL DEFAULT 3.0,
                    all_red_time REAL DEFAULT 2.0,
                    is_optimized BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (intersection_id) REFERENCES intersections(intersection_id)
                )
            """)
            
            # Create optimization_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intersection_id TEXT NOT NULL,
                    signal_timing_id INTEGER,
                    throughput REAL,
                    avg_delay REAL,
                    avg_stops REAL,
                    max_queue_length REAL,
                    fitness_score REAL,
                    optimization_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (intersection_id) REFERENCES intersections(intersection_id),
                    FOREIGN KEY (signal_timing_id) REFERENCES signal_timings(id)
                )
            """)
            
            # Create indices for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_county 
                ON traffic_data(county)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_timestamp 
                ON traffic_data(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_station 
                ON traffic_data(station_id)
            """)
            
            self.connection.commit()
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def insert_traffic_data(self, data: List[Dict[str, Any]]) -> int:
        """
        Insert traffic data records into database.
        
        Args:
            data: List of traffic data dictionaries
            
        Returns:
            Number of records inserted
        """
        if not data:
            return 0
        
        cursor = self.connection.cursor()
        inserted = 0
        
        for record in data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO traffic_data 
                    (county, station_id, direction, timestamp, volume, speed, occupancy, data_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get('county', ''),
                    record.get('station_id', ''),
                    record.get('direction', ''),
                    record.get('timestamp'),
                    record.get('volume'),
                    record.get('speed'),
                    record.get('occupancy'),
                    record.get('data_type', 'continuous')
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                logger.warning(f"Error inserting record: {e}")
                continue
        
        self.connection.commit()
        logger.info(f"Inserted {inserted} traffic data records")
        return inserted
    
    def get_traffic_data_by_county(
        self, 
        county: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve traffic data for a specific county.
        
        Args:
            county: County name
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            List of traffic data records
        """
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM traffic_data WHERE county = ?"
        params = [county]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp"
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
    
    def insert_intersection(self, intersection_data: Dict[str, Any]) -> int:
        """
        Insert intersection information.
        
        Args:
            intersection_data: Dictionary containing intersection details
            
        Returns:
            Intersection ID
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO intersections 
                (intersection_id, county, name, latitude, longitude, num_approaches)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                intersection_data.get('intersection_id'),
                intersection_data.get('county'),
                intersection_data.get('name'),
                intersection_data.get('latitude'),
                intersection_data.get('longitude'),
                intersection_data.get('num_approaches', 4)
            ))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting intersection: {e}")
            raise
    
    def insert_signal_timing(self, timing_data: Dict[str, Any]) -> int:
        """
        Insert signal timing configuration.
        
        Args:
            timing_data: Dictionary containing signal timing details
            
        Returns:
            Signal timing ID
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO signal_timings 
                (intersection_id, cycle_length, green_time_north, green_time_south,
                 green_time_east, green_time_west, yellow_time, all_red_time, is_optimized)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timing_data.get('intersection_id'),
                timing_data.get('cycle_length'),
                timing_data.get('green_time_north'),
                timing_data.get('green_time_south'),
                timing_data.get('green_time_east'),
                timing_data.get('green_time_west'),
                timing_data.get('yellow_time', 3.0),
                timing_data.get('all_red_time', 2.0),
                timing_data.get('is_optimized', 0)
            ))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting signal timing: {e}")
            raise
    
    def insert_optimization_result(self, result_data: Dict[str, Any]) -> int:
        """
        Insert optimization results.
        
        Args:
            result_data: Dictionary containing optimization results
            
        Returns:
            Result ID
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO optimization_results 
                (intersection_id, signal_timing_id, throughput, avg_delay, 
                 avg_stops, max_queue_length, fitness_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result_data.get('intersection_id'),
                result_data.get('signal_timing_id'),
                result_data.get('throughput'),
                result_data.get('avg_delay'),
                result_data.get('avg_stops'),
                result_data.get('max_queue_length'),
                result_data.get('fitness_score')
            ))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting optimization result: {e}")
            raise
    
    def get_intersections_by_county(self, county: str) -> List[Dict[str, Any]]:
        """Get all intersections in a county."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM intersections WHERE county = ?", (county,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

