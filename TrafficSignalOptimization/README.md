# Traffic Signal Optimization System

This is a traffic signal optimization tool I built for analyzing & optimizing traffic patterns using data from NYS Traffic Data Viewer. It pulls historical traffic counts, runs simulations to figure out how intersections are currently performing, then uses a genetic algorithm to find better signal timings. The whole thing works offline once you've got the data, stores everything in SQLite, & has both a GUI (built w/ Tkinter) and CLI for batch processing multiple intersections.

The optimizer focuses on real metrics that matter - throughput (vehicles/hour), avg delay per vehicle, queue lengths, & number of stops. It uses Webster's formula for delay calculations & proper queuing theory (M/M/1 model) instead of just guessing. The GA runs through different timing configurations (cycle lengths 45-120s, green splits based on actual volumes) & converges on solutions that balance all the objectives. Tested it w/ synthetic data when the API's down & it handles coordination between adjacent signals too.

## Installation

Python 3.8+ required. NumPy 1.x specifically (not 2.x) due to matplotlib compatibility.

```bash
cd TrafficSignalOptimization
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

**GUI Mode:**
```bash
python main.py --gui
```

**CLI Mode:**
```bash
python main.py --county Albany --fetch-data --optimize
python main.py --county Monroe --optimize --generations 200 --export results.json
```

**Verify Installation:**
```bash
python verify_installation.py
```

## Core Components

### Data Pipeline
The system pulls data from NYS Traffic Data Viewer OData API (continuous & short counts). Falls back to synthetic data generation if API's unavailable. Everything gets validated (outlier detection, volume sanity checks), cleaned, & stored in SQLite w/ 4 tables: traffic_data, intersections, signal_timings, optimization_results. Handles missing data via linear interpolation or moving averages.

### Signal Timing Inference
Takes raw traffic volumes by direction & infers baseline signal timings. Calculates cycle lengths (45-120s range) based on total demand, splits green time proportionally to volumes while respecting min green time (10s) & pedestrian crossing requirements. Also estimates coordination offsets for adjacent intersections using travel times & progression bands.

### Traffic Simulation
Discrete-event simulator that models individual vehicles arriving at intersection. Uses Poisson arrivals, tracks queues per approach, calculates delays using Webster's formula. Outputs throughput, avg delay, stops/vehicle, max queue length, & Level of Service grade (A-F). Runs typically 1hr simulation time but configurable.

### Genetic Algorithm Optimizer
Population-based search (default 50 individuals, 100 generations). Chromosome = signal timing config. Fitness function balances 4 objectives: maximize throughput (35% weight), minimize delay (35%), minimize stops (15%), minimize queue length (15%). Uses tournament selection, uniform crossover, gaussian mutation. Elitism keeps top 2 solutions. Converges typically within 50-75 generations.

### Performance Metrics
- **Throughput**: veh/hr capacity utilization
- **Avg Delay**: Webster's uniform + random delay components  
- **Stops**: probability vehicle must stop (affected by saturation)
- **Queue Length**: M/M/1 queuing theory, accounts for oversaturation
- **LOS**: Highway Capacity Manual standards (A ≤10s, B ≤20s, C ≤35s, D ≤55s, E ≤80s, F >80s)

## 🏗️ Architecture

```
TrafficSignalOptimization/
│
├── data_ingestion/          # Data fetching and storage
│   ├── fetch_data.py        # NYS OData API integration
│   └── database.py          # SQLite database management
│
├── data_processing/         # Data validation and inference
│   ├── validate_data.py     # Data validation and cleaning
│   ├── interpolate.py       # Missing data interpolation
│   └── infer_signal_timings.py  # Signal timing inference
│
├── simulation/              # Traffic flow simulation
│   ├── traffic_simulator.py # Discrete-event simulator
│   └── queue_model.py       # Queue theory models
│
├── optimization/            # Optimization algorithms
│   ├── genetic_algorithm.py # GA implementation
│   └── fitness_functions.py # Fitness evaluation
│
├── ui/                      # User interface
│   ├── main_window.py       # Main GUI window
│   └── display.py           # Visualization components
│
├── config/                  # Configuration files
│   ├── settings.json        # Application settings
│   └── signal_timing_defaults.json  # Default timings
│
├── tests/                   # Comprehensive test suite
│   ├── test_data_ingestion.py
│   ├── test_data_processing.py
│   ├── test_simulation.py
│   ├── test_optimization.py
│   └── test_ui.py
│
└── main.py                  # Application entry point
```

## Technical Details

### Algorithm Specifics
**Genetic Algorithm Configuration:**
- Population size: 50 (configurable 20-200)
- Generations: 100 (configurable 20-500)  
- Selection: Tournament (size=3)
- Crossover: Uniform, rate=0.8
- Mutation: Gaussian, rate=0.1, σ=10% of param range
- Elitism: Top 2 preserved

**Simulation Parameters:**
- Duration: 3600s (1 hour)
- Saturation flow: 1800 veh/hr/lane
- Service rate: 0.5 veh/sec
- Arrival distribution: Poisson
- Queue model: M/M/1 w/ oversaturation handling

**Signal Timing Constraints:**
- Cycle length: 45-120s
- Min green: 10s (15s for major arterials)
- Yellow: 3s (fixed)
- All-red: 2s (fixed)
- Lost time: ~5s/phase

### Data Schema
**traffic_data table:**
- station_id, direction, timestamp, volume, speed, occupancy
- Indexed on county, timestamp, station_id

**signal_timings table:**
- cycle_length, green_time_north/south/east/west
- yellow_time, all_red_time, is_optimized flag

**optimization_results table:**
- throughput, avg_delay, avg_stops, max_queue_length
- fitness_score, optimization_date

### API Integration
Uses Socrata Open Data API (SODA). Endpoints:
- Continuous: `qzve-kjga.json`
- Short counts: `qjpt-z4rb.json`

Rate limits: 1000 req/day without token, 10000 w/ app token. Implements exponential backoff & retry logic. Falls back to synthetic data generation (Poisson arrivals, volume peaks at 7-9am & 4-6pm).

## GUI Walkthrough

**Window Layout:**
- Left panel: County/day selection, GA params (pop size, generations, mutation rate)
- Right panel: 4 tabs (comparison charts, timing diagrams, convergence plots, directional analysis)
- Bottom panel: Text output w/ optimization summary

**Typical workflow:**
1. Select county (Albany, Erie, Monroe, Nassau, etc.)
2. Hit "Fetch Data" - pulls from API or generates synthetic
3. Adjust GA params if needed (defaults work fine)
4. "Run Optimization" - takes ~30-60s depending on params
5. Check results in tabs, export to JSON if needed

**CLI Examples:**
```bash
# Quick run w/ defaults
python main.py --county Albany --fetch-data --optimize

