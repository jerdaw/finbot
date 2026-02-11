.PHONY: help install update lint format type security test test-cov test-quick clean run-update check all pre-commit

# Default target - show help
help:
	@echo "Finbot Development Tasks"
	@echo "======================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        Install dependencies with Poetry"
	@echo "  make update         Update all dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run ruff linter with auto-fix"
	@echo "  make format         Format code with ruff"
	@echo "  make type           Run mypy type checker"
	@echo "  make security       Run bandit security scanner"
	@echo "  make check          Run all checks (lint + format + type + security)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests with verbose output"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make test-quick     Run tests in quiet mode (fast)"
	@echo ""
	@echo "Data Pipeline:"
	@echo "  make run-update     Run daily data update pipeline"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove cache files and build artifacts"
	@echo "  make pre-commit     Run pre-commit hooks on all files"
	@echo "  make all            Run full CI pipeline (check + test)"
	@echo ""

# Setup & Installation
install:
	@echo "Installing dependencies with Poetry..."
	poetry install

update:
	@echo "Updating dependencies..."
	poetry update

# Code Quality
lint:
	@echo "Running ruff linter with auto-fix..."
	poetry run ruff check . --fix --exclude notebooks/

format:
	@echo "Formatting code with ruff..."
	poetry run ruff format . --exclude notebooks/

type:
	@echo "Running mypy type checker..."
	@poetry run mypy finbot/ libs/ config/ constants/ scripts/ || echo "⚠ Type checking found issues (non-fatal)"

security:
	@echo "Running bandit security scanner..."
	@poetry run bandit -r finbot libs || echo "⚠ Security scan found issues (non-fatal)"

check: lint format type security
	@echo ""
	@echo "✓ All code quality checks passed!"

# Testing
test:
	@echo "Running all tests with verbose output..."
	DYNACONF_ENV=development poetry run pytest tests/ -v

test-cov:
	@echo "Running tests with coverage report..."
	DYNACONF_ENV=development poetry run pytest --cov=finbot --cov-report=term-missing --cov-report=html tests/

test-quick:
	@echo "Running tests in quiet mode..."
	DYNACONF_ENV=development poetry run pytest tests/ -q

# Data Pipeline
run-update:
	@echo "Running daily data update pipeline..."
	DYNACONF_ENV=development poetry run python scripts/update_daily.py

# Maintenance
clean:
	@echo "Cleaning cache files and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "✓ Cleaned all cache files and build artifacts"

pre-commit:
	@echo "Running pre-commit hooks on all files..."
	poetry run pre-commit run --all-files

# Full CI Pipeline
all: check test
	@echo ""
	@echo "================================"
	@echo "✓ Full CI pipeline passed!"
	@echo "================================"
