"""
Fitness Functions Module
Defines fitness functions for signal timing optimization.
"""

import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


def calculate_throughput(simulation_results: Dict[str, Any]) -> float:
    """
    Calculate throughput fitness (higher is better).
    
    Args:
        simulation_results: Dictionary with simulation results
        
    Returns:
        Throughput score (vehicles per hour)
    """
    return simulation_results.get('throughput', 0)


def calculate_delay(simulation_results: Dict[str, Any]) -> float:
    """
    Calculate delay fitness (lower is better, so we return negative).
    
    Args:
        simulation_results: Dictionary with simulation results
        
    Returns:
        Negative average delay
    """
    avg_delay = simulation_results.get('avg_delay', 0)
    # Return negative because we want to minimize delay
    return -avg_delay


def calculate_stops(simulation_results: Dict[str, Any]) -> float:
    """
    Calculate stops fitness (lower is better, so we return negative).
    
    Args:
        simulation_results: Dictionary with simulation results
        
    Returns:
        Negative average stops
    """
    avg_stops = simulation_results.get('avg_stops', 0)
    return -avg_stops


def calculate_queue_length(simulation_results: Dict[str, Any]) -> float:
    """
    Calculate queue length fitness (lower is better).
    
    Args:
        simulation_results: Dictionary with simulation results
        
    Returns:
        Negative maximum queue length
    """
    max_queue = simulation_results.get('max_queue_length', 0)
    return -max_queue


def composite_fitness(
    simulation_results: Dict[str, Any],
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate composite fitness score combining multiple objectives.
    
    Args:
        simulation_results: Dictionary with simulation results
        weights: Dictionary of weights for each objective
        
    Returns:
        Composite fitness score (higher is better)
    """
    if weights is None:
        weights = {
            'throughput': 0.35,
            'delay': 0.35,
            'stops': 0.15,
            'queue': 0.15
        }
    
    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    # Calculate individual fitness components
    throughput_score = calculate_throughput(simulation_results)
    delay_score = calculate_delay(simulation_results)
    stops_score = calculate_stops(simulation_results)
    queue_score = calculate_queue_length(simulation_results)
    
    # Normalize scores to similar scales
    # Throughput is typically 0-2000 veh/hr
    throughput_normalized = throughput_score / 2000.0
    
    # Delay is typically 0-100 seconds (negative)
    delay_normalized = delay_score / -100.0
    
    # Stops is typically 0-2 (negative)
    stops_normalized = stops_score / -2.0
    
    # Queue is typically 0-50 vehicles (negative)
    queue_normalized = queue_score / -50.0
    
    # Composite score
    fitness = (
        weights['throughput'] * throughput_normalized +
        weights['delay'] * delay_normalized +
        weights['stops'] * stops_normalized +
        weights['queue'] * queue_normalized
    )
    
    return fitness


def penalty_for_constraints(signal_timing: Dict[str, Any]) -> float:
    """
    Calculate penalty for constraint violations.
    
    Args:
        signal_timing: Signal timing parameters
        
    Returns:
        Penalty value (0 if no violations, negative otherwise)
    """
    penalty = 0.0
    
    # Minimum green time constraint (10 seconds)
    min_green = 10.0
    for direction in ['north', 'south', 'east', 'west']:
        green_key = f'green_time_{direction}'
        green_time = signal_timing.get(green_key, 0)
        if green_time < min_green:
            penalty -= (min_green - green_time) * 10  # Heavy penalty
    
    # Cycle length constraint
    cycle_length = signal_timing.get('cycle_length', 0)
    if cycle_length < 45 or cycle_length > 120:
        penalty -= abs(cycle_length - 80) * 5
    
    # Green times should sum to less than cycle length
    total_green = sum([
        signal_timing.get(f'green_time_{d}', 0)
        for d in ['north', 'south', 'east', 'west']
    ])
    
    # Account for lost time (yellow + all-red per phase)
    lost_time = (signal_timing.get('yellow_time', 3.0) + signal_timing.get('all_red_time', 2.0)) * 2
    available_green = cycle_length - lost_time
    
    if total_green > available_green:
        penalty -= (total_green - available_green) * 20
    
    return penalty


def evaluate_fitness_with_constraints(
    simulation_results: Dict[str, Any],
    signal_timing: Dict[str, Any],
    weights: Dict[str, float] = None
) -> float:
    """
    Evaluate fitness including constraint penalties.
    
    Args:
        simulation_results: Dictionary with simulation results
        signal_timing: Signal timing parameters
        weights: Weights for fitness components
        
    Returns:
        Total fitness score
    """
    base_fitness = composite_fitness(simulation_results, weights)
    constraint_penalty = penalty_for_constraints(signal_timing)
    
    total_fitness = base_fitness + constraint_penalty
    
    return total_fitness


def compare_scenarios(
    baseline_results: Dict[str, Any],
    optimized_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare baseline and optimized scenarios.
    
    Args:
        baseline_results: Simulation results for baseline
        optimized_results: Simulation results for optimized timing
        
    Returns:
        Dictionary with comparison metrics
    """
    comparison = {}
    
    metrics = ['throughput', 'avg_delay', 'avg_stops', 'max_queue_length']
    
    for metric in metrics:
        baseline_value = baseline_results.get(metric, 0)
        optimized_value = optimized_results.get(metric, 0)
        
        if baseline_value != 0:
            improvement = ((optimized_value - baseline_value) / baseline_value) * 100
        else:
            improvement = 0
        
        comparison[metric] = {
            'baseline': baseline_value,
            'optimized': optimized_value,
            'improvement_percent': improvement
        }
    
    # Overall fitness improvement
    baseline_fitness = composite_fitness(baseline_results)
    optimized_fitness = composite_fitness(optimized_results)
    
    if baseline_fitness != 0:
        fitness_improvement = ((optimized_fitness - baseline_fitness) / abs(baseline_fitness)) * 100
    else:
        fitness_improvement = 0
    
    comparison['overall_fitness'] = {
        'baseline': baseline_fitness,
        'optimized': optimized_fitness,
        'improvement_percent': fitness_improvement
    }
    
    return comparison


def calculate_coordination_score(
    intersection_results: list[Dict[str, Any]],
    coordination_params: Dict[str, Any]
) -> float:
    """
    Calculate score for signal coordination across multiple intersections.
    
    Args:
        intersection_results: List of simulation results for each intersection
        coordination_params: Coordination parameters (offsets, etc.)
        
    Returns:
        Coordination score (higher is better)
    """
    if len(intersection_results) < 2:
        return 0.0
    
    # Calculate average progression for each direction
    total_progression = 0.0
    
    for results in intersection_results:
        # Platoon progression is indicated by lower delays
        avg_delay = results.get('avg_delay', 100)
        # Lower delay indicates better progression
        progression_score = max(0, 100 - avg_delay) / 100
        total_progression += progression_score
    
    # Average coordination score
    coordination_score = total_progression / len(intersection_results)
    
    return coordination_score