# More thorough search
python main.py --county Monroe --optimize --generations 200 --population-size 100

# Batch processing w/ export
python main.py --county Erie --optimize --export results_erie.json
python main.py --county Nassau --optimize --export results_nassau.json

# Debug mode
python main.py --optimize --log-level DEBUG --log-file debug.log
```

## Configuration

Edit `config/settings.json` to tweak behavior:

```json
{
  "simulation": {
    "default_simulation_duration_seconds": 3600,  // 1hr simulation
    "saturation_flow_rate_vphpl": 1800            // veh/hr/lane capacity
  },
  "optimization": {
    "genetic_algorithm": {
      "population_size": 50,
      "generations": 100,
      "mutation_rate": 0.1
    },
    "fitness_weights": {
      "throughput": 0.35,    // Adjust these to prioritize different objectives
      "delay": 0.35,
      "stops": 0.15,
      "queue": 0.15
    }
  }
}
```

`signal_timing_defaults.json` has templates for urban arterial, downtown, suburban, rural intersections. Useful starting points.

## Module Details

**data_ingestion/**
- `fetch_data.py`: Handles Socrata API requests, parses JSON responses, implements rate limiting & retry logic
- `database.py`: SQLite wrapper w/ table creation, CRUD operations, indices for fast queries

**data_processing/**
- `validate_data.py`: Checks volume/speed/occupancy ranges, flags outliers (>3σ), identifies peak hours
- `interpolate.py`: Fills gaps using linear interp or moving avg, handles time series w/ irregular intervals
- `infer_signal_timings.py`: Calculates cycle lengths from volume, splits green proportionally, estimates offsets for coordination

**simulation/**
- `traffic_simulator.py`: Event queue manages arrivals/departures, tracks vehicles through intersection, calculates delay & stops
- `queue_model.py`: Webster's formula for delay, M/M/1 queue length calcs, capacity analysis, LOS determination

**optimization/**
- `genetic_algorithm.py`: Population initialization, selection/crossover/mutation operators, elitism, convergence detection
- `fitness_functions.py`: Multi-objective fitness (weighted sum), constraint penalties, scenario comparison

**ui/**
- `main_window.py`: Tkinter GUI w/ control panel, notebook tabs, progress bar, callbacks to main app
- `display.py`: Matplotlib figure generation (bar charts, timing diagrams, line plots), result formatting

## Testing

```bash
python -m pytest tests/                           # Run all
python -m pytest tests/ --cov=. --cov-report=html # W/ coverage
python -m pytest tests/test_optimization.py -v    # Specific module
```

Test suite covers database ops, API parsing, validation logic, interpolation methods, simulation accuracy, GA convergence, & UI components. ~95% coverage.

## Known Issues & Limitations

- Two-phase signals only (NS/EW) - haven't implemented protected left turn phases yet
- Single intersection optimization - corridor coordination is basic (just offset calcs, no bandwidth optimization)
- Synthetic data generation is pretty naive - real API data gives better results
- GUI can freeze during long optimizations (should've threaded it but tkinter threading is annoying)
- No real-time data integration - purely historical analysis
- Pedestrian timing is simplified (constant walk speed assumption)

## Dependencies

Core: numpy<2.0, matplotlib, requests, pandas
UI: tkinter (usually comes w/ Python)
DB: sqlite3 (standard library)
Testing: pytest, pytest-cov

Note: NumPy must be 1.x not 2.x due to matplotlib compilation.

## Example Usage

```python
# Basic optimization
from main import TrafficOptimizationApp

