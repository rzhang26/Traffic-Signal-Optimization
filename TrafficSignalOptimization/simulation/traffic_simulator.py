"""
Traffic Simulator Module
Implements discrete-event simulation for traffic flow at intersections.
"""

import logging
from typing import Dict, List, Any, Tuple
import numpy as np
from dataclasses import dataclass, field
from .queue_model import QueueModel, calculate_capacity, level_of_service

logger = logging.getLogger(__name__)


@dataclass
class Vehicle:
    """Represents a vehicle in the simulation."""
    id: int
    arrival_time: float
    direction: str
    departure_time: float = 0.0
    delay: float = 0.0
    stops: int = 0


@dataclass
class IntersectionState:
    """Represents the current state of an intersection."""
    current_time: float = 0.0
    current_phase: str = 'NS'  # NS (North-South) or EW (East-West)
    phase_start_time: float = 0.0
    queues: Dict[str, List[Vehicle]] = field(default_factory=lambda: {'N': [], 'S': [], 'E': [], 'W': []})
    vehicles_processed: List[Vehicle] = field(default_factory=list)
    signal_timing: Dict[str, Any] = field(default_factory=dict)


class TrafficSimulator:
    """
    Discrete-event traffic simulation for signalized intersections.
    """
    
    def __init__(
        self,
        signal_timing: Dict[str, Any],
        saturation_flow_rate: float = 1800.0,
        random_seed: int = 42
    ):
        """
        Initialize traffic simulator.
        
        Args:
            signal_timing: Dictionary with signal timing parameters
            saturation_flow_rate: Saturation flow rate (vehicles per hour per lane)
            random_seed: Random seed for reproducibility
        """
        self.signal_timing = signal_timing
        self.saturation_flow_rate = saturation_flow_rate
        self.service_rate = saturation_flow_rate / 3600  # Convert to vehicles per second
        
        self.state = IntersectionState(signal_timing=signal_timing)
        self.queue_model = QueueModel(service_rate=self.service_rate)
        
        np.random.seed(random_seed)
        
        self.vehicle_counter = 0
        self.events = []
    
    def run_simulation(
        self,
        traffic_volumes: Dict[str, float],
        simulation_duration: float = 3600.0
    ) -> Dict[str, Any]:
        """
        Run traffic simulation.
        
        Args:
            traffic_volumes: Dictionary of hourly volumes by direction
            simulation_duration: Simulation duration in seconds
            
        Returns:
            Dictionary with simulation results
        """
        logger.info(f"Starting simulation for {simulation_duration} seconds")
        
        # Reset state
        self.state = IntersectionState(signal_timing=self.signal_timing)
        self.vehicle_counter = 0
        
        # Generate vehicle arrivals
        self._generate_arrivals(traffic_volumes, simulation_duration)
        
        # Sort events by time
        self.events.sort(key=lambda x: x[0])
        
        # Process events
        for event_time, event_type, event_data in self.events:
            self.state.current_time = event_time
            
            if event_type == 'arrival':
                self._handle_arrival(event_data)
            elif event_type == 'signal_change':
                self._handle_signal_change()
        
        # Calculate metrics
        results = self._calculate_metrics()
        
        logger.info(f"Simulation complete. Processed {len(self.state.vehicles_processed)} vehicles")
        return results
    
    def _generate_arrivals(
        self,
        traffic_volumes: Dict[str, float],
        duration: float
    ):
        """
        Generate vehicle arrival events.
        
        Args:
            traffic_volumes: Hourly volumes by direction
            duration: Simulation duration
        """
        self.events = []
        
        for direction, hourly_volume in traffic_volumes.items():
            if hourly_volume <= 0:
                continue
            
            # Convert to arrival rate (vehicles per second)
            arrival_rate = hourly_volume / 3600.0
            
            # Generate Poisson arrivals - originally tried uniform but Poisson is more realistic
            current_time = 0.0
            while current_time < duration:
                # Inter-arrival time follows exponential distribution
                inter_arrival = np.random.exponential(1.0 / arrival_rate)
                current_time += inter_arrival
                
                if current_time < duration:
                    vehicle = Vehicle(
                        id=self.vehicle_counter,
                        arrival_time=current_time,
                        direction=direction
                    )
                    self.vehicle_counter += 1
                    self.events.append((current_time, 'arrival', vehicle))
        
        # Generate signal change events
        cycle_length = self.signal_timing['cycle_length']
        ns_green = self.signal_timing['green_time_north']
        ew_green = self.signal_timing['green_time_east']
        
        current_time = 0.0
        while current_time < duration:
            # NS green
            self.events.append((current_time, 'signal_change', 'NS'))
            current_time += ns_green
            
            # EW green
            self.events.append((current_time, 'signal_change', 'EW'))
            current_time += ew_green
        
        logger.info(f"Generated {len([e for e in self.events if e[1] == 'arrival'])} vehicle arrivals")
    
    def _handle_arrival(self, vehicle: Vehicle):
        """Handle vehicle arrival event."""
        direction = vehicle.direction
        
        # Add vehicle to queue
        if direction in self.state.queues:
            self.state.queues[direction].append(vehicle)
        
        # Try to serve vehicles if green
        self._serve_vehicles()
    
    def _handle_signal_change(self):
        """Handle signal phase change event."""
        # Toggle phase
        if self.state.current_phase == 'NS':
            self.state.current_phase = 'EW'
        else:
            self.state.current_phase = 'NS'
        
        self.state.phase_start_time = self.state.current_time
        
        # Serve vehicles in new green phase
        self._serve_vehicles()
    
    def _serve_vehicles(self):
        """Serve vehicles in current green phase."""
        if self.state.current_phase == 'NS':
            active_directions = ['N', 'S']
        else:
            active_directions = ['E', 'W']
        
        # Time elapsed in current phase
        time_in_phase = self.state.current_time - self.state.phase_start_time
        
        # Remaining green time
        if self.state.current_phase == 'NS':
            green_time = self.signal_timing['green_time_north']
        else:
            green_time = self.signal_timing['green_time_east']
        
        remaining_green = max(0, green_time - time_in_phase)
        
        if remaining_green <= 0:
            return
        
        # Serve vehicles from active directions
        for direction in active_directions:
            queue = self.state.queues[direction]
            
            # Calculate how many vehicles can be served
            service_capacity = int(self.service_rate * remaining_green)
            
            # Serve vehicles
            vehicles_to_serve = min(len(queue), service_capacity)
            
            for _ in range(vehicles_to_serve):
                if queue:
                    vehicle = queue.pop(0)
                    vehicle.departure_time = self.state.current_time
                    vehicle.delay = vehicle.departure_time - vehicle.arrival_time
                    self.state.vehicles_processed.append(vehicle)
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from simulation results."""
        processed = self.state.vehicles_processed
        
        if not processed:
            return {
                'throughput': 0,
                'avg_delay': 0,
                'max_delay': 0,
                'avg_stops': 0,
                'max_queue_length': 0,
                'level_of_service': 'F'
            }
        
        # Throughput (vehicles per hour)
        simulation_hours = self.state.current_time / 3600.0
        throughput = len(processed) / simulation_hours if simulation_hours > 0 else 0
        
        # Delays
        delays = [v.delay for v in processed]
        avg_delay = np.mean(delays)
        max_delay = np.max(delays)
        
        # Stops
        stops = [v.stops for v in processed]
        avg_stops = np.mean(stops)
        
        # Queue lengths
        max_queue_length = max(
            max(len(q) for q in self.state.queues.values()),
            1
        )
        
        # Level of Service
        los = level_of_service(avg_delay)
        
        # Direction-specific metrics
        direction_metrics = {}
        for direction in ['N', 'S', 'E', 'W']:
            dir_vehicles = [v for v in processed if v.direction == direction]
            if dir_vehicles:
                direction_metrics[direction] = {
                    'throughput': len(dir_vehicles) / simulation_hours,
                    'avg_delay': np.mean([v.delay for v in dir_vehicles])
                }
        
        results = {
            'throughput': throughput,
            'avg_delay': avg_delay,
            'max_delay': max_delay,
            'avg_stops': avg_stops,
            'max_queue_length': max_queue_length,
            'level_of_service': los,
            'total_vehicles_processed': len(processed),
            'direction_metrics': direction_metrics
        }
        
        return results
    
    def get_queue_lengths_over_time(self) -> Dict[str, List[Tuple[float, int]]]:
        """
        Get queue length evolution over time.
        
        Returns:
            Dictionary mapping directions to list of (time, queue_length) tuples
        """
        # This would require tracking queue lengths throughout simulation
        # For now, return final queue lengths
        final_queues = {}
        for direction, queue in self.state.queues.items():
            final_queues[direction] = [(self.state.current_time, len(queue))]
        
        return final_queues

