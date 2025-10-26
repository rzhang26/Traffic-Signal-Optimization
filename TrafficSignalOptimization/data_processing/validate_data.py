"""
Data Validation Module
Validates and cleans traffic data for processing.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


def validate_traffic_data(data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Validate traffic data records.
    
    Args:
        data: List of traffic data dictionaries
        
    Returns:
        Tuple of (valid_records, error_messages)
    """
    valid_records = []
    errors = []
    
    for idx, record in enumerate(data):
        # Check required fields
        if not record.get('station_id'):
            errors.append(f"Record {idx}: Missing station_id")
            continue
        
        if not record.get('timestamp'):
            errors.append(f"Record {idx}: Missing timestamp")
            continue
        
        # Validate volume
        volume = record.get('volume')
        if volume is not None:
            if not isinstance(volume, (int, float)) or volume < 0:
                errors.append(f"Record {idx}: Invalid volume {volume}")
                continue
            if volume > 10000:  # Sanity check for unrealistic values
                logger.warning(f"Record {idx}: Unusually high volume {volume}")
        
        # Validate speed
        speed = record.get('speed')
        if speed is not None:
            if not isinstance(speed, (int, float)) or speed < 0 or speed > 150:
                errors.append(f"Record {idx}: Invalid speed {speed}")
                continue
        
        # Validate occupancy
        occupancy = record.get('occupancy')
        if occupancy is not None:
            if not isinstance(occupancy, (int, float)) or occupancy < 0 or occupancy > 100:
                errors.append(f"Record {idx}: Invalid occupancy {occupancy}")
                continue
        
        valid_records.append(record)
    
    logger.info(f"Validated {len(valid_records)} out of {len(data)} records")
    if errors:
        logger.warning(f"Found {len(errors)} validation errors")
    
    return valid_records, errors


def clean_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean traffic data by removing outliers and filling missing values.
    
    Args:
        data: List of traffic data dictionaries
        
    Returns:
        Cleaned data
    """
    if not data:
        return []
    
    cleaned_data = []
    
    # Extract volumes for statistical analysis
    volumes = [r['volume'] for r in data if r.get('volume') is not None]
    
    if volumes:
        volume_mean = np.mean(volumes)
        volume_std = np.std(volumes)
        volume_median = np.median(volumes)
        
        # Define outlier thresholds (3 standard deviations)
        # tried 2σ first but was removing too much valid data, 3σ is better
        lower_bound = max(0, volume_mean - 3 * volume_std)
        upper_bound = volume_mean + 3 * volume_std
        
        for record in data:
            cleaned_record = record.copy()
            
            # Handle volume outliers
            if cleaned_record.get('volume') is not None:
                if cleaned_record['volume'] < lower_bound or cleaned_record['volume'] > upper_bound:
                    logger.debug(f"Replacing outlier volume {cleaned_record['volume']} with median {volume_median}")
                    cleaned_record['volume'] = int(volume_median)
            else:
                # Fill missing volumes with median
                cleaned_record['volume'] = int(volume_median)
            
            # Handle missing speeds (use typical urban speed)
            if cleaned_record.get('speed') is None:
                cleaned_record['speed'] = 35.0  # Default urban speed in mph
            
            # Handle missing occupancy
            if cleaned_record.get('occupancy') is None:
                # Estimate based on volume (rough approximation)
                if cleaned_record['volume'] > volume_mean:
                    cleaned_record['occupancy'] = 50.0
                else:
                    cleaned_record['occupancy'] = 25.0
            
            cleaned_data.append(cleaned_record)
    else:
        # If no volume data, return original data
        cleaned_data = data
    
    logger.info(f"Cleaned {len(cleaned_data)} records")
    return cleaned_data


def aggregate_by_hour(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Aggregate traffic data by hour of day.
    
    Args:
        data: List of traffic data dictionaries
        
    Returns:
        Dictionary mapping hours to traffic records
    """
    hourly_data = {}
    
    for record in data:
        try:
            timestamp = record.get('timestamp', '')
            hour = timestamp.split()[1].split(':')[0] if ' ' in timestamp else '00'
            
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(record)
        except (IndexError, AttributeError):
            continue
    
    return hourly_data


def get_peak_hours(data: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Identify AM and PM peak hours from traffic data.
    
    Args:
        data: List of traffic data dictionaries
        
    Returns:
        Tuple of (am_peak_hour, pm_peak_hour)
    """
    hourly_data = aggregate_by_hour(data)
    hourly_volumes = {}
    
    for hour, records in hourly_data.items():
        total_volume = sum(r.get('volume', 0) for r in records)
        hourly_volumes[hour] = total_volume
    
    # Split into AM and PM
    am_hours = {h: v for h, v in hourly_volumes.items() if 6 <= int(h) < 12}
    pm_hours = {h: v for h, v in hourly_volumes.items() if 15 <= int(h) < 20}
    
    am_peak = max(am_hours.items(), key=lambda x: x[1])[0] if am_hours else '08'
    pm_peak = max(pm_hours.items(), key=lambda x: x[1])[0] if pm_hours else '17'
    
    logger.info(f"Peak hours identified: AM={am_peak}:00, PM={pm_peak}:00")
    return am_peak, pm_peak