app = TrafficOptimizationApp()
app.fetch_data('Albany')
results = app.run_optimization()

print(f"Improved throughput by {results['optimized_results']['throughput'] - results['baseline_results']['throughput']:.1f} veh/hr")
```

```python
# Custom GA params
from optimization.genetic_algorithm import GeneticAlgorithm
from simulation.traffic_simulator import TrafficSimulator

traffic_volumes = {'N': 600, 'S': 600, 'E': 400, 'W': 400}

def fitness_func(timing):
    sim = TrafficSimulator(timing)
    results = sim.run_simulation(traffic_volumes, 3600)
    return results['throughput'] / (results['avg_delay'] + 1), results

ga = GeneticAlgorithm(population_size=100, generations=200)
best_timing, results = ga.optimize(initial_timing, fitness_func)
```

See `example_usage.py` for more.

## References

Based on traffic engineering standards:
- Highway Capacity Manual (HCM) 2010 for LOS thresholds
- Webster (1958) for delay formulas
- Kendall notation (M/M/1) for queue modeling
- Standard GA operators from Goldberg's work

Relevant Papers (from Google's Project Green Light):
- https://research.google/pubs/on-the-relationship-of-speed-limit-and-co2-emissions-in-urban-traffic/?_gl=1*1xcowit*_ga*MTQyMTY0NjA5MS4xNzYxNDI0MTYx*_ga_163LFDWS1G*czE3NjE0MjM1NjMkbzMkZzEkdDE3NjE0MjQxNjMkajU3JGwwJGgw
- https://research.google/pubs/estimating-daily-start-times-of-periodic-traffic-light-plans-from-traffic-trajectories/?_gl=1*jhf0sh*_ga*MTQyMTY0NjA5MS4xNzYxNDI0MTYx*_ga_163LFDWS1G*czE3NjE0MjM1NjMkbzMkZzEkdDE3NjE0MjQxNjMkajU3JGwwJGgw
- https://research.google/pubs/systematic-data-driven-detection-of-unintentional-changes-in-traffic-light-plans/?_gl=1*jhf0sh*_ga*MTQyMTY0NjA5MS4xNzYxNDI0MTYx*_ga_163LFDWS1G*czE3NjE0MjM1NjMkbzMkZzEkdDE3NjE0MjQxNjMkajU3JGwwJGgw
- https://research.google/pubs/quantitative-approach-for-coordination-at-scale-of-signalized-2-intersection-pairs/?_gl=1*jhf0sh*_ga*MTQyMTY0NjA5MS4xNzYxNDI0MTYx*_ga_163LFDWS1G*czE3NjE0MjM1NjMkbzMkZzEkdDE3NjE0MjQxNjMkajU3JGwwJGgw
- https://research.google/pubs/city-wide-probe-based-study-of-traffic-variability/?_gl=1*jhf0sh*_ga*MTQyMTY0NjA5MS4xNzYxNDI0MTYx*_ga_163LFDWS1G*czE3NjE0MjM1NjMkbzMkZzEkdDE3NjE0MjQxNjMkajU3JGwwJGgw 


## License

MIT License - see LICENSE file

