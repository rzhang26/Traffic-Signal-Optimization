"""
Display Module
Handles visualization and display of optimization results.
"""

import logging
from typing import Dict, List, Any
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

logger = logging.getLogger(__name__)


class DisplayPanel:
    """Handles creating visualizations for optimization results."""
    
    @staticmethod
    def create_comparison_chart(
        baseline_results: Dict[str, Any],
        optimized_results: Dict[str, Any]
    ) -> Figure:
        """
        Create bar chart comparing baseline and optimized results.
        
        Args:
            baseline_results: Baseline simulation results
            optimized_results: Optimized simulation results
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Traffic Signal Optimization Results', fontsize=16, fontweight='bold')
        
        metrics = [
            ('throughput', 'Throughput (veh/hr)', axes[0, 0], True),
            ('avg_delay', 'Average Delay (sec)', axes[0, 1], False),
            ('avg_stops', 'Average Stops', axes[1, 0], False),
            ('max_queue_length', 'Max Queue Length (veh)', axes[1, 1], False)
        ]
        
        for metric_key, label, ax, higher_better in metrics:
            baseline_val = baseline_results.get(metric_key, 0)
            optimized_val = optimized_results.get(metric_key, 0)
            
            x = ['Baseline', 'Optimized']
            values = [baseline_val, optimized_val]
            
            colors = ['#e74c3c', '#2ecc71'] if higher_better else ['#2ecc71', '#e74c3c']
            if not higher_better and optimized_val < baseline_val:
                colors = ['#e74c3c', '#2ecc71']
            elif not higher_better and optimized_val > baseline_val:
                colors = ['#2ecc71', '#e74c3c']
            
            bars = ax.bar(x, values, color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylabel(label, fontweight='bold')
            ax.set_title(label)
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontweight='bold')
            
            # Add improvement percentage
            if baseline_val != 0:
                improvement = ((optimized_val - baseline_val) / baseline_val) * 100
                improvement_text = f'{improvement:+.1f}%'
                ax.text(0.5, 0.95, improvement_text,
                       transform=ax.transAxes,
                       ha='center', va='top',
                       fontsize=12, fontweight='bold',
                       color='green' if (higher_better and improvement > 0) or (not higher_better and improvement < 0) else 'red',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_signal_timing_diagram(
        signal_timing: Dict[str, Any]
    ) -> Figure:
        """
        Create signal timing diagram.
        
        Args:
            signal_timing: Signal timing configuration
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        cycle_length = signal_timing.get('cycle_length', 90)
        yellow_time = signal_timing.get('yellow_time', 3)
        all_red_time = signal_timing.get('all_red_time', 2)
        
        # NS phase
        ns_green = signal_timing.get('green_time_north', 30)
        
        # EW phase
        ew_green = signal_timing.get('green_time_east', 30)
        
        directions = ['North-South', 'East-West']
        y_positions = [1, 0]
        
        for direction, y_pos in zip(directions, y_positions):
            if direction == 'North-South':
                # Green
                ax.barh(y_pos, ns_green, left=0, height=0.8, 
                       color='green', alpha=0.7, edgecolor='black', linewidth=2)
                # Yellow
                ax.barh(y_pos, yellow_time, left=ns_green, height=0.8,
                       color='yellow', alpha=0.7, edgecolor='black', linewidth=2)
                # All-red
                ax.barh(y_pos, all_red_time, left=ns_green + yellow_time, height=0.8,
                       color='red', alpha=0.7, edgecolor='black', linewidth=2)
                # Red during EW phase
                red_start = ns_green + yellow_time + all_red_time
                red_duration = ew_green + yellow_time + all_red_time
                ax.barh(y_pos, red_duration, left=red_start, height=0.8,
                       color='red', alpha=0.7, edgecolor='black', linewidth=2)
            else:
                # Red during NS phase
                red_duration = ns_green + yellow_time + all_red_time
                ax.barh(y_pos, red_duration, left=0, height=0.8,
                       color='red', alpha=0.7, edgecolor='black', linewidth=2)
                # Green
                ax.barh(y_pos, ew_green, left=red_duration, height=0.8,
                       color='green', alpha=0.7, edgecolor='black', linewidth=2)
                # Yellow
                ax.barh(y_pos, yellow_time, left=red_duration + ew_green, height=0.8,
                       color='yellow', alpha=0.7, edgecolor='black', linewidth=2)
                # All-red
                ax.barh(y_pos, all_red_time, left=red_duration + ew_green + yellow_time, height=0.8,
                       color='red', alpha=0.7, edgecolor='black', linewidth=2)
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels(directions, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontweight='bold')
        ax.set_title(f'Signal Timing Diagram (Cycle Length: {cycle_length}s)', 
                    fontsize=14, fontweight='bold')
        ax.set_xlim(0, cycle_length)
        ax.grid(axis='x', alpha=0.3)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, edgecolor='black', label='Green'),
            Patch(facecolor='yellow', alpha=0.7, edgecolor='black', label='Yellow'),
            Patch(facecolor='red', alpha=0.7, edgecolor='black', label='Red')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_fitness_history_plot(
        fitness_history: List[float]
    ) -> Figure:
        """
        Create fitness evolution plot.
        
        Args:
            fitness_history: List of fitness values over generations
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        
        generations = list(range(1, len(fitness_history) + 1))
        ax.plot(generations, fitness_history, 'b-', linewidth=2, marker='o', 
               markersize=4, markevery=max(1, len(generations)//20))
        
        ax.set_xlabel('Generation', fontweight='bold')
        ax.set_ylabel('Fitness Score', fontweight='bold')
        ax.set_title('Genetic Algorithm Convergence', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Highlight best fitness
        best_fitness = max(fitness_history)
        best_gen = fitness_history.index(best_fitness) + 1
        ax.axhline(y=best_fitness, color='r', linestyle='--', alpha=0.5)
        ax.text(len(generations) * 0.7, best_fitness * 1.05, 
               f'Best: {best_fitness:.4f} (Gen {best_gen})',
               fontweight='bold', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_direction_analysis(
        direction_metrics: Dict[str, Dict[str, float]]
    ) -> Figure:
        """
        Create directional analysis chart.
        
        Args:
            direction_metrics: Metrics by direction
            
        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        directions = list(direction_metrics.keys())
        throughputs = [direction_metrics[d].get('throughput', 0) for d in directions]
        delays = [direction_metrics[d].get('avg_delay', 0) for d in directions]
        
        # Throughput by direction
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        ax1.bar(directions, throughputs, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Throughput (veh/hr)', fontweight='bold')
        ax1.set_title('Throughput by Direction', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        for i, (d, t) in enumerate(zip(directions, throughputs)):
            ax1.text(i, t, f'{t:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Delay by direction
        ax2.bar(directions, delays, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Average Delay (sec)', fontweight='bold')
        ax2.set_title('Average Delay by Direction', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for i, (d, delay) in enumerate(zip(directions, delays)):
            ax2.text(i, delay, f'{delay:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_summary_text(
        baseline_timing: Dict[str, Any],
        optimized_timing: Dict[str, Any],
        optimization_results: Dict[str, Any]
    ) -> str:
        """
        Create text summary of optimization results.
        
        Args:
            baseline_timing: Baseline signal timing
            optimized_timing: Optimized signal timing
            optimization_results: Optimization results
            
        Returns:
            Formatted text summary
        """
        summary = "=" * 60 + "\n"
        summary += "TRAFFIC SIGNAL OPTIMIZATION SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        summary += "BASELINE SIGNAL TIMING:\n"
        summary += f"  Cycle Length: {baseline_timing.get('cycle_length', 0)} seconds\n"
        summary += f"  NS Green Time: {baseline_timing.get('green_time_north', 0):.1f} seconds\n"
        summary += f"  EW Green Time: {baseline_timing.get('green_time_east', 0):.1f} seconds\n\n"
        
        summary += "OPTIMIZED SIGNAL TIMING:\n"
        summary += f"  Cycle Length: {optimized_timing.get('cycle_length', 0)} seconds\n"
        summary += f"  NS Green Time: {optimized_timing.get('green_time_north', 0):.1f} seconds\n"
        summary += f"  EW Green Time: {optimized_timing.get('green_time_east', 0):.1f} seconds\n\n"
        
        summary += "PERFORMANCE IMPROVEMENTS:\n"
        sim_results = optimization_results.get('simulation_results', {})
        summary += f"  Throughput: {sim_results.get('throughput', 0):.1f} veh/hr\n"
        summary += f"  Average Delay: {sim_results.get('avg_delay', 0):.2f} seconds\n"
        summary += f"  Average Stops: {sim_results.get('avg_stops', 0):.2f}\n"
        summary += f"  Max Queue Length: {sim_results.get('max_queue_length', 0):.1f} vehicles\n"
        summary += f"  Level of Service: {sim_results.get('level_of_service', 'N/A')}\n\n"
        
        summary += "OPTIMIZATION PROCESS:\n"
        summary += f"  Generations Run: {optimization_results.get('generations', 0)}\n"
        summary += f"  Best Fitness: {optimization_results.get('best_fitness', 0):.4f}\n"
        summary += f"  Population Size: {optimization_results.get('final_population_size', 0)}\n\n"
        
        summary += "=" * 60 + "\n"
        
        return summary

