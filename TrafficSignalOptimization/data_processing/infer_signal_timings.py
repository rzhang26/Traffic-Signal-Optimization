"""
Signal Timing Inference Module
Infers signal timings from traffic data patterns.
"""

import logging
from typing import Dict, List, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


def infer_signal_timings(
    traffic_data: List[Dict[str, Any]],
    cycle_length_range: Tuple[int, int] = (45, 120)
) -> Dict[str, Any]:
    """
    Infer signal timing parameters from traffic data.
    
    Args:
        traffic_data: List of traffic data for an intersection
        cycle_length_range: Tuple of (min_cycle, max_cycle) in seconds
        
    Returns:
        Dictionary with inferred signal timing parameters
    """
    # Group data by direction
    direction_data = _group_by_direction(traffic_data)
    
    # Calculate volumes for each direction
    volumes = {}
    for direction, records in direction_data.items():
        total_volume = sum(r.get('volume', 0) for r in records)
        avg_volume = total_volume / len(records) if records else 0
        volumes[direction] = avg_volume
    
    # Determine cycle length based on total demand
    total_volume = sum(volumes.values())
    cycle_length = _calculate_cycle_length(total_volume, cycle_length_range)
    
    # Calculate green splits based on volumes
    green_splits = _calculate_green_splits(volumes, cycle_length)
    
    # Standard yellow and all-red times
    yellow_time = 3.0  # seconds
    all_red_time = 2.0  # seconds
    
    signal_timing = {
        'cycle_length': cycle_length,
        'green_time_north': green_splits.get('N', 0),
        'green_time_south': green_splits.get('S', 0),
        'green_time_east': green_splits.get('E', 0),
        'green_time_west': green_splits.get('W', 0),
        'yellow_time': yellow_time,
        'all_red_time': all_red_time,
        'volumes': volumes
    }
    
    logger.info(f"Inferred signal timing: cycle={cycle_length}s, splits={green_splits}")
    return signal_timing


