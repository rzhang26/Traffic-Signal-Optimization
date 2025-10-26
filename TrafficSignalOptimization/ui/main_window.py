"""
Main Window Module
Implements the main GUI window for the traffic signal optimization application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import logging
from typing import Dict, Any, Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .display import DisplayPanel
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window for Traffic Signal Optimization."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize main window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Traffic Signal Optimization System")
        self.root.geometry("1400x900")
        
        # Data
        self.baseline_results = None
        self.optimized_results = None
        self.baseline_timing = None
        self.optimized_timing = None
        self.optimization_results = None
        
        # Callbacks (to be set by main application)
        self.on_fetch_data = None
        self.on_run_optimization = None
        
        self._setup_ui()
        self._setup_menubar()
        
    def _setup_menubar(self):
        """Setup menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self._export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_ui(self):
        """Setup UI components."""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Left panel - Controls
        self._setup_control_panel(main_container)
        
        # Right panel - Visualization
        self._setup_visualization_panel(main_container)
        
        # Bottom panel - Log/Results
        self._setup_results_panel(main_container)
    
    def _setup_control_panel(self, parent):
        """Setup control panel."""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # County selection
        ttk.Label(control_frame, text="County:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.county_var = tk.StringVar(value="Albany")
        counties = ['Albany', 'Erie', 'Monroe', 'Nassau', 'Onondaga', 'Suffolk', 
                   'Westchester', 'Other']
        county_combo = ttk.Combobox(control_frame, textvariable=self.county_var, 
                                    values=counties, width=25, state='readonly')
        county_combo.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Day of week
        ttk.Label(control_frame, text="Day of Week:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.day_var = tk.StringVar(value="Monday")
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_combo = ttk.Combobox(control_frame, textvariable=self.day_var,
                                values=days, width=25, state='readonly')
        day_combo.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, 
                                                               sticky=(tk.W, tk.E), pady=10)
        
        # Optimization parameters
        ttk.Label(control_frame, text="Population Size:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pop_size_var = tk.IntVar(value=50)
        ttk.Spinbox(control_frame, from_=20, to=200, textvariable=self.pop_size_var,
                   width=23).grid(row=3, column=1, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(control_frame, text="Generations:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.generations_var = tk.IntVar(value=100)
        ttk.Spinbox(control_frame, from_=20, to=500, textvariable=self.generations_var,
                   width=23).grid(row=4, column=1, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(control_frame, text="Mutation Rate:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.mutation_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(control_frame, from_=0.01, to=0.5, increment=0.01,
                   textvariable=self.mutation_var, width=23).grid(row=5, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=6, column=0, columnspan=2,
                                                               sticky=(tk.W, tk.E), pady=10)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.fetch_btn = ttk.Button(button_frame, text="Fetch Data", 
                                    command=self._on_fetch_data_click)
        self.fetch_btn.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.optimize_btn = ttk.Button(button_frame, text="Run Optimization",
                                       command=self._on_optimize_click, state='disabled')
        self.optimize_btn.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Results",
                                    command=self._clear_results)
        self.clear_btn.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var,
                                foreground='blue', font=('Arial', 9, 'italic'))
        status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W)
    
    def _setup_visualization_panel(self, parent):
        """Setup visualization panel."""
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Notebook for multiple visualizations
        self.notebook = ttk.Notebook(viz_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab frames
        self.comparison_frame = ttk.Frame(self.notebook)
        self.timing_frame = ttk.Frame(self.notebook)
        self.convergence_frame = ttk.Frame(self.notebook)
        self.direction_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.comparison_frame, text="Comparison")
        self.notebook.add(self.timing_frame, text="Signal Timing")
        self.notebook.add(self.convergence_frame, text="Convergence")
        self.notebook.add(self.direction_frame, text="By Direction")
    
    def _setup_results_panel(self, parent):
        """Setup results panel."""
        results_frame = ttk.LabelFrame(parent, text="Results & Logs", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12,
                                                      font=('Courier', 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _on_fetch_data_click(self):
        """Handle fetch data button click."""
        if self.on_fetch_data:
            county = self.county_var.get()
            day = self.day_var.get()
            self.status_var.set(f"Fetching data for {county}, {day}...")
            self.progress.start()
            self.root.update()
            
            try:
                success = self.on_fetch_data(county, day)
                if success:
                    self.status_var.set("Data fetched successfully!")
                    self.optimize_btn['state'] = 'normal'
                    self.log_message(f"Successfully fetched data for {county}")
                else:
                    self.status_var.set("Failed to fetch data")
                    messagebox.showerror("Error", "Failed to fetch traffic data")
            except Exception as e:
                self.status_var.set("Error fetching data")
                messagebox.showerror("Error", f"Error: {str(e)}")
                logger.error(f"Error fetching data: {e}")
            finally:
                self.progress.stop()
    
    def _on_optimize_click(self):
        """Handle optimize button click."""
        if self.on_run_optimization:
            self.status_var.set("Running optimization...")
            self.progress.start()
            self.optimize_btn['state'] = 'disabled'
            self.root.update()
            
            # TODO: should really run this in a separate thread so GUI doesn't freeze
            # tried threading but tkinter + threads = headache, just keeping it simple for now
            try:
                params = {
                    'population_size': self.pop_size_var.get(),
                    'generations': self.generations_var.get(),
                    'mutation_rate': self.mutation_var.get()
                }
                
                results = self.on_run_optimization(params)
                if results:
                    self.display_results(results)
                    self.status_var.set("Optimization complete!")
                    self.log_message("Optimization completed successfully")
                else:
                    self.status_var.set("Optimization failed")
                    messagebox.showerror("Error", "Optimization failed")
            except Exception as e:
                self.status_var.set("Error during optimization")
                messagebox.showerror("Error", f"Error: {str(e)}")
                logger.error(f"Error during optimization: {e}")
            finally:
                self.progress.stop()
                self.optimize_btn['state'] = 'normal'
    
    def display_results(self, results: Dict[str, Any]):
        """
        Display optimization results.
        
        Args:
            results: Dictionary containing all results
        """
        self.baseline_results = results.get('baseline_results')
        self.optimized_results = results.get('optimized_results')
        self.baseline_timing = results.get('baseline_timing')
        self.optimized_timing = results.get('optimized_timing')
        self.optimization_results = results.get('optimization_results')
        
        # Clear previous plots
        for frame in [self.comparison_frame, self.timing_frame, 
                     self.convergence_frame, self.direction_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Create comparison chart
        if self.baseline_results and self.optimized_results:
            fig1 = DisplayPanel.create_comparison_chart(self.baseline_results, 
                                                        self.optimized_results)
            self._add_figure_to_frame(fig1, self.comparison_frame)
        
        # Create signal timing diagram
        if self.optimized_timing:
            fig2 = DisplayPanel.create_signal_timing_diagram(self.optimized_timing)
            self._add_figure_to_frame(fig2, self.timing_frame)
        
        # Create convergence plot
        fitness_history = self.optimization_results.get('fitness_history', [])
        if fitness_history:
            fig3 = DisplayPanel.create_fitness_history_plot(fitness_history)
            self._add_figure_to_frame(fig3, self.convergence_frame)
        
        # Create direction analysis
        direction_metrics = self.optimized_results.get('direction_metrics', {})
        if direction_metrics:
            fig4 = DisplayPanel.create_direction_analysis(direction_metrics)
            self._add_figure_to_frame(fig4, self.direction_frame)
        
        # Display text summary
        summary = DisplayPanel.create_summary_text(
            self.baseline_timing,
            self.optimized_timing,
            self.optimization_results
        )
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, summary)
    
    def _add_figure_to_frame(self, fig, frame):
        """Add matplotlib figure to a frame."""
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
    
    def log_message(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.results_text.insert(tk.END, log_line)
        self.results_text.see(tk.END)
    
    def _clear_results(self):
        """Clear all results."""
        self.results_text.delete(1.0, tk.END)
        for frame in [self.comparison_frame, self.timing_frame,
                     self.convergence_frame, self.direction_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        self.status_var.set("Results cleared")
    
    def _export_results(self):
        """Export results to file."""
        if not self.optimized_results:
            messagebox.showwarning("No Results", "No results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                export_data = {
                    'baseline_timing': self.baseline_timing,
                    'optimized_timing': self.optimized_timing,
                    'baseline_results': self.baseline_results,
                    'optimized_results': self.optimized_results,
                    'optimization_results': self.optimization_results
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """Traffic Signal Optimization System
Version 1.0

A comprehensive system for optimizing traffic signal 
timings using genetic algorithms and traffic simulation.

Developed for NYS traffic data analysis.

© 2025 - MIT License"""
        
        messagebox.showinfo("About", about_text)

