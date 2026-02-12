# Contributing to Finbot

Thank you for your interest in contributing to Finbot!

## Quick Start

```bash
# Clone and setup
git clone https://github.com/jerdaw/finbot.git
cd finbot
uv sync
uv run pre-commit install

# Run tests
uv run pytest
```

## Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run checks: `make check && make test`
5. Commit with descriptive message
6. Push and create pull request

## Code Quality

```bash
make lint      # Ruff linting
make format    # Ruff formatting
make type      # Mypy type checking
make test      # Run test suite
```

## Standards

- **Python**: 3.11+
- **Line length**: 120 characters
- **Docstrings**: Google style
- **Type hints**: Required
- **Testing**: Required for new features

## Commit Messages

Follow conventional commit format:
```
type(scope): brief description

Longer description if needed.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

## Questions?

See full documentation: [docs_site/contributing.md](docs_site/contributing.md)
