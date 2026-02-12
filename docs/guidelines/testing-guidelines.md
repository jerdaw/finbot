# Testing Guidelines

Standards for writing and maintaining tests.

## Test Structure

```
tests/
  unit/           # Fast, isolated unit tests
  integration/    # End-to-end tests (future)
```

## Running Tests

```bash
uv run pytest tests/ -v               # All tests
uv run pytest tests/unit/ -v          # Unit tests only
uv run pytest -k test_pattern         # Tests matching pattern
uv run pytest --cov=finbot tests/     # With coverage
```

## Test File Naming

- `test_<module_name>.py` for module-specific tests
- `test_<module_name>_e2e.py` for end-to-end tests of a module
- `test_imports.py` for import smoke tests

## Writing Tests

### Import Smoke Tests

Every new module should have an import smoke test in `test_imports.py`:

```python
def test_import_my_module():
    from finbot.services.my_module import MyClass
    assert MyClass is not None
```

### Unit Tests

Use pytest classes to group related tests:

```python
class TestMyFunction:
    def test_basic_case(self):
        result = my_function(valid_input)
        assert result == expected

    def test_edge_case(self):
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Fixtures

Use `@pytest.fixture()` for shared test setup. Prefer function-scoped fixtures unless setup is expensive.

### Parametrized Tests

Use `@pytest.mark.parametrize` when testing the same logic with multiple inputs.

## What to Test

| Component | What to Test |
|---|---|
| Data classes | Defaults, immutability, field validation |
| Simulators | Output shapes, key presence, reproducibility (seed), edge cases |
| Strategies | Runs without error, value stays positive, expected metrics present |
| Optimizers | Result shape/columns, sorting, parameter scaling |
| Utilities | Correctness, edge cases, error handling |

## Coverage

- Current threshold: 30% (configured in CI)
- Target: increase as more tests are added
- Check coverage: `uv run pytest --cov=finbot --cov-report=term-missing tests/`

## CI Integration

Tests run automatically on push/PR to main via GitHub Actions. The CI workflow runs:
1. Ruff lint check
2. Ruff format check
3. Pytest with coverage reporting

## Avoiding Flaky Tests

- Use fixed random seeds for any stochastic tests
- Use `pytest.approx()` for floating-point comparisons
- Avoid depending on external APIs or network access in unit tests
- Mock external dependencies when needed
