#!/usr/bin/env python3
"""
Installation Verification Script
Checks that all dependencies and modules are properly installed.
"""

import sys

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️  Warning: Python 3.8+ recommended")
        return False
    return True

def check_module(module_name, version_check=True):
    """Check if a module is installed and optionally check version."""
    try:
        module = __import__(module_name)
        if version_check and hasattr(module, '__version__'):
            print(f"✓ {module_name} {module.__version__}")
        else:
            print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - NOT INSTALLED")
        print(f"  Error: {e}")
        return False

def check_numpy_version():
    """Check NumPy version specifically."""
    try:
        import numpy
        version = numpy.__version__
        major = int(version.split('.')[0])
        print(f"✓ NumPy {version}")
        if major >= 2:
            print("  ⚠️  Warning: NumPy 2.x may cause compatibility issues")
            print("  Recommended: Run 'pip install \"numpy<2.0\" --upgrade'")
            return False
        return True
    except ImportError:
        print("✗ NumPy - NOT INSTALLED")
        return False

def check_custom_modules():
    """Check custom application modules."""
    modules = [
        'data_ingestion',
        'data_processing',
        'simulation',
        'optimization',
        'ui'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - ERROR")
            print(f"  {e}")
            all_ok = False
    
    return all_ok

def check_tkinter():
    """Check if Tkinter is available."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        print("✓ Tkinter (GUI support available)")
        return True
    except ImportError:
        print("✗ Tkinter - NOT AVAILABLE")
        print("  GUI mode will not work. CLI mode still available.")
        return False
    except Exception as e:
        print("⚠️  Tkinter - Issues detected")
        print(f"  {e}")
        return False

def check_database():
    """Check SQLite3."""
    try:
        import sqlite3
        print(f"✓ SQLite {sqlite3.sqlite_version}")
        return True
    except ImportError:
        print("✗ SQLite3 - NOT AVAILABLE")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Traffic Signal Optimization - Installation Verification")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("Checking core dependencies...")
    numpy_ok = check_numpy_version()
    matplotlib_ok = check_module('matplotlib')
    requests_ok = check_module('requests')
    pandas_ok = check_module('pandas')
    print()
    
    print("Checking system libraries...")
    sqlite_ok = check_database()
    tkinter_ok = check_tkinter()
    print()
    
    print("Checking application modules...")
    # Add current directory to path
    sys.path.insert(0, '.')
    modules_ok = check_custom_modules()
    print()
    
    print("=" * 60)
    
    # Summary
    all_critical_ok = (python_ok and numpy_ok and matplotlib_ok and 
                       requests_ok and sqlite_ok and modules_ok)
    
    if all_critical_ok:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Your installation is ready to use.")
        print()
        print("Quick start:")
        print("  GUI Mode:  python main.py --gui")
        print("  CLI Mode:  python main.py --county Albany --optimize")
        print("  Examples:  python example_usage.py")
    else:
        print("⚠️  SOME ISSUES DETECTED")
        print()
        print("Please fix the issues above before running the application.")
        print()
        print("To install missing dependencies:")
        print("  pip install -r requirements.txt")
        print()
        print("For troubleshooting, see TROUBLESHOOTING.md")
    
    print("=" * 60)
    
    return 0 if all_critical_ok else 1

if __name__ == "__main__":
    sys.exit(main())

