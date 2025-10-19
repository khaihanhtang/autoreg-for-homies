#!/bin/bash

# Script to run SlotManager tests with pytest
echo "Running SlotManager tests with pytest..."
echo "========================================"

cd /workspaces/autoreg-for-homies

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing pytest..."
    pip install pytest pytest-cov
fi

# Run the specific test file with pytest
echo "Running tests with coverage..."
pytest tests/test_slot_manager.py -v --tb=short

# Run with coverage if pytest-cov is available
if python -c "import pytest_cov" &> /dev/null; then
    echo ""
    echo "Generating coverage report..."
    pytest tests/ --cov=auto_registration_system --cov-report=term-missing --cov-report=html
    echo "Coverage report saved to htmlcov/index.html"
else
    echo "pytest-cov not available. Install with: pip install pytest-cov"
fi

echo ""
echo "Test execution completed."