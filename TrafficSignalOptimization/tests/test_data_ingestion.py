"""
Unit tests for data ingestion module.
"""

import unittest
import os
import tempfile
from datetime import datetime
from data_ingestion.database import DatabaseManager
from data_ingestion.fetch_data import TrafficDataFetcher


class TestDatabaseManager(unittest.TestCase):
    """Test database management functionality."""
    
    def setUp(self):
        """Setup test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Cleanup test database."""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization."""
        self.assertIsNotNone(self.db.connection)
    
    def test_insert_traffic_data(self):
        """Test inserting traffic data."""
        test_data = [
            {
                'county': 'Test County',
                'station_id': 'TEST_001',
                'direction': 'N',
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500,
                'speed': 35.0,
                'occupancy': 25.0,
                'data_type': 'test'
            }
        ]
        
        inserted = self.db.insert_traffic_data(test_data)
        self.assertEqual(inserted, 1)
    
    def test_get_traffic_data_by_county(self):
        """Test retrieving traffic data by county."""
        test_data = [
            {
                'county': 'Albany',
                'station_id': 'ALB_001',
                'direction': 'N',
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500,
                'speed': 35.0,
                'occupancy': 25.0
            }
        ]
        
        self.db.insert_traffic_data(test_data)
        results = self.db.get_traffic_data_by_county('Albany')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['county'], 'Albany')
    
    def test_insert_intersection(self):
        """Test inserting intersection data."""
        intersection_data = {
            'intersection_id': 'INT_001',
            'county': 'Albany',
            'name': 'Test Intersection',
            'latitude': 42.6526,
            'longitude': -73.7562,
            'num_approaches': 4
        }
        
        result = self.db.insert_intersection(intersection_data)
        self.assertIsNotNone(result)
    
    def test_insert_signal_timing(self):
        """Test inserting signal timing data."""
        # First insert intersection
        intersection_data = {
            'intersection_id': 'INT_001',
            'county': 'Albany',
            'name': 'Test Intersection'
        }
        self.db.insert_intersection(intersection_data)
        
        # Insert timing
        timing_data = {
            'intersection_id': 'INT_001',
            'cycle_length': 90,
            'green_time_north': 35.0,
            'green_time_south': 35.0,
            'green_time_east': 30.0,
            'green_time_west': 30.0
        }
        
        result = self.db.insert_signal_timing(timing_data)
        self.assertIsNotNone(result)


class TestTrafficDataFetcher(unittest.TestCase):
    """Test traffic data fetching functionality."""
    
    def test_fetcher_initialization(self):
        """Test fetcher initialization."""
        fetcher = TrafficDataFetcher()
        self.assertIsNotNone(fetcher)
    
    def test_parse_traffic_data(self):
        """Test parsing raw traffic data."""
        fetcher = TrafficDataFetcher()
        
        raw_data = [
            {
                'county': 'Albany',
                'station_id': 'ST_001',
                'direction': 'N',
                'date': '2025-01-01T12:00:00',
                'volume': 500
            }
        ]
        
        parsed = fetcher._parse_traffic_data(raw_data, 'test')
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['county'], 'Albany')


if __name__ == '__main__':
    unittest.main()

