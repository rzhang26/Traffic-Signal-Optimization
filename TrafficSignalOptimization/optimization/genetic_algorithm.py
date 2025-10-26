"""
Genetic Algorithm Module
Implements genetic algorithm for signal timing optimization.
"""

import logging
from typing import Dict, List, Any, Tuple, Callable
import numpy as np
import random
from copy import deepcopy

logger = logging.getLogger(__name__)


class Individual:
    """Represents an individual solution (signal timing configuration)."""
    
    def __init__(self, signal_timing: Dict[str, Any]):
        """
        Initialize individual with signal timing.
        
        Args:
            signal_timing: Dictionary with signal timing parameters
        """
        self.signal_timing = signal_timing
        self.fitness = 0.0
        self.simulation_results = None
    
    def __repr__(self):
        return f"Individual(fitness={self.fitness:.4f}, cycle={self.signal_timing.get('cycle_length')})"


class GeneticAlgorithm:
    """
    Genetic Algorithm for optimizing signal timings.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism_count: int = 2,
        random_seed: int = 42
    ):
        """
        Initialize genetic algorithm.
        
        Args:
            population_size: Number of individuals in population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elitism_count: Number of best individuals to preserve
            random_seed: Random seed for reproducibility
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        self.population = []
        self.best_individual = None
        self.fitness_history = []
    
    def optimize(
        self,
        initial_timing: Dict[str, Any],
        fitness_function: Callable[[Dict[str, Any]], Tuple[float, Dict[str, Any]]],
        constraints: Dict[str, Tuple[float, float]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Run genetic algorithm optimization.
        
        Args:
            initial_timing: Initial signal timing configuration
            fitness_function: Function that evaluates fitness given signal timing
            constraints: Dictionary of parameter constraints (min, max)
            
        Returns:
            Tuple of (best_signal_timing, optimization_results)
        """
        logger.info(f"Starting GA optimization: {self.population_size} individuals, {self.generations} generations")
        
        # Set default constraints
        if constraints is None:
            constraints = self._get_default_constraints()
        
        # Initialize population
        self.population = self._initialize_population(initial_timing, constraints)
        
        # Evaluate initial population
        self._evaluate_population(fitness_function)
        
        # Evolution loop
        for generation in range(self.generations):
            # Selection
            parents = self._selection()
            
            # Crossover and mutation
            offspring = []
            for i in range(0, len(parents) - 1, 2):
                parent1, parent2 = parents[i], parents[i + 1]
                
                # originally tried single-point crossover but uniform works better for signal timings
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = deepcopy(parent1), deepcopy(parent2)
                
                # mutate after crossover - tried other way around but this converges faster
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1, constraints)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2, constraints)
                
                offspring.extend([child1, child2])
            
            # Elitism: preserve best individuals
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            elite = self.population[:self.elitism_count]
            
            # Form new population
            self.population = elite + offspring[:self.population_size - self.elitism_count]
            
            # Evaluate new population
            self._evaluate_population(fitness_function)
            
            # Track best individual
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            self.best_individual = self.population[0]
            self.fitness_history.append(self.best_individual.fitness)
            
            if (generation + 1) % 10 == 0:
                logger.info(f"Generation {generation + 1}/{self.generations}: Best fitness = {self.best_individual.fitness:.4f}")
        
        # Prepare results
        optimization_results = {
            'best_fitness': self.best_individual.fitness,
            'fitness_history': self.fitness_history,
            'generations': self.generations,
            'final_population_size': len(self.population),
            'simulation_results': self.best_individual.simulation_results
        }
        
        logger.info(f"Optimization complete. Best fitness: {self.best_individual.fitness:.4f}")
        
        return self.best_individual.signal_timing, optimization_results
    
    def _initialize_population(
        self,
        initial_timing: Dict[str, Any],
        constraints: Dict[str, Tuple[float, float]]
    ) -> List[Individual]:
        """
        Initialize population with random signal timings.
        
        Args:
            initial_timing: Base timing configuration
            constraints: Parameter constraints
            
        Returns:
            List of individuals
        """
        population = []
        
        # Add initial timing as first individual
        population.append(Individual(deepcopy(initial_timing)))
        
        # Generate random individuals
        for _ in range(self.population_size - 1):
            timing = deepcopy(initial_timing)
            
            # Randomize cycle length
            min_cycle, max_cycle = constraints.get('cycle_length', (45, 120))
            timing['cycle_length'] = random.randint(min_cycle, max_cycle)
            
            # Randomize green times
            for direction in ['north', 'south', 'east', 'west']:
                key = f'green_time_{direction}'
                min_green, max_green = constraints.get(key, (10, 60))
                timing[key] = random.uniform(min_green, max_green)
            
            # Normalize green times to fit within cycle
            self._normalize_green_times(timing)
            
            population.append(Individual(timing))
        
        return population
    
    def _normalize_green_times(self, timing: Dict[str, Any]):
        """
        Normalize green times to fit within cycle length.
        
        Args:
            timing: Signal timing dictionary (modified in place)
        """
        cycle_length = timing['cycle_length']
        yellow_time = timing.get('yellow_time', 3.0)
        all_red_time = timing.get('all_red_time', 2.0)
        
        # Lost time per phase
        lost_time = (yellow_time + all_red_time) * 2
        available_green = cycle_length - lost_time
        
        # Get current green times (assuming 2-phase: NS and EW)
        ns_green = (timing.get('green_time_north', 0) + timing.get('green_time_south', 0)) / 2
        ew_green = (timing.get('green_time_east', 0) + timing.get('green_time_west', 0)) / 2
        
        total_green = ns_green + ew_green
        
        if total_green > available_green:
            # Scale down
            scale_factor = available_green / total_green
            ns_green *= scale_factor
            ew_green *= scale_factor
        
        # Update timing
        timing['green_time_north'] = ns_green
        timing['green_time_south'] = ns_green
        timing['green_time_east'] = ew_green
        timing['green_time_west'] = ew_green
    
    def _evaluate_population(self, fitness_function: Callable):
        """
        Evaluate fitness for all individuals in population.
        
        Args:
            fitness_function: Function to evaluate fitness
        """
        for individual in self.population:
            fitness, sim_results = fitness_function(individual.signal_timing)
            individual.fitness = fitness
            individual.simulation_results = sim_results
    
    def _selection(self) -> List[Individual]:
        """
        Select parents using tournament selection.
        
        Returns:
            List of selected parents
        """
        parents = []
        tournament_size = 3  # tried 5 but 3 gives better diversity
        
        for _ in range(self.population_size):
            # Tournament selection - tested roulette wheel but this was more stable
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            parents.append(deepcopy(winner))
        
        return parents
    
    def _crossover(
        self,
        parent1: Individual,
        parent2: Individual
    ) -> Tuple[Individual, Individual]:
        """
        Perform crossover between two parents.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Tuple of two offspring
        """
        child1_timing = deepcopy(parent1.signal_timing)
        child2_timing = deepcopy(parent2.signal_timing)
        
        # Uniform crossover for each parameter
        parameters = ['cycle_length', 'green_time_north', 'green_time_south', 
                     'green_time_east', 'green_time_west']
        
        for param in parameters:
            if random.random() < 0.5:
                child1_timing[param] = parent2.signal_timing[param]
                child2_timing[param] = parent1.signal_timing[param]
        
        # Normalize green times
        self._normalize_green_times(child1_timing)
        self._normalize_green_times(child2_timing)
        
        return Individual(child1_timing), Individual(child2_timing)
    
    def _mutate(
        self,
        individual: Individual,
        constraints: Dict[str, Tuple[float, float]]
    ) -> Individual:
        """
        Mutate an individual.
        
        Args:
            individual: Individual to mutate
            constraints: Parameter constraints
            
        Returns:
            Mutated individual
        """
        timing = individual.signal_timing
        
        # Select random parameter to mutate
        parameters = ['cycle_length', 'green_time_north', 'green_time_south',
                     'green_time_east', 'green_time_west']
        param = random.choice(parameters)
        
        # Get constraints
        min_val, max_val = constraints.get(param, (10, 60))
        
        # Gaussian mutation
        current_val = timing[param]
        mutation = np.random.normal(0, (max_val - min_val) * 0.1)
        new_val = np.clip(current_val + mutation, min_val, max_val)
        
        timing[param] = int(new_val) if param == 'cycle_length' else new_val
        
        # Normalize green times
        self._normalize_green_times(timing)
        
        return Individual(timing)
    
    def _get_default_constraints(self) -> Dict[str, Tuple[float, float]]:
        """Get default parameter constraints."""
        return {
            'cycle_length': (45, 120),
            'green_time_north': (10, 60),
            'green_time_south': (10, 60),
            'green_time_east': (10, 60),
            'green_time_west': (10, 60)
        }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        Get summary of optimization process.
        
        Returns:
            Dictionary with optimization summary
        """
        if not self.best_individual:
            return {}
        
        return {
            'best_signal_timing': self.best_individual.signal_timing,
            'best_fitness': self.best_individual.fitness,
            'generations_run': len(self.fitness_history),
            'fitness_improvement': self.fitness_history[-1] - self.fitness_history[0] if self.fitness_history else 0,
            'convergence_generation': self._find_convergence_generation()
        }
    
    def _find_convergence_generation(self) -> int:
        """Find generation where algorithm converged."""
        if len(self.fitness_history) < 10:
            return len(self.fitness_history)
        
        # Find when fitness stopped improving significantly
        threshold = 0.001
        for i in range(10, len(self.fitness_history)):
            recent_improvement = abs(self.fitness_history[i] - self.fitness_history[i-10])
            if recent_improvement < threshold:
                return i
        
        return len(self.fitness_history)

