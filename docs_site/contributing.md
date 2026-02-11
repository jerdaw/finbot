# Contributing to Finbot

Thank you for your interest in contributing to Finbot! This guide will help you get started.

## Development Setup

```bash
# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install with dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

## Code Quality

### Linting and Formatting

```bash
# Run all checks
make check

# Individual checks
make lint      # Ruff linting
make format    # Ruff formatting
make type      # Mypy type checking
make security  # Bandit security scan
```

### Pre-commit Hooks

Automatic hooks run on every commit:
- Trailing whitespace removal
- YAML/JSON/TOML syntax validation
- Python AST validation
- Ruff linting and formatting
- Line ending normalization (LF)

Manual hooks (run on demand):
```bash
uv run pre-commit run --hook-stage manual mypy
uv run pre-commit run --hook-stage manual bandit
```

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
uv run pytest tests/unit/test_finance_utils.py -v
```

## Coding Standards

- **Python version**: 3.11+
- **Line length**: 120 characters
- **Docstrings**: Google style
- **Type hints**: Required for all functions
- **Imports**: Sorted with ruff/isort
- **Code style**: ruff format

## Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Make changes with tests
4. Run `make check` and `make test`
5. Commit with descriptive message
6. Push to your fork
7. Create pull request

## Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

## Adding New Features

### New Utility Functions

1. Add function to appropriate `finbot/utils/` category
2. Add comprehensive docstring (Google style)
3. Add type hints
4. Add unit tests
5. Update category README if needed

### New Strategies

1. Create strategy in `finbot/services/backtesting/strategies/`
2. Inherit from `bt.Strategy`
3. Add comprehensive docstring
4. Add to strategy registry
5. Add tests

### New Simulators

1. Create simulator in `finbot/services/simulation/`
2. Use vectorized NumPy operations
3. Add comprehensive docstring
4. Add validation tests
5. Add performance benchmark

## Documentation

### Module Docstrings

All modules require comprehensive module-level docstrings:

```python
"""Brief one-line description.

Detailed description with:
- Purpose
- Typical usage examples
- Key features
- Use cases
- Performance notes
- Limitations
- Dependencies
- Related modules
"""
```

### API Documentation

Update mkdocs documentation when adding public APIs:

```bash
# Build documentation
uv run mkdocs build

# Serve locally
uv run mkdocs serve
```

## Questions?

- **Documentation**: This site
- **Issues**: [GitHub Issues](https://github.com/jerdaw/finbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jerdaw/finbot/discussions)
