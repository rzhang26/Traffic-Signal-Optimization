"""
Unit tests for data processing module.
"""

import unittest
from data_processing.validate_data import validate_traffic_data, clean_data, get_peak_hours
from data_processing.interpolate import interpolate_missing_data
from data_processing.infer_signal_timings import infer_signal_timings, estimate_coordination


class TestDataValidation(unittest.TestCase):
    """Test data validation functionality."""
    
    def test_validate_valid_data(self):
        """Test validation with valid data."""
        data = [
            {
                'station_id': 'ST_001',
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500,
                'speed': 35.0,
                'occupancy': 25.0
            }
        ]
        
        valid_data, errors = validate_traffic_data(data)
        self.assertEqual(len(valid_data), 1)
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_station_id(self):
        """Test validation with missing station_id."""
        data = [
            {
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500
            }
        ]
        
        valid_data, errors = validate_traffic_data(data)
        self.assertEqual(len(valid_data), 0)
        self.assertGreater(len(errors), 0)
    
    def test_validate_invalid_volume(self):
        """Test validation with invalid volume."""
        data = [
            {
                'station_id': 'ST_001',
                'timestamp': '2025-01-01 12:00:00',
                'volume': -100
            }
        ]
        
        valid_data, errors = validate_traffic_data(data)
        self.assertEqual(len(valid_data), 0)
    
    def test_clean_data(self):
        """Test data cleaning."""
        data = [
            {
                'station_id': 'ST_001',
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500
            },
            {
                'station_id': 'ST_001',
                'timestamp': '2025-01-01 12:15:00',
                'volume': None
            }
        ]
        
        cleaned = clean_data(data)
        self.assertEqual(len(cleaned), 2)
        # Second record should have filled volume
        self.assertIsNotNone(cleaned[1]['volume'])
    
    def test_get_peak_hours(self):
        """Test peak hour identification."""
        data = []
        for hour in range(24):
            # Create higher volume during peak hours
            volume = 800 if (7 <= hour <= 9 or 16 <= hour <= 18) else 300
            data.append({
                'timestamp': f'2025-01-01 {hour:02d}:00:00',
                'volume': volume
            })
        
        am_peak, pm_peak = get_peak_hours(data)
        self.assertTrue(6 <= int(am_peak) <= 11)
        self.assertTrue(15 <= int(pm_peak) <= 19)


class TestDataInterpolation(unittest.TestCase):
    """Test data interpolation functionality."""
    
    def test_linear_interpolation(self):
        """Test linear interpolation."""
        data = [
            {
                'station_id': 'ST_001',
                'direction': 'N',
                'timestamp': '2025-01-01 12:00:00',
                'volume': 500
            },
            {
                'station_id': 'ST_001',
                'direction': 'N',
                'timestamp': '2025-01-01 12:15:00',
                'volume': None
            },
            {
                'station_id': 'ST_001',
                'direction': 'N',
                'timestamp': '2025-01-01 12:30:00',
                'volume': 700
            }
        ]
        
        interpolated = interpolate_missing_data(data, method='linear')
        self.assertEqual(len(interpolated), 3)


class TestSignalTimingInference(unittest.TestCase):
    """Test signal timing inference."""
    
    def test_infer_signal_timings(self):
        """Test signal timing inference."""
        data = [
            {'direction': 'N', 'volume': 600},
            {'direction': 'S', 'volume': 600},
            {'direction': 'E', 'volume': 400},
            {'direction': 'W', 'volume': 400}
        ]
        
        timing = infer_signal_timings(data)
        
        self.assertIn('cycle_length', timing)
        self.assertIn('green_time_north', timing)
        self.assertGreaterEqual(timing['cycle_length'], 45)
        self.assertLessEqual(timing['cycle_length'], 120)
    
    def test_estimate_coordination(self):
        """Test coordination estimation."""
        timings = [
            {'cycle_length': 90, 'green_time_north': 35},
            {'cycle_length': 90, 'green_time_north': 35}
        ]
        
        distances = [500]  # 500 feet between intersections
        
        coordination = estimate_coordination(timings, distances, avg_speed=35)
        
        self.assertIn('offsets', coordination)
        self.assertEqual(len(coordination['offsets']), 2)


if __name__ == '__main__':
    unittest.main()

