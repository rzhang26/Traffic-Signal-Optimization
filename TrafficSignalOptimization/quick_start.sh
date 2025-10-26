#!/bin/bash
# Quick Start Script for Traffic Signal Optimization System

echo "🚦 Traffic Signal Optimization System - Quick Start"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Setting up directories..."
mkdir -p logs
mkdir -p exports
echo "✓ Directories created"
echo ""

# Display menu
echo "=================================================="
echo "What would you like to do?"
echo "=================================================="
echo "1) Launch GUI application"
echo "2) Run CLI demo (Albany County)"
echo "3) Run tests"
echo "4) View README"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Launching GUI..."
        python main.py --gui
        ;;
    2)
        echo ""
        echo "Running CLI demo for Albany County..."
        python main.py --county Albany --fetch-data --optimize --export exports/demo_results.json
        ;;
    3)
        echo ""
        echo "Running tests..."
        python -m pytest tests/ -v
        ;;
    4)
        echo ""
        less README.md
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "Done! Check the logs/ and exports/ directories for output."
echo "To run again, execute: ./quick_start.sh"
echo "=================================================="