def _group_by_direction(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group traffic data by direction."""
    grouped = {}
    
    for record in data:
        direction = record.get('direction', 'N').upper()
        if direction not in grouped:
            grouped[direction] = []
        grouped[direction].append(record)
    
    return grouped


def _calculate_cycle_length(total_volume: float, cycle_range: Tuple[int, int]) -> int:
    """
    Calculate appropriate cycle length based on traffic volume.
    
    Args:
        total_volume: Total traffic volume across all approaches
        cycle_range: Allowable cycle length range
        
    Returns:
        Cycle length in seconds
    """
    min_cycle, max_cycle = cycle_range
    
    # Use volume to determine cycle length
    # Low volume: shorter cycles
    # High volume: longer cycles
    # initially tried Webster's optimal cycle formula but this heuristic works better w/ limited data
    if total_volume < 500:
        cycle_length = min_cycle
    elif total_volume > 2000:
        cycle_length = max_cycle
    else:
        # Linear interpolation between min and max
        ratio = (total_volume - 500) / (2000 - 500)
        cycle_length = int(min_cycle + ratio * (max_cycle - min_cycle))
    
    # Round to nearest 5 seconds for practical implementation
    cycle_length = round(cycle_length / 5) * 5
    
    return max(min_cycle, min(max_cycle, cycle_length))


def _calculate_green_splits(
    volumes: Dict[str, float], 
    cycle_length: int
) -> Dict[str, float]:
    """
    Calculate green time splits for each direction based on volumes.
    
    Args:
        volumes: Dictionary of volumes by direction
        cycle_length: Total cycle length in seconds
        
    Returns:
        Dictionary of green times by direction
    """
    # Reserve time for yellow and all-red for each phase
    yellow_time = 3.0
    all_red_time = 2.0
    lost_time_per_phase = yellow_time + all_red_time
    
    # Assume 2-phase operation (NS and EW)
    num_phases = 2
    total_lost_time = lost_time_per_phase * num_phases
    effective_green_time = cycle_length - total_lost_time
    
    # Calculate phase volumes
    ns_volume = volumes.get('N', 0) + volumes.get('S', 0)
    ew_volume = volumes.get('E', 0) + volumes.get('W', 0)
    total_phase_volume = ns_volume + ew_volume
    
    if total_phase_volume == 0:
        # Equal split if no volume data
        green_splits = {
            'N': effective_green_time / 2,
            'S': effective_green_time / 2,
            'E': effective_green_time / 2,
            'W': effective_green_time / 2
        }
    else:
        # Proportional split based on volumes
        ns_ratio = ns_volume / total_phase_volume
        ew_ratio = ew_volume / total_phase_volume
        
        # Apply minimum green time constraint (10 seconds)
        min_green = 10.0
        
        ns_green = max(min_green, effective_green_time * ns_ratio)
        ew_green = max(min_green, effective_green_time * ew_ratio)
        
        # Normalize if sum exceeds available time
        total_green = ns_green + ew_green
        if total_green > effective_green_time:
            scale_factor = effective_green_time / total_green
            ns_green *= scale_factor
            ew_green *= scale_factor
        
        green_splits = {
            'N': ns_green,
            'S': ns_green,
            'E': ew_green,
            'W': ew_green
        }
    
    return green_splits


def estimate_coordination(
    intersection_timings: List[Dict[str, Any]],
    distances: List[float],
    avg_speed: float = 35.0
) -> Dict[str, Any]:
    """
    Estimate coordination offsets for a series of intersections.
    
    Args:
        intersection_timings: List of signal timing dictionaries for each intersection
        distances: List of distances between consecutive intersections (in feet)
        avg_speed: Average travel speed in mph
        
    Returns:
        Dictionary with coordination parameters
    """
    if len(intersection_timings) < 2:
        logger.warning("Need at least 2 intersections for coordination")
        return {}
    
    # Convert speed to feet per second
    speed_fps = avg_speed * 5280 / 3600
    
    # Calculate travel times between intersections
    travel_times = [dist / speed_fps for dist in distances]
    
    # Use first intersection as reference (offset = 0)
    offsets = [0]
    
    # Calculate offsets for subsequent intersections
    for i, travel_time in enumerate(travel_times):
        # Offset is travel time modulo cycle length
        cycle_length = intersection_timings[i + 1]['cycle_length']
        offset = travel_time % cycle_length
        offsets.append(round(offset, 1))
    
    coordination = {
        'offsets': offsets,
        'travel_times': travel_times,
        'reference_intersection': 0,
        'coordination_speed': avg_speed
    }
    
    logger.info(f"Estimated coordination offsets: {offsets}")
    return coordination


def adjust_for_pedestrians(
    signal_timing: Dict[str, Any],
    crossing_width: float = 40.0,
    walking_speed: float = 3.5
) -> Dict[str, Any]:
    """
    Adjust signal timing to accommodate pedestrian crossing requirements.
    
    Args:
        signal_timing: Current signal timing parameters
        crossing_width: Street crossing width in feet
        walking_speed: Pedestrian walking speed in feet per second
        
    Returns:
        Adjusted signal timing
    """
    # Calculate minimum pedestrian crossing time
    min_ped_time = crossing_width / walking_speed
    
    # Add buffer time
    required_ped_time = min_ped_time + 4.0  # 4 seconds buffer
    
    adjusted_timing = signal_timing.copy()
    
    # Ensure each green phase is long enough for pedestrians
    for direction in ['north', 'south', 'east', 'west']:
        green_key = f'green_time_{direction}'
        if green_key in adjusted_timing:
            current_green = adjusted_timing[green_key]
            if current_green < required_ped_time:
                logger.info(f"Adjusting {direction} green time from {current_green} to {required_ped_time} for pedestrians")
                adjusted_timing[green_key] = required_ped_time
    
    return adjusted_timing

