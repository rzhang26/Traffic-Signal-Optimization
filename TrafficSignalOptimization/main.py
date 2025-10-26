"""
Traffic Signal Optimization System - Main Entry Point
Provides both CLI and GUI interfaces for the application.
"""

import sys
import os
import argparse
import logging
import json
from typing import Dict, Any, Optional
import tkinter as tk
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion.database import DatabaseManager
from data_ingestion.fetch_data import fetch_data_by_county
from data_processing.validate_data import validate_traffic_data, clean_data, get_peak_hours
from data_processing.interpolate import interpolate_missing_data
from data_processing.infer_signal_timings import infer_signal_timings
from simulation.traffic_simulator import TrafficSimulator
from optimization.genetic_algorithm import GeneticAlgorithm
from optimization.fitness_functions import composite_fitness, evaluate_fitness_with_constraints
from ui.main_window import MainWindow


# Configure logging
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


class TrafficOptimizationApp:
    """Main application class for traffic signal optimization."""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        Initialize application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db = DatabaseManager(self.config['database']['path'])
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.traffic_data = []
        self.baseline_timing = None
        self.optimized_timing = None
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'database': {'path': 'traffic_data.db'},
            'simulation': {
                'default_simulation_duration_seconds': 3600,
                'saturation_flow_rate_vphpl': 1800
            },
            'optimization': {
                'genetic_algorithm': {
                    'population_size': 50,
                    'generations': 100,
                    'mutation_rate': 0.1,
                    'crossover_rate': 0.8,
                    'elitism_count': 2
                }
            }
        }
    
    def fetch_data(self, county: str, max_records: int = 5000) -> bool:
        """
        Fetch traffic data for a county.
        
        Args:
            county: County name
            max_records: Maximum records to fetch
            
        Returns:
            Success status
        """
        try:
            self.logger.info(f"Fetching data for {county}...")
            
            # For demo purposes, generate synthetic data if API fetch fails
            raw_data = fetch_data_by_county(county)
            
            if not raw_data:
                self.logger.warning("No data from API, generating synthetic data for demo")
                raw_data = self._generate_demo_data(county)
            
            # Validate and clean data
            valid_data, errors = validate_traffic_data(raw_data)
            cleaned_data = clean_data(valid_data)
            
            # Interpolate missing values
            self.traffic_data = interpolate_missing_data(cleaned_data)
            
            # Store in database
            self.db.insert_traffic_data(self.traffic_data)
            
            self.logger.info(f"Successfully processed {len(self.traffic_data)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return False
    
    def _generate_demo_data(self, county: str, num_records: int = 1000) -> list:
        """Generate synthetic demo data."""
        import random
        from datetime import datetime, timedelta
        
        data = []
        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        directions = ['N', 'S', 'E', 'W']
        stations = [f"{county}_ST_{i:03d}" for i in range(1, 6)]
        
        for i in range(num_records):
            timestamp = base_time + timedelta(minutes=i * 15)
            
            # Simulate peak hours
            hour = timestamp.hour
            if 7 <= hour <= 9 or 16 <= hour <= 18:
                base_volume = random.randint(400, 800)
            else:
                base_volume = random.randint(100, 400)
            
            record = {
                'county': county,
                'station_id': random.choice(stations),
                'direction': random.choice(directions),
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'volume': base_volume + random.randint(-50, 50),
                'speed': random.uniform(25, 45),
                'occupancy': random.uniform(10, 60),
                'data_type': 'synthetic'
            }
            data.append(record)
        
        return data
    
    def run_optimization(self, optimization_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run traffic signal optimization.
        
        Args:
            optimization_params: Optimization parameters
            
        Returns:
            Dictionary with optimization results
        """
        try:
            if not self.traffic_data:
                raise ValueError("No traffic data available. Fetch data first.")
            
            self.logger.info("Starting optimization process...")
            
            # Get optimization parameters
            if optimization_params is None:
                optimization_params = self.config['optimization']['genetic_algorithm']
            
            # Infer baseline signal timing
            self.baseline_timing = infer_signal_timings(self.traffic_data)
            self.logger.info(f"Baseline timing: {self.baseline_timing}")
            
            # Calculate traffic volumes by direction
            volumes = self.baseline_timing.get('volumes', {})
            traffic_volumes = {
                'N': volumes.get('N', 500),
                'S': volumes.get('S', 500),
                'E': volumes.get('E', 400),
                'W': volumes.get('W', 400)
            }
            
            # Simulate baseline
            baseline_sim = TrafficSimulator(
                self.baseline_timing,
                self.config['simulation']['saturation_flow_rate_vphpl']
            )
            baseline_results = baseline_sim.run_simulation(
                traffic_volumes,
                self.config['simulation']['default_simulation_duration_seconds']
            )
            
            self.logger.info(f"Baseline results: {baseline_results}")
            
            # Define fitness function
            def fitness_func(signal_timing: Dict[str, Any]):
                sim = TrafficSimulator(signal_timing)
                results = sim.run_simulation(traffic_volumes, 3600)
                fitness = evaluate_fitness_with_constraints(results, signal_timing)
                return fitness, results
            
            # Run genetic algorithm
            ga = GeneticAlgorithm(
                population_size=optimization_params.get('population_size', 50),
                generations=optimization_params.get('generations', 100),
                mutation_rate=optimization_params.get('mutation_rate', 0.1)
            )
            
            self.optimized_timing, optimization_results = ga.optimize(
                self.baseline_timing,
                fitness_func
            )
            
            self.logger.info(f"Optimized timing: {self.optimized_timing}")
            
            # Simulate optimized
            optimized_sim = TrafficSimulator(self.optimized_timing)
            optimized_results = optimized_sim.run_simulation(traffic_volumes, 3600)
            
            # Store results in database
            self._store_optimization_results(optimization_results)
            
            return {
                'baseline_timing': self.baseline_timing,
                'optimized_timing': self.optimized_timing,
                'baseline_results': baseline_results,
                'optimized_results': optimized_results,
                'optimization_results': optimization_results
            }
            
        except Exception as e:
            self.logger.error(f"Error during optimization: {e}")
            raise
    
    def _store_optimization_results(self, results: Dict[str, Any]):
        """Store optimization results in database."""
        try:
            # Create intersection record
            intersection_data = {
                'intersection_id': 'DEMO_001',
                'county': self.traffic_data[0].get('county', 'Unknown') if self.traffic_data else 'Unknown',
                'name': 'Demo Intersection',
                'num_approaches': 4
            }
            self.db.insert_intersection(intersection_data)
            
            # Store signal timing
            timing_data = self.optimized_timing.copy()
            timing_data['intersection_id'] = 'DEMO_001'
            timing_data['is_optimized'] = 1
            timing_id = self.db.insert_signal_timing(timing_data)
            
            # Store optimization results
            sim_results = results.get('simulation_results', {})
            result_data = {
                'intersection_id': 'DEMO_001',
                'signal_timing_id': timing_id,
                'throughput': sim_results.get('throughput', 0),
                'avg_delay': sim_results.get('avg_delay', 0),
                'avg_stops': sim_results.get('avg_stops', 0),
                'max_queue_length': sim_results.get('max_queue_length', 0),
                'fitness_score': results.get('best_fitness', 0)
            }
            self.db.insert_optimization_result(result_data)
            
            self.logger.info("Optimization results stored in database")
            
        except Exception as e:
            self.logger.warning(f"Could not store results in database: {e}")
    
    def run_gui(self):
        """Launch GUI application."""
        root = tk.Tk()
        main_window = MainWindow(root)
        
        # Connect callbacks
        main_window.on_fetch_data = lambda county, day: self.fetch_data(county)
        main_window.on_run_optimization = lambda params: self.run_optimization(params)
        
        root.mainloop()
    
    def run_cli(self, args):
        """Run CLI mode."""
        if args.fetch_data:
            success = self.fetch_data(args.county, args.max_records)
            if success:
                print(f"✓ Successfully fetched data for {args.county}")
            else:
                print(f"✗ Failed to fetch data for {args.county}")
                return
        
        if args.optimize:
            print(f"Running optimization for {args.county}...")
            
            params = {
                'population_size': args.population_size,
                'generations': args.generations,
                'mutation_rate': args.mutation_rate
            }
            
            results = self.run_optimization(params)
            
            # Print results
            print("\n" + "=" * 60)
            print("OPTIMIZATION RESULTS")
            print("=" * 60)
            print(f"\nBaseline Cycle Length: {results['baseline_timing']['cycle_length']}s")
            print(f"Optimized Cycle Length: {results['optimized_timing']['cycle_length']}s")
            print(f"\nBaseline Throughput: {results['baseline_results']['throughput']:.1f} veh/hr")
            print(f"Optimized Throughput: {results['optimized_results']['throughput']:.1f} veh/hr")
            print(f"\nBaseline Delay: {results['baseline_results']['avg_delay']:.2f}s")
            print(f"Optimized Delay: {results['optimized_results']['avg_delay']:.2f}s")
            print(f"\nLevel of Service: {results['optimized_results']['level_of_service']}")
            print("=" * 60 + "\n")
            
            if args.export:
                self._export_results(results, args.export)
    
    def _export_results(self, results: Dict[str, Any], filename: str):
        """Export results to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✓ Results exported to {filename}")
        except Exception as e:
            print(f"✗ Failed to export results: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Traffic Signal Optimization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI
  python main.py --gui
  
  # Fetch data and optimize via CLI
  python main.py --county Albany --fetch-data --optimize
  
  # Optimize with custom parameters
  python main.py --county Monroe --optimize --generations 200 --population-size 100
  
  # Export results
  python main.py --county Erie --optimize --export results.json
        """
    )
    
    parser.add_argument('--gui', action='store_true',
                       help='Launch graphical user interface')
    parser.add_argument('--county', type=str, default='Albany',
                       help='County name for analysis (default: Albany)')
    parser.add_argument('--fetch-data', action='store_true',
                       help='Fetch traffic data from NYS OData endpoint')
    parser.add_argument('--optimize', action='store_true',
                       help='Run signal timing optimization')
    parser.add_argument('--max-records', type=int, default=5000,
                       help='Maximum records to fetch (default: 5000)')
    parser.add_argument('--population-size', type=int, default=50,
                       help='GA population size (default: 50)')
    parser.add_argument('--generations', type=int, default=100,
                       help='GA generations (default: 100)')
    parser.add_argument('--mutation-rate', type=float, default=0.1,
                       help='GA mutation rate (default: 0.1)')
    parser.add_argument('--export', type=str, metavar='FILE',
                       help='Export results to JSON file')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str,
                       help='Log file path')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Create application
    app = TrafficOptimizationApp()
    
    # Run in appropriate mode
    if args.gui or (not args.fetch_data and not args.optimize):
        # Default to GUI if no CLI options specified
        app.run_gui()
    else:
        app.run_cli(args)


if __name__ == "__main__":
    main()

