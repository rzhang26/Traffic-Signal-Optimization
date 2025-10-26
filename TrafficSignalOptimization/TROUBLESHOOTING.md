# Troubleshooting Guide

## Common Issues and Solutions

### 1. NumPy Version Compatibility Error

**Error Message:**
```
ImportError: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.1
```

**Solution:**
The application requires NumPy 1.x for compatibility with matplotlib. Run:
```bash
pip install "numpy>=1.24.0,<2.0.0" "matplotlib>=3.7.0,<3.10.0" --upgrade
```

Or simply reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### 2. Tkinter Not Available

**Error Message:**
```
ModuleNotFoundError: No module named '_tkinter'
```

**Solution:**

**On macOS:**
```bash
# Tkinter comes with Python on macOS, but ensure you're using system Python or:
brew install python-tk@3.12
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**On Windows:**
Tkinter is included with Python installation from python.org

### 3. Database Permission Errors

**Error Message:**
```
sqlite3.OperationalError: unable to open database file
```

**Solution:**
Ensure you have write permissions in the current directory:
```bash
chmod 755 .
# Or run from a directory where you have write access
```

### 4. Import Errors

**Error Message:**
```
ModuleNotFoundError: No module named 'data_ingestion'
```

**Solution:**
Ensure you're running from the TrafficSignalOptimization directory:
```bash
cd TrafficSignalOptimization
python main.py --help
```

### 5. API Rate Limiting

**Symptom:** Slow data fetching or no data returned

**Solution:**
1. Get a Socrata app token from https://data.ny.gov/profile/app_tokens
2. Add it to your environment:
```bash
export SOCRATA_APP_TOKEN="your_token_here"
```

Or the application will use synthetic demo data automatically.

### 6. Matplotlib Display Issues

**Error Message:**
```
UserWarning: Matplotlib is currently using agg, which is a non-GUI backend
```

**Solution:**
For GUI mode, ensure you have a display available. On headless systems, use CLI mode:
```bash
python main.py --county Albany --fetch-data --optimize --export results.json
```

### 7. Memory Issues with Large Datasets

**Symptom:** Application crashes with large `--max-records` values

**Solution:**
Start with smaller datasets:
```bash
python main.py --county Albany --fetch-data --max-records 1000 --optimize
```

Increase gradually based on available memory.

### 8. Genetic Algorithm Not Converging

**Symptom:** Optimization takes too long or doesn't improve results

**Solution:**
Adjust GA parameters:
```bash
# Increase generations for better results (slower)
python main.py --optimize --generations 200

# Increase population for broader search (slower)
python main.py --optimize --population-size 100

# Increase mutation rate for more exploration
python main.py --optimize --mutation-rate 0.2
```

### 9. Test Failures

**Error Message:**
```
FAILED tests/test_*.py
```

**Solution:**
Ensure all dependencies are installed:
```bash
pip install pytest pytest-cov --upgrade
pip install -r requirements.txt --upgrade
python -m pytest tests/ -v
```

### 10. Configuration Not Loading

**Symptom:** Application ignores config/settings.json

**Solution:**
Verify JSON syntax:
```bash
python -m json.tool config/settings.json
```

Ensure file exists in correct location:
```bash
ls -la config/settings.json
```

## Dependency Version Requirements

For best compatibility, use these version ranges:

```
Python: 3.8 - 3.12
NumPy: 1.24.0 - 1.26.x (NOT 2.x)
Matplotlib: 3.7.0 - 3.9.x
Pandas: 2.0.0 - 2.2.x
Requests: 2.31.0+
```

## Platform-Specific Notes

### macOS M1/M2
- All functionality tested and working
- Use native Python or conda environment
- GUI works with both system Python and Anaconda

### Linux
- Ensure Tkinter is installed separately
- May need to install python3-tk package
- Works well in WSL2

### Windows
- Use Python from python.org (includes Tkinter)
- May need Visual C++ redistributable for some packages
- Use Command Prompt or PowerShell, not Git Bash for GUI

## Getting Help

If you encounter issues not listed here:

1. Check the README.md for detailed setup instructions
2. Review the logs in `traffic_optimizer.log` (if using --log-file)
3. Run with DEBUG logging:
   ```bash
   python main.py --log-level DEBUG --optimize
   ```
4. Check existing GitHub issues
5. Create a new issue with:
   - Python version (`python --version`)
   - OS and version
   - Full error traceback
   - Steps to reproduce

## Quick Diagnostic

Run this diagnostic script to check your environment:

```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import numpy
    print(f'NumPy: {numpy.__version__} ✓')
except Exception as e:
    print(f'NumPy: ERROR - {e}')

try:
    import matplotlib
    print(f'Matplotlib: {matplotlib.__version__} ✓')
except Exception as e:
    print(f'Matplotlib: ERROR - {e}')

try:
    import tkinter
    print(f'Tkinter: Available ✓')
except Exception as e:
    print(f'Tkinter: ERROR - {e}')

try:
    import requests
    print(f'Requests: Available ✓')
except Exception as e:
    print(f'Requests: ERROR - {e}')

try:
    import sqlite3
    print(f'SQLite3: Available ✓')
except Exception as e:
    print(f'SQLite3: ERROR - {e}')

print('\\nDiagnostic complete!')
"
```

## Performance Tips

1. **Use synthetic data for testing:**
   The application automatically generates demo data if API fetch fails

2. **Reduce simulation duration for faster results:**
   Edit `config/settings.json`:
   ```json
   "simulation": {
     "default_simulation_duration_seconds": 1800
   }
   ```

3. **Use fewer generations for quick tests:**
   ```bash
   python main.py --optimize --generations 50 --population-size 30
   ```

4. **Enable caching** (planned feature):
   Will significantly speed up repeated optimizations

## Known Limitations

1. **Two-phase signals only** - Four-phase operation not yet implemented
2. **Single intersection** - Corridor optimization planned for future
3. **Offline mode** - No real-time data integration yet
4. **API rate limits** - May need Socrata app token for large datasets

## Still Having Issues?

Contact information:
- GitHub Issues: [Your GitHub repo]
- Documentation: README.md, CONTRIBUTING.md
- Examples: example_usage.py

