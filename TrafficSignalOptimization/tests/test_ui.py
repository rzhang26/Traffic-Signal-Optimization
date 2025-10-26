"""
Unit tests for UI module.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.main_window import MainWindow
from ui.display import DisplayPanel


class TestDisplayPanel(unittest.TestCase):
    """Test display panel functionality."""
    
    def setUp(self):
        """Setup test data."""
        self.baseline_results = {
            'throughput': 1400,
            'avg_delay': 30.0,
            'avg_stops': 1.5,
            'max_queue_length': 10.0
        }
        
        self.optimized_results = {
            'throughput': 1500,
            'avg_delay': 25.0,
            'avg_stops': 1.2,
            'max_queue_length': 8.5
        }
        
        self.signal_timing = {
            'cycle_length': 90,
            'green_time_north': 35,
            'green_time_south': 35,
            'green_time_east': 30,
            'green_time_west': 30,
            'yellow_time': 3.0,
            'all_red_time': 2.0
        }
    
    def test_create_comparison_chart(self):
        """Test creating comparison chart."""
        fig = DisplayPanel.create_comparison_chart(
            self.baseline_results,
            self.optimized_results
        )
        
        self.assertIsNotNone(fig)
        # Matplotlib figure object
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_create_signal_timing_diagram(self):
        """Test creating signal timing diagram."""
        fig = DisplayPanel.create_signal_timing_diagram(self.signal_timing)
        
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_create_fitness_history_plot(self):
        """Test creating fitness history plot."""
        fitness_history = [0.5, 0.6, 0.7, 0.75, 0.78, 0.8]
        fig = DisplayPanel.create_fitness_history_plot(fitness_history)
        
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_create_direction_analysis(self):
        """Test creating direction analysis chart."""
        direction_metrics = {
            'N': {'throughput': 400, 'avg_delay': 22},
            'S': {'throughput': 400, 'avg_delay': 23},
            'E': {'throughput': 350, 'avg_delay': 28},
            'W': {'throughput': 350, 'avg_delay': 27}
        }
        
        fig = DisplayPanel.create_direction_analysis(direction_metrics)
        
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_create_summary_text(self):
        """Test creating summary text."""
        baseline_timing = self.signal_timing.copy()
        optimized_timing = self.signal_timing.copy()
        optimized_timing['cycle_length'] = 85
        
        optimization_results = {
            'simulation_results': self.optimized_results,
            'best_fitness': 0.8,
            'generations': 100
        }
        
        summary = DisplayPanel.create_summary_text(
            baseline_timing,
            optimized_timing,
            optimization_results
        )
        
        self.assertIsInstance(summary, str)
        self.assertIn('OPTIMIZATION SUMMARY', summary)
        self.assertIn('85', summary)  # Optimized cycle length


class TestMainWindow(unittest.TestCase):
    """Test main window functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Setup Tkinter root for all tests."""
        cls.root = tk.Tk()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup Tkinter root."""
        cls.root.destroy()
    
    def test_main_window_creation(self):
        """Test main window creation."""
        window = MainWindow(self.root)
        self.assertIsNotNone(window)
        self.assertEqual(window.root, self.root)
    
    def test_log_message(self):
        """Test logging message to UI."""
        window = MainWindow(self.root)
        window.log_message("Test message")
        
        content = window.results_text.get(1.0, tk.END)
        self.assertIn("Test message", content)
    
    def test_clear_results(self):
        """Test clearing results."""
        window = MainWindow(self.root)
        window.log_message("Test message")
        window._clear_results()
        
        content = window.results_text.get(1.0, tk.END).strip()
        self.assertEqual(content, "")


if __name__ == '__main__':
    unittest.main()

