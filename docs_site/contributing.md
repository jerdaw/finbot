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
uv run pre-commit install --hook-type commit-msg

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
- Conventional commit message validation
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

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Commit messages are automatically validated by a pre-commit hook.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**Components:**

- **type** (required): The kind of change
- **scope** (optional): The area of the codebase affected
- **subject** (required): Brief description, max 72 characters
- **body** (optional): Detailed explanation
- **footer** (optional): Breaking changes, issue references

### Commit Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(backtesting): add dual momentum strategy` |
| `fix` | Bug fix | `fix(api): handle rate limit errors in FRED client` |
| `docs` | Documentation only | `docs(readme): update installation instructions` |
| `style` | Code style/formatting | `style: fix trailing whitespace` |
| `refactor` | Code restructuring | `refactor(config): migrate to dynaconf settings` |
| `test` | Add or update tests | `test(simulation): add fund simulator edge cases` |
| `chore` | Maintenance tasks | `chore(deps): update pandas to 2.2.0` |
| `perf` | Performance improvement | `perf(backtesting): optimize batch processing` |
| `ci` | CI/CD changes | `ci: add conventional commit linting` |
| `build` | Build system changes | `build: update python version to 3.12` |
| `revert` | Revert previous commit | `revert: revert "feat: add new strategy"` |

### Common Scopes

Use these scopes to indicate which part of the codebase is affected:

- `api` — API client code
- `cli` — Command-line interface
- `dashboard` — Streamlit dashboard
- `backtesting` — Backtesting engine
- `simulation` — Simulation services
- `optimization` — Portfolio optimizers
- `config` — Configuration management
- `docs` — Documentation
- `deps` — Dependencies
- `tests` — Test suite

### Examples

**Simple feature:**
```
feat(backtesting): add risk parity strategy
```

**Bug fix with details:**
```
fix(simulation): correct leverage calculation in fund simulator

The previous calculation did not account for daily compounding
of fees when leverage > 2x. This fix applies the exponential
fee calculation as documented in the methodology.

Fixes #123
```

**Breaking change:**
```
feat(api)!: change API manager initialization signature

BREAKING CHANGE: APIManager now requires explicit rate limit
configuration instead of using defaults. Update all API manager
instantiations to include rate_limit parameter.
```

**Documentation update:**
```
docs(contributing): add conventional commit guidelines
```

**Dependency update:**
```
chore(deps): update pandas to 2.2.0
```

### Validation

The pre-commit hook automatically validates:

- ✓ Valid commit type from allowed list
- ✓ Subject line ≤ 72 characters
- ✓ Proper format with colon separator
- ✓ Lowercase type

**Invalid examples** (will be rejected):

- `Add new feature` — Missing type
- `fixed bug` — Wrong format, missing colon
- `WIP` — Not conventional format
- `FEAT: add feature` — Type must be lowercase

### Why Conventional Commits?

1. **Automated changelog generation** — Types make it easy to generate release notes
2. **Clear commit history** — Easy to scan and understand changes
3. **Semantic versioning** — Types map to version bumps (feat → minor, fix → patch, BREAKING CHANGE → major)
4. **Better collaboration** — Consistent format across all contributors

### References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [conventional-pre-commit Hook](https://github.com/compilerla/conventional-pre-commit)
- Configuration: See `.commitlintrc.yaml` in repository root

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
