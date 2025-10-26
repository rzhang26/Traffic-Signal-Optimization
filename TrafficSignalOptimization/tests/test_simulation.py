"""
Unit tests for simulation module.
"""

import unittest
from simulation.traffic_simulator import TrafficSimulator
from simulation.queue_model import QueueModel, calculate_capacity, level_of_service


class TestQueueModel(unittest.TestCase):
    """Test queue model functionality."""
    
    def test_queue_model_initialization(self):
        """Test queue model initialization."""
        qm = QueueModel(service_rate=0.5)
        self.assertEqual(qm.service_rate, 0.5)
    
    def test_calculate_queue_length(self):
        """Test queue length calculation."""
        qm = QueueModel(service_rate=0.5)
        avg_queue, max_queue = qm.calculate_queue_length(
            arrival_rate=0.3,
            service_time=30,
            time_period=60
        )
        
        self.assertGreaterEqual(avg_queue, 0)
        self.assertGreaterEqual(max_queue, avg_queue)
    
    def test_calculate_delay(self):
        """Test delay calculation."""
        qm = QueueModel(service_rate=0.5)
        delay_metrics = qm.calculate_delay(
            arrival_rate=0.3,
            green_time=30,
            red_time=30
        )
        
        self.assertIn('uniform_delay', delay_metrics)
        self.assertIn('random_delay', delay_metrics)
        self.assertIn('total_delay', delay_metrics)
        self.assertGreater(delay_metrics['total_delay'], 0)
    
    def test_calculate_stops(self):
        """Test stop calculation."""
        qm = QueueModel(service_rate=0.5)
        prob_stop = qm.calculate_stops(
            arrival_rate=0.3,
            green_time=30,
            cycle_length=60
        )
        
        self.assertGreaterEqual(prob_stop, 0)
        self.assertLessEqual(prob_stop, 1)
    
    def test_simulate_queue_evolution(self):
        """Test queue evolution simulation."""
        qm = QueueModel(service_rate=0.5)
        evolution = qm.simulate_queue_evolution(
            arrival_rate=0.3,
            green_time=30,
            red_time=30,
            num_cycles=10
        )
        
        self.assertEqual(len(evolution), 10)
        self.assertIn('arrivals', evolution[0])
        self.assertIn('served', evolution[0])


class TestCapacityCalculation(unittest.TestCase):
    """Test capacity calculation functions."""
    
    def test_calculate_capacity(self):
        """Test capacity calculation."""
        capacity = calculate_capacity(
            saturation_flow=1800,
            green_time=30,
            cycle_length=60,
            lost_time=5
        )
        
        self.assertGreater(capacity, 0)
        self.assertLess(capacity, 1800)
    
    def test_level_of_service(self):
        """Test level of service determination."""
        self.assertEqual(level_of_service(5), 'A')
        self.assertEqual(level_of_service(15), 'B')
        self.assertEqual(level_of_service(30), 'C')
        self.assertEqual(level_of_service(50), 'D')
        self.assertEqual(level_of_service(70), 'E')
        self.assertEqual(level_of_service(100), 'F')


class TestTrafficSimulator(unittest.TestCase):
    """Test traffic simulator functionality."""
    
    def setUp(self):
        """Setup test signal timing."""
        self.signal_timing = {
            'cycle_length': 90,
            'green_time_north': 35,
            'green_time_south': 35,
            'green_time_east': 30,
            'green_time_west': 30,
            'yellow_time': 3.0,
            'all_red_time': 2.0
        }
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        sim = TrafficSimulator(self.signal_timing)
        self.assertIsNotNone(sim)
        self.assertEqual(sim.signal_timing, self.signal_timing)
    
    def test_run_simulation(self):
        """Test running simulation."""
        sim = TrafficSimulator(self.signal_timing)
        
        traffic_volumes = {
            'N': 600,
            'S': 600,
            'E': 400,
            'W': 400
        }
        
        results = sim.run_simulation(traffic_volumes, simulation_duration=1800)
        
        self.assertIn('throughput', results)
        self.assertIn('avg_delay', results)
        self.assertIn('level_of_service', results)
        self.assertGreater(results['throughput'], 0)
    
    def test_simulation_with_different_volumes(self):
        """Test simulation with varying traffic volumes."""
        sim = TrafficSimulator(self.signal_timing)
        
        # Low volume
        low_volumes = {'N': 200, 'S': 200, 'E': 200, 'W': 200}
        low_results = sim.run_simulation(low_volumes, 1800)
        
        # High volume
        high_volumes = {'N': 800, 'S': 800, 'E': 800, 'W': 800}
        high_results = sim.run_simulation(high_volumes, 1800)
        
        # High volume should result in higher delay
        self.assertGreater(high_results['avg_delay'], low_results['avg_delay'])


if __name__ == '__main__':
    unittest.main()

