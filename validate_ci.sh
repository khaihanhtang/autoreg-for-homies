#!/bin/bash

# validate_ci.sh - Script to validate CI setup locally before pushing to GitHub

set -e  # Exit on any error

echo "🔍 Validating CI/CD Setup for autoreg-for-homies"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "auto_registration_system" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure validated"

# Check required files exist
echo ""
echo "📁 Checking required files..."
required_files=(
    ".github/workflows/ci.yml"
    "requirements.txt"
    "requirements-dev.txt"
    "pytest.ini"
    "pyproject.toml"
    ".flake8"
    "tests/test_slot_manager.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Install dependencies if needed
echo ""
echo "📦 Installing dependencies..."
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-cov
fi

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Run tests
echo ""
echo "🧪 Running tests..."
pytest tests/ -v --tb=short

# Check code formatting (if black is available)
echo ""
echo "🎨 Checking code formatting..."
if command -v black &> /dev/null; then
    echo "Running black check..."
    if black --check --diff . &> /dev/null; then
        echo "✅ Code formatting is good"
    else
        echo "⚠️  Code formatting issues found. Run 'black .' to fix."
    fi
else
    echo "⚠️  Black not installed. Install with: pip install black"
fi

# Check imports (if isort is available)
if command -v isort &> /dev/null; then
    echo "Running import sort check..."
    if isort --check-only . &> /dev/null; then
        echo "✅ Import sorting is good"
    else
        echo "⚠️  Import sorting issues found. Run 'isort .' to fix."
    fi
else
    echo "⚠️  isort not installed. Install with: pip install isort"
fi

# Check linting (if flake8 is available)
echo ""
echo "🔍 Running linter..."
if command -v flake8 &> /dev/null; then
    echo "Running flake8 check..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
        echo "✅ No critical linting errors found"
    else
        echo "❌ Critical linting errors found"
        exit 1
    fi
else
    echo "⚠️  flake8 not installed. Install with: pip install flake8"
fi

# Generate coverage report
echo ""
echo "📊 Generating coverage report..."
if command -v pytest &> /dev/null && python -c "import pytest_cov" &> /dev/null; then
    pytest tests/ --cov=auto_registration_system --cov-report=term-missing
    echo "✅ Coverage report generated"
else
    echo "⚠️  pytest-cov not available for coverage reporting"
fi

echo ""
echo "🎉 CI/CD validation completed successfully!"
echo "Your project is ready for GitHub Actions."
echo ""
echo "Next steps:"
echo "1. Commit your changes: git add . && git commit -m 'Add CI/CD setup'"
echo "2. Push to GitHub: git push"
echo "3. Check the Actions tab in your GitHub repository"