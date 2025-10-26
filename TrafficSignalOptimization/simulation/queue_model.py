"""
Queue Model Module
Implements queuing theory models for traffic flow simulation.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class QueueModel:
    """
    Implements M/M/1 and M/D/1 queuing models for traffic analysis.
    """
    
    def __init__(self, service_rate: float = 0.5):
        """
        Initialize queue model.
        
        Args:
            service_rate: Service rate (vehicles per second)
        """
        self.service_rate = service_rate
        self.queue_history = []
    
    def calculate_queue_length(
        self,
        arrival_rate: float,
        service_time: float,
        time_period: float
    ) -> Tuple[float, float]:
        """
        Calculate average and maximum queue length.
        
        Args:
            arrival_rate: Vehicle arrival rate (vehicles per second)
            service_time: Available service time (seconds)
            time_period: Total time period (seconds)
            
        Returns:
            Tuple of (average_queue_length, max_queue_length)
        """
        # Calculate utilization factor
        rho = (arrival_rate * time_period) / (service_time * self.service_rate)
        
        if rho >= 1.0:
            # Oversaturated condition
            # Queue grows linearly
            avg_queue = (rho - 1) * service_time * self.service_rate / 2
            max_queue = (rho - 1) * service_time * self.service_rate
            logger.warning(f"Oversaturated condition: rho={rho:.2f}")
        else:
            # Under-saturated condition - use M/M/1 formula
            avg_queue = rho * rho / (1 - rho)
            max_queue = avg_queue * 2  # Approximate maximum
        
        return avg_queue, max_queue
    
    def calculate_delay(
        self,
        arrival_rate: float,
        green_time: float,
        red_time: float
    ) -> Dict[str, float]:
        """
        Calculate average delay per vehicle using Webster's formula.
        
        Args:
            arrival_rate: Vehicle arrival rate (vehicles per second)
            green_time: Green time duration (seconds)
            red_time: Red time duration (seconds)
            
        Returns:
            Dictionary with delay metrics
        """
        cycle_length = green_time + red_time
        
        # Calculate degree of saturation
        capacity = self.service_rate * green_time / cycle_length
        x = arrival_rate / capacity if capacity > 0 else 1.0
        
        # Webster's formula for uniform delay - tried HCM2010 method but Webster is simpler & close enough
        if x < 1.0:
            uniform_delay = (cycle_length * (1 - green_time/cycle_length)**2) / (2 * (1 - x * green_time/cycle_length))
        else:
            # Oversaturated - use alternative formula (TODO: should probably use Akcelik's equation here)
            uniform_delay = cycle_length * 0.5
        
        # Random delay component
        random_delay = (x * x) / (2 * arrival_rate * (1 - x)) if x < 1.0 else cycle_length * 0.25
        
        # Total delay
        total_delay = uniform_delay + random_delay
        
        return {
            'uniform_delay': uniform_delay,
            'random_delay': random_delay,
            'total_delay': total_delay,
            'saturation': x
        }
    
    def calculate_stops(
        self,
        arrival_rate: float,
        green_time: float,
        cycle_length: float
    ) -> float:
        """
        Calculate proportion of vehicles that must stop.
        
        Args:
            arrival_rate: Vehicle arrival rate (vehicles per second)
            green_time: Green time duration (seconds)
            cycle_length: Total cycle length (seconds)
            
        Returns:
            Proportion of vehicles that stop (0 to 1)
        """
        # Probability of arrival during red
        red_time = cycle_length - green_time
        prob_stop = red_time / cycle_length
        
        # Adjust for queue spillback
        x = (arrival_rate * cycle_length) / (self.service_rate * green_time)
        if x > 0.8:
            # Increase stop probability for high saturation
            prob_stop = min(1.0, prob_stop * (1 + (x - 0.8)))
        
        return prob_stop
    
    def simulate_queue_evolution(
        self,
        arrival_rate: float,
        green_time: float,
        red_time: float,
        num_cycles: int = 10
    ) -> List[Dict[str, float]]:
        """
        Simulate queue evolution over multiple signal cycles.
        
        Args:
            arrival_rate: Vehicle arrival rate (vehicles per second)
            green_time: Green time duration (seconds)
            red_time: Red time duration (seconds)
            num_cycles: Number of cycles to simulate
            
        Returns:
            List of dictionaries with queue metrics per cycle
        """
        cycle_length = green_time + red_time
        queue_evolution = []
        
        current_queue = 0
        
        for cycle in range(num_cycles):
            # Vehicles arriving during cycle
            arrivals = arrival_rate * cycle_length
            
            # Vehicles served during green
            service_capacity = self.service_rate * green_time
            
            # Queue at start of green
            queue_at_green = current_queue
            
            # Vehicles served
            served = min(queue_at_green + arrivals, service_capacity)
            
            # Queue at end of cycle
            current_queue = max(0, queue_at_green + arrivals - served)
            
            # Maximum queue during cycle (occurs at end of red)
            max_queue = queue_at_green + (arrival_rate * red_time)
            
            cycle_data = {
                'cycle': cycle,
                'arrivals': arrivals,
                'served': served,
                'queue_start': queue_at_green,
                'queue_end': current_queue,
                'max_queue': max_queue,
                'delay': (queue_at_green + current_queue) / 2 * cycle_length / arrivals if arrivals > 0 else 0
            }
            
            queue_evolution.append(cycle_data)
        
        self.queue_history = queue_evolution
        return queue_evolution
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get aggregate performance metrics from queue history.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.queue_history:
            return {}
        
        avg_queue = np.mean([c['queue_end'] for c in self.queue_history])
        max_queue = max([c['max_queue'] for c in self.queue_history])
        avg_delay = np.mean([c['delay'] for c in self.queue_history])
        total_served = sum([c['served'] for c in self.queue_history])
        
        return {
            'avg_queue_length': avg_queue,
            'max_queue_length': max_queue,
            'avg_delay': avg_delay,
            'total_throughput': total_served
        }


def calculate_capacity(
    saturation_flow: float,
    green_time: float,
    cycle_length: float,
    lost_time: float = 5.0
) -> float:
    """
    Calculate intersection approach capacity.
    
    Args:
        saturation_flow: Saturation flow rate (vehicles per hour per lane)
        green_time: Effective green time (seconds)
        cycle_length: Cycle length (seconds)
        lost_time: Lost time per cycle (seconds)
        
    Returns:
        Capacity in vehicles per hour
    """
    effective_green = max(0, green_time - lost_time)
    green_ratio = effective_green / cycle_length
    capacity = saturation_flow * green_ratio
    
    return capacity


def level_of_service(delay: float) -> str:
    """
    Determine Level of Service (LOS) based on delay.
    
    Args:
        delay: Average delay per vehicle (seconds)
        
    Returns:
        LOS grade (A-F)
    """
    if delay <= 10:
        return 'A'
    elif delay <= 20:
        return 'B'
    elif delay <= 35:
        return 'C'
    elif delay <= 55:
        return 'D'
    elif delay <= 80:
        return 'E'
    else:
        return 'F'

