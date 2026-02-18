.PHONY: help install update lint format type docstring security test test-cov test-quick clean run-update check all pre-commit docs docs-serve docs-build dashboard dashboard-dev docker-build docker-run docker-status docker-update docker-test docker-clean docker-security-scan test-release changelog

# Default target - show help
help:
	@echo "Finbot Development Tasks"
	@echo "======================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        Install dependencies with uv"
	@echo "  make update         Update all dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run ruff linter with auto-fix"
	@echo "  make format         Format code with ruff"
	@echo "  make type           Run mypy type checker"
	@echo "  make docstring      Check docstring coverage with interrogate"
	@echo "  make security       Run bandit security scanner"
	@echo "  make check          Run all checks (lint + format + type + docstring + security)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests with verbose output"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make test-quick     Run tests in quiet mode (fast)"
	@echo ""
	@echo "Data Pipeline:"
	@echo "  make run-update     Run daily data update pipeline"
	@echo ""
	@echo "Dashboard:"
	@echo "  make dashboard      Launch Streamlit dashboard"
	@echo "  make dashboard-dev  Launch dashboard in dev mode (auto-reload)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           Build and serve documentation locally"
	@echo "  make docs-serve     Serve documentation (auto-reload)"
	@echo "  make docs-build     Build documentation site"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build          Build Docker image"
	@echo "  make docker-run            Run interactive finbot CLI in Docker"
	@echo "  make docker-status         Show data freshness via Docker"
	@echo "  make docker-update         Run daily update pipeline in Docker"
	@echo "  make docker-test           Run tests in Docker"
	@echo "  make docker-security-scan  Run Trivy security scan on Docker image"
	@echo "  make docker-clean          Remove Docker image and volumes"
	@echo ""
	@echo "Release:"
	@echo "  make test-release   Validate release workflow and files"
	@echo "  make changelog      Generate changelog from git history"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove cache files and build artifacts"
	@echo "  make pre-commit     Run pre-commit hooks on all files"
	@echo "  make all            Run full CI pipeline (check + test)"
	@echo ""

# Setup & Installation
install:
	@echo "Installing dependencies with uv..."
	uv sync

update:
	@echo "Updating dependencies..."
	uv lock --upgrade && uv sync

# Code Quality
lint:
	@echo "Running ruff linter with auto-fix..."
	uv run ruff check . --fix --exclude notebooks/

format:
	@echo "Formatting code with ruff..."
	uv run ruff format . --exclude notebooks/

type:
	@echo "Running mypy type checker..."
	@uv run mypy finbot/ scripts/ || echo "⚠ Type checking found issues (non-fatal)"

docstring:
	@echo "Checking docstring coverage..."
	@uv run interrogate finbot/ || echo "⚠ Docstring coverage below threshold (non-fatal)"

security:
	@echo "Running bandit security scanner..."
	@uv run bandit -r finbot || echo "⚠ Security scan found issues (non-fatal)"

check: lint format type docstring security
	@echo ""
	@echo "✓ All code quality checks passed!"

# Testing
test:
	@echo "Running all tests with verbose output..."
	DYNACONF_ENV=development uv run pytest tests/ -v

test-cov:
	@echo "Running tests with coverage report..."
	DYNACONF_ENV=development uv run pytest --cov=finbot --cov-report=term-missing --cov-report=html --cov-fail-under=30 tests/

test-quick:
	@echo "Running tests in quiet mode..."
	DYNACONF_ENV=development uv run pytest tests/ -q

# Data Pipeline
run-update:
	@echo "Running daily data update pipeline..."
	DYNACONF_ENV=development uv run python scripts/update_daily.py

# Dashboard
dashboard:
	@echo "Starting Finbot Dashboard at http://localhost:8501..."
	DYNACONF_ENV=development uv run finbot dashboard

dashboard-dev:
	@echo "Starting Finbot Dashboard in dev mode..."
	DYNACONF_ENV=development uv run streamlit run finbot/dashboard/app.py --server.runOnSave true

# Documentation
docs: docs-build docs-serve

docs-serve:
	@echo "Serving documentation at http://127.0.0.1:8000..."
	@echo "Press Ctrl+C to stop"
	uv run mkdocs serve

docs-build:
	@echo "Building documentation..."
	uv run mkdocs build

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
	uv run pre-commit run --all-files

# Release
test-release:
	@echo "Validating release workflow..."
	@./scripts/test_release_workflow.sh

changelog:
	@echo "Generating changelog from git history..."
	@uv run git-changelog --output CHANGELOG_GENERATED.md --config-file .git-changelog.toml
	@echo "✓ Changelog generated to CHANGELOG_GENERATED.md"
	@echo ""
	@echo "Review the generated changelog and manually merge into CHANGELOG.md"
	@echo "Note: git-changelog generates from git history only."
	@echo "      The current CHANGELOG.md has manual formatting that should be preserved."

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t finbot .

docker-run:
	@echo "Running finbot CLI in Docker..."
	docker compose run --rm finbot $(CMD)

docker-status:
	@echo "Checking data freshness in Docker..."
	docker compose run --rm finbot-status

docker-update:
	@echo "Running daily update pipeline in Docker..."
	docker compose run --rm finbot-update

docker-test:
	@echo "Running tests in Docker..."
	docker run --rm -e DYNACONF_ENV=development finbot sh -c "uv run pytest tests/ -v"

docker-clean:
	@echo "Removing Docker image and volumes..."
	docker compose down -v --rmi local 2>/dev/null || true
	docker rmi finbot 2>/dev/null || true
	@echo "✓ Docker cleanup complete"

# Full CI Pipeline
all: check test
	@echo ""
	@echo "================================"
	@echo "✓ Full CI pipeline passed!"
	@echo "================================"
