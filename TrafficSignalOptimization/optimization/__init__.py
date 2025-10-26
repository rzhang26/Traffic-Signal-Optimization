"""
Optimization Module
Implements genetic algorithm for optimizing signal timings.
"""

from .genetic_algorithm import GeneticAlgorithm
from .fitness_functions import (
    calculate_throughput,
    calculate_delay,
    calculate_stops,
    composite_fitness
)

__all__ = [
    'GeneticAlgorithm',
    'calculate_throughput',
    'calculate_delay',
    'calculate_stops',
    'composite_fitness'
]

