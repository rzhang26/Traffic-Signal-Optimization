"""
Unit tests for optimization module.
"""

import unittest
from optimization.genetic_algorithm import GeneticAlgorithm, Individual
from optimization.fitness_functions import (
    calculate_throughput,
    calculate_delay,
    composite_fitness,
    penalty_for_constraints,
    compare_scenarios
)


class TestFitnessFunctions(unittest.TestCase):
    """Test fitness function calculations."""
    
    def setUp(self):
        """Setup test data."""
        self.simulation_results = {
            'throughput': 1500,
            'avg_delay': 25.0,
            'avg_stops': 1.2,
            'max_queue_length': 8.5
        }
    
    def test_calculate_throughput(self):
        """Test throughput fitness calculation."""
        throughput = calculate_throughput(self.simulation_results)
        self.assertEqual(throughput, 1500)
    
    def test_calculate_delay(self):
        """Test delay fitness calculation."""
        delay = calculate_delay(self.simulation_results)
        self.assertEqual(delay, -25.0)  # Negative because we minimize
    
    def test_composite_fitness(self):
        """Test composite fitness calculation."""
        fitness = composite_fitness(self.simulation_results)
        self.assertIsInstance(fitness, float)
    
    def test_penalty_for_constraints(self):
        """Test constraint penalty calculation."""
        valid_timing = {
            'cycle_length': 90,
            'green_time_north': 35,
            'green_time_south': 35,
            'green_time_east': 30,
            'green_time_west': 30,
            'yellow_time': 3.0,
            'all_red_time': 2.0
        }
        
        penalty = penalty_for_constraints(valid_timing)
        self.assertGreaterEqual(penalty, 0)  # Valid timing should have no penalty
        
        # Invalid timing (green time too short)
        invalid_timing = valid_timing.copy()
        invalid_timing['green_time_north'] = 5
        
        penalty_invalid = penalty_for_constraints(invalid_timing)
        self.assertLess(penalty_invalid, 0)
    
    def test_compare_scenarios(self):
        """Test scenario comparison."""
        baseline = {
            'throughput': 1400,
            'avg_delay': 30.0,
            'avg_stops': 1.5,
            'max_queue_length': 10.0
        }
        
        optimized = {
            'throughput': 1500,
            'avg_delay': 25.0,
            'avg_stops': 1.2,
            'max_queue_length': 8.5
        }
        
        comparison = compare_scenarios(baseline, optimized)
        
        self.assertIn('throughput', comparison)
        self.assertGreater(comparison['throughput']['improvement_percent'], 0)


class TestIndividual(unittest.TestCase):
    """Test Individual class."""
    
    def test_individual_creation(self):
        """Test creating an individual."""
        timing = {
            'cycle_length': 90,
            'green_time_north': 35
        }
        
        individual = Individual(timing)
        self.assertEqual(individual.signal_timing, timing)
        self.assertEqual(individual.fitness, 0.0)


class TestGeneticAlgorithm(unittest.TestCase):
    """Test genetic algorithm functionality."""
    
    def setUp(self):
        """Setup test data."""
        self.initial_timing = {
            'cycle_length': 90,
            'green_time_north': 35,
            'green_time_south': 35,
            'green_time_east': 30,
            'green_time_west': 30,
            'yellow_time': 3.0,
            'all_red_time': 2.0
        }
    
    def test_ga_initialization(self):
        """Test GA initialization."""
        ga = GeneticAlgorithm(population_size=20, generations=10)
        self.assertEqual(ga.population_size, 20)
        self.assertEqual(ga.generations, 10)
    
    def test_initialize_population(self):
        """Test population initialization."""
        ga = GeneticAlgorithm(population_size=10)
        constraints = ga._get_default_constraints()
        population = ga._initialize_population(self.initial_timing, constraints)
        
        self.assertEqual(len(population), 10)
        self.assertIsInstance(population[0], Individual)
    
    def test_crossover(self):
        """Test crossover operation."""
        ga = GeneticAlgorithm()
        
        parent1 = Individual(self.initial_timing)
        parent2 = Individual({
            'cycle_length': 100,
            'green_time_north': 40,
            'green_time_south': 40,
            'green_time_east': 35,
            'green_time_west': 35,
            'yellow_time': 3.0,
            'all_red_time': 2.0
        })
        
        child1, child2 = ga._crossover(parent1, parent2)
        
        self.assertIsInstance(child1, Individual)
        self.assertIsInstance(child2, Individual)
    
    def test_mutate(self):
        """Test mutation operation."""
        ga = GeneticAlgorithm()
        individual = Individual(self.initial_timing)
        constraints = ga._get_default_constraints()
        
        original_cycle = individual.signal_timing['cycle_length']
        mutated = ga._mutate(individual, constraints)
        
        self.assertIsInstance(mutated, Individual)
        # Mutation may or may not change the value, so we just check it's valid
        self.assertGreaterEqual(mutated.signal_timing['cycle_length'], 45)
        self.assertLessEqual(mutated.signal_timing['cycle_length'], 120)
    
    def test_optimize_simple(self):
        """Test optimization with simple fitness function."""
        ga = GeneticAlgorithm(population_size=10, generations=5)
        
        # Simple fitness function that prefers shorter cycles
        def simple_fitness(timing):
            fitness = 1.0 / timing['cycle_length']
            sim_results = {'throughput': 1500, 'avg_delay': 20}
            return fitness, sim_results
        
        best_timing, results = ga.optimize(self.initial_timing, simple_fitness)
        
        self.assertIn('cycle_length', best_timing)
        self.assertIn('best_fitness', results)
        self.assertEqual(len(results['fitness_history']), 5)


if __name__ == '__main__':
    unittest.main()

