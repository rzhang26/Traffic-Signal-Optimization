# Contributing to Traffic Signal Optimization System

Thank you for your interest in contributing to the Traffic Signal Optimization System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Exercise empathy and kindness
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show courtesy and respect towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of traffic engineering concepts (helpful but not required)
- Familiarity with Python, NumPy, and Tkinter

### Setup Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/traffic-optimizer.git
   cd traffic-optimizer/TrafficSignalOptimization
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies including dev tools:
   ```bash
   pip install -r requirements.txt
   pip install black flake8 mypy pytest pytest-cov
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `bugfix/description`
- Documentation: `docs/description`
- Performance: `perf/description`

### Commit Messages

Follow the conventional commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add multi-intersection corridor optimization

- Implement corridor coordination algorithm
- Add visualization for corridor analysis
- Update tests for new functionality
```

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Formatting

Format your code using Black:
```bash
black .
```

Check code quality with flake8:
```bash
flake8 . --max-line-length=100 --ignore=E203,W503
```

Type check with mypy:
```bash
mypy . --ignore-missing-imports
```

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include type hints in function signatures
- Add inline comments for complex logic

Example:
```python
def calculate_delay(
    arrival_rate: float,
    green_time: float,
    red_time: float
) -> Dict[str, float]:
    """
    Calculate average delay per vehicle using Webster's formula.
    
    Args:
        arrival_rate: Vehicle arrival rate (vehicles per second)
        green_time: Green time duration (seconds)
        red_time: Red time duration (seconds)
        
    Returns:
        Dictionary with delay metrics including uniform_delay,
        random_delay, and total_delay
        
    Raises:
        ValueError: If any parameter is negative
    """
    # Implementation
```

## Testing

### Writing Tests

- Write unit tests for all new functionality
- Aim for >90% code coverage
- Use descriptive test names
- Include edge cases and error conditions

### Running Tests

Run all tests:
```bash
python -m pytest tests/
```

Run with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

Run specific test file:
```bash
python -m pytest tests/test_optimization.py -v
```

### Test Structure

```python
import unittest

class TestFeature(unittest.TestCase):
    """Test suite for Feature functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        pass
    
    def tearDown(self):
        """Cleanup after tests."""
        pass
    
    def test_basic_functionality(self):
        """Test basic feature operation."""
        # Arrange
        input_data = ...
        
        # Act
        result = feature_function(input_data)
        
        # Assert
        self.assertEqual(result, expected_value)
```

## Documentation

### Code Documentation

- All modules should have module-level docstrings
- All public classes and functions must have docstrings
- Complex algorithms should include references to academic papers or standards

### README Updates

When adding new features, update:
- Feature list in README
- Usage examples
- Configuration options if applicable

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Update documentation
3. Add tests for new functionality
4. Run code formatters and linters
5. Update CHANGELOG.md

### Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to GitHub and create a Pull Request

3. Fill out the PR template with:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)

4. Ensure CI checks pass

5. Request review from maintainers

### PR Review Process

- Maintainers will review your code
- Address any feedback or requested changes
- Once approved, maintainers will merge your PR

### After Your PR is Merged

- Delete your feature branch
- Pull the latest changes from main:
  ```bash
  git checkout main
  git pull upstream main
  ```

## Areas for Contribution

### High Priority

- Real-time data integration
- Four-phase signal operation
- Multi-intersection corridor optimization
- Performance optimizations
- Additional test coverage

### Medium Priority

- Web-based interface (Flask/Streamlit)
- Machine learning models for traffic prediction
- Environmental impact metrics
- Integration with SUMO simulator
- Mobile data collection app

### Good First Issues

- Documentation improvements
- UI enhancements
- Additional chart types
- Configuration validation
- Error message improvements

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing documentation
- Review closed issues for similar discussions

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (when available)

Thank you for contributing to making traffic flow better! 🚦

