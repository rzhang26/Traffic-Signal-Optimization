"""
Data Interpolation Module
Handles interpolation of missing traffic data.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def interpolate_missing_data(
    data: List[Dict[str, Any]], 
    method: str = 'linear'
) -> List[Dict[str, Any]]:
    """
    Interpolate missing data points in traffic data.
    
    Args:
        data: List of traffic data dictionaries (sorted by timestamp)
        method: Interpolation method ('linear', 'moving_average')
        
    Returns:
        Data with interpolated values
    """
    if not data or len(data) < 2:
        return data
    
    # Sort by timestamp
    sorted_data = sorted(data, key=lambda x: x.get('timestamp', ''))
    
    if method == 'linear':
        return _linear_interpolation(sorted_data)
    elif method == 'moving_average':
        return _moving_average_interpolation(sorted_data)
    else:
        logger.warning(f"Unknown interpolation method: {method}, using linear")
        return _linear_interpolation(sorted_data)


def _linear_interpolation(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Perform linear interpolation on missing values.
    
    Args:
        data: Sorted list of traffic data
        
    Returns:
        Interpolated data
    """
    interpolated_data = []
    
    # Group by station and direction
    grouped = {}
    for record in data:
        key = (record.get('station_id'), record.get('direction'))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(record)
    
    # Interpolate each group
    for key, records in grouped.items():
        if len(records) < 2:
            interpolated_data.extend(records)
            continue
        
        # Extract volumes and timestamps
        volumes = []
        timestamps = []
        indices_with_data = []
        
        for idx, record in enumerate(records):
            volume = record.get('volume')
            if volume is not None and volume > 0:
                volumes.append(volume)
                timestamps.append(idx)
                indices_with_data.append(idx)
        
        if len(volumes) < 2:
            interpolated_data.extend(records)
            continue
        
        # Interpolate missing values
        for idx, record in enumerate(records):
            interpolated_record = record.copy()
            
            if idx not in indices_with_data:
                # Find surrounding points
                before_idx = max([i for i in indices_with_data if i < idx], default=None)
                after_idx = min([i for i in indices_with_data if i > idx], default=None)
                
                if before_idx is not None and after_idx is not None:
                    # Linear interpolation
                    before_vol = records[before_idx]['volume']
                    after_vol = records[after_idx]['volume']
                    weight = (idx - before_idx) / (after_idx - before_idx)
                    interpolated_vol = before_vol + weight * (after_vol - before_vol)
                    interpolated_record['volume'] = int(interpolated_vol)
                    logger.debug(f"Interpolated volume at index {idx}: {interpolated_vol}")
            
            interpolated_data.append(interpolated_record)
    
    return interpolated_data


def _moving_average_interpolation(
    data: List[Dict[str, Any]], 
    window_size: int = 3
) -> List[Dict[str, Any]]:
    """
    Use moving average to fill missing values.
    
    Args:
        data: Sorted list of traffic data
        window_size: Size of moving average window
        
    Returns:
        Interpolated data
    """
    interpolated_data = []
    
    for idx, record in enumerate(data):
        interpolated_record = record.copy()
        
        if interpolated_record.get('volume') is None or interpolated_record['volume'] == 0:
            # Calculate moving average from surrounding records
            start_idx = max(0, idx - window_size)
            end_idx = min(len(data), idx + window_size + 1)
            
            surrounding_volumes = [
                r['volume'] for r in data[start_idx:end_idx]
                if r.get('volume') is not None and r['volume'] > 0
            ]
            
            if surrounding_volumes:
                avg_volume = np.mean(surrounding_volumes)
                interpolated_record['volume'] = int(avg_volume)
                logger.debug(f"Filled missing volume at index {idx} with moving average: {avg_volume}")
        
        interpolated_data.append(interpolated_record)
    
    return interpolated_data


def fill_time_gaps(
    data: List[Dict[str, Any]], 
    interval_minutes: int = 15
) -> List[Dict[str, Any]]:
    """
    Fill gaps in time series data with interpolated values.
    
    Args:
        data: Traffic data sorted by timestamp
        interval_minutes: Expected interval between records
        
    Returns:
        Data with filled time gaps
    """
    if not data:
        return []
    
    filled_data = []
    
    for i in range(len(data) - 1):
        current = data[i]
        next_record = data[i + 1]
        
        filled_data.append(current)
        
        try:
            current_time = datetime.strptime(current['timestamp'], '%Y-%m-%d %H:%M:%S')
            next_time = datetime.strptime(next_record['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            time_diff = (next_time - current_time).total_seconds() / 60
            
            # If gap is larger than expected interval, fill it
            if time_diff > interval_minutes * 1.5:
                num_gaps = int(time_diff / interval_minutes) - 1
                
                for gap_idx in range(1, num_gaps + 1):
                    gap_time = current_time + timedelta(minutes=interval_minutes * gap_idx)
                    
                    # Interpolate volume
                    weight = gap_idx / (num_gaps + 1)
                    interpolated_volume = current['volume'] + weight * (next_record['volume'] - current['volume'])
                    
                    gap_record = current.copy()
                    gap_record['timestamp'] = gap_time.strftime('%Y-%m-%d %H:%M:%S')
                    gap_record['volume'] = int(interpolated_volume)
                    
                    filled_data.append(gap_record)
                    logger.debug(f"Filled gap at {gap_time}")
        
        except (ValueError, KeyError) as e:
            logger.warning(f"Error processing timestamps: {e}")
            continue
    
    # Add last record
    if data:
        filled_data.append(data[-1])
    
    logger.info(f"Filled time gaps: {len(data)} -> {len(filled_data)} records")
    return filled_data

