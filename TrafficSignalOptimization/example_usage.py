"""
Example Usage Script
Demonstrates how to use the Traffic Signal Optimization System programmatically.
"""

import sys
import logging
from main import TrafficOptimizationApp

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def example_1_basic_optimization():
    """Example 1: Basic optimization workflow."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Optimization")
    print("="*60 + "\n")
    
    # Create application instance
    app = TrafficOptimizationApp()
    
    # Fetch data for a county
    print("Step 1: Fetching traffic data...")
    success = app.fetch_data('Albany', max_records=1000)
    
    if not success:
        print("❌ Failed to fetch data")
        return
    
    print("✓ Data fetched successfully\n")
    
    # Run optimization with default parameters
    print("Step 2: Running optimization...")
    results = app.run_optimization()
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    baseline = results['baseline_results']
    optimized = results['optimized_results']
    
    print(f"\n📊 BASELINE PERFORMANCE:")
    print(f"   Cycle Length: {results['baseline_timing']['cycle_length']}s")
    print(f"   Throughput: {baseline['throughput']:.1f} veh/hr")
    print(f"   Avg Delay: {baseline['avg_delay']:.2f}s")
    print(f"   Level of Service: {baseline['level_of_service']}")
    
    print(f"\n📈 OPTIMIZED PERFORMANCE:")
    print(f"   Cycle Length: {results['optimized_timing']['cycle_length']}s")
    print(f"   Throughput: {optimized['throughput']:.1f} veh/hr")
    print(f"   Avg Delay: {optimized['avg_delay']:.2f}s")
    print(f"   Level of Service: {optimized['level_of_service']}")
    
    # Calculate improvements
    throughput_improvement = ((optimized['throughput'] - baseline['throughput']) / 
                             baseline['throughput'] * 100)
    delay_reduction = ((baseline['avg_delay'] - optimized['avg_delay']) / 
                      baseline['avg_delay'] * 100)
    
    print(f"\n💡 IMPROVEMENTS:")
    print(f"   Throughput: {throughput_improvement:+.1f}%")
    print(f"   Delay Reduction: {delay_reduction:+.1f}%")
    print(f"   Stops Reduction: {((baseline['avg_stops'] - optimized['avg_stops']) / baseline['avg_stops'] * 100):+.1f}%")
    
    print("\n" + "="*60 + "\n")


def example_2_custom_parameters():
    """Example 2: Optimization with custom parameters."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Optimization Parameters")
    print("="*60 + "\n")
    
    app = TrafficOptimizationApp()
    
    # Fetch data
    print("Fetching data...")
    app.fetch_data('Monroe', max_records=500)
    
    # Custom optimization parameters
    custom_params = {
        'population_size': 30,      # Smaller population for faster run
        'generations': 50,           # Fewer generations
        'mutation_rate': 0.15,       # Higher mutation rate
        'crossover_rate': 0.9,
        'elitism_count': 3
    }
    
    print("\nRunning optimization with custom parameters:")
    print(f"  Population Size: {custom_params['population_size']}")
    print(f"  Generations: {custom_params['generations']}")
    print(f"  Mutation Rate: {custom_params['mutation_rate']}")
    
    results = app.run_optimization(custom_params)
    
    print(f"\n✓ Optimization complete!")
    print(f"  Best Fitness: {results['optimization_results']['best_fitness']:.4f}")
    print(f"  Final Throughput: {results['optimized_results']['throughput']:.1f} veh/hr")
    
    print("\n" + "="*60 + "\n")


def example_3_analyze_directions():
    """Example 3: Analyze performance by direction."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Directional Analysis")
    print("="*60 + "\n")
    
    app = TrafficOptimizationApp()
    
    # Fetch and optimize
    print("Fetching data and optimizing...")
    app.fetch_data('Erie', max_records=500)
    results = app.run_optimization()
    
    # Analyze by direction
    direction_metrics = results['optimized_results'].get('direction_metrics', {})
    
    if direction_metrics:
        print("\n📍 PERFORMANCE BY DIRECTION:")
        print("-" * 60)
        
        for direction in ['N', 'S', 'E', 'W']:
            if direction in direction_metrics:
                metrics = direction_metrics[direction]
                print(f"\n{direction} (North/South/East/West):")
                print(f"  Throughput: {metrics.get('throughput', 0):.1f} veh/hr")
                print(f"  Avg Delay: {metrics.get('avg_delay', 0):.2f}s")
        
        print("\n" + "-" * 60)
    
    print("\n" + "="*60 + "\n")


def example_4_compare_scenarios():
    """Example 4: Compare different optimization strategies."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comparing Optimization Strategies")
    print("="*60 + "\n")
    
    app = TrafficOptimizationApp()
    
    # Fetch data once
    print("Fetching data...")
    app.fetch_data('Nassau', max_records=500)
    
    print("\nTesting different strategies...\n")
    
    # Strategy 1: Fast optimization (few generations)
    print("Strategy 1: Fast optimization (50 generations)")
    results_fast = app.run_optimization({
        'population_size': 30,
        'generations': 50,
        'mutation_rate': 0.1
    })
    
    # Strategy 2: Thorough optimization (more generations)
    print("\nStrategy 2: Thorough optimization (100 generations)")
    results_thorough = app.run_optimization({
        'population_size': 50,
        'generations': 100,
        'mutation_rate': 0.1
    })
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)
    
    print(f"\nFast Strategy:")
    print(f"  Throughput: {results_fast['optimized_results']['throughput']:.1f} veh/hr")
    print(f"  Avg Delay: {results_fast['optimized_results']['avg_delay']:.2f}s")
    print(f"  Best Fitness: {results_fast['optimization_results']['best_fitness']:.4f}")
    
    print(f"\nThorough Strategy:")
    print(f"  Throughput: {results_thorough['optimized_results']['throughput']:.1f} veh/hr")
    print(f"  Avg Delay: {results_thorough['optimized_results']['avg_delay']:.2f}s")
    print(f"  Best Fitness: {results_thorough['optimization_results']['best_fitness']:.4f}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Run all examples."""
    print("\n" + "🚦" * 20)
    print("Traffic Signal Optimization System - Examples")
    print("🚦" * 20)
    
    # Check if user wants to run specific example
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            '1': example_1_basic_optimization,
            '2': example_2_custom_parameters,
            '3': example_3_analyze_directions,
            '4': example_4_compare_scenarios
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"\nInvalid example number: {example_num}")
            print("Available examples: 1, 2, 3, 4")
            print("\nUsage: python example_usage.py [example_number]")
    else:
        # Run all examples
        print("\nRunning all examples (this may take a few minutes)...\n")
        
        try:
            example_1_basic_optimization()
            example_2_custom_parameters()
            example_3_analyze_directions()
            # example_4_compare_scenarios()  # Commented out as it takes longer
            
            print("\n✅ All examples completed successfully!")
            print("\nTo run a specific example:")
            print("  python example_usage.py 1  # Basic optimization")
            print("  python example_usage.py 2  # Custom parameters")
            print("  python example_usage.py 3  # Directional analysis")
            print("  python example_usage.py 4  # Compare strategies")
            
        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "🚦" * 20 + "\n")


if __name__ == "__main__":
    main()

