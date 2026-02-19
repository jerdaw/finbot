# Integration Tests

This directory contains integration tests that verify end-to-end workflows in Finbot. Integration tests complement unit tests by validating that components work together correctly.

## Overview

**Purpose:** Verify that complete workflows execute correctly from start to finish.

**Scope:** Integration tests cover:
- Fund simulation workflows
- Backtest execution and analysis
- Portfolio optimization
- CLI command execution

## Running Integration Tests

### Run All Integration Tests

```bash
# Run all integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest tests/integration/ --cov=finbot --cov-report=html
```

### Run Specific Test Files

```bash
# Fund simulation tests
uv run pytest tests/integration/test_fund_simulation_integration.py -v

# Backtest runner tests
uv run pytest tests/integration/test_backtest_runner_integration.py -v

# DCA optimizer tests
uv run pytest tests/integration/test_dca_optimizer_integration.py -v

# CLI tests
uv run pytest tests/integration/test_cli_integration.py -v
```

### Run By Marker

```bash
# Run only slow tests
uv run pytest tests/integration/ -m slow -v

# Skip slow tests
uv run pytest tests/integration/ -m "not slow" -v
```

## Test Categories

### Fund Simulation Integration Tests
**File:** `test_fund_simulation_integration.py`

Tests complete fund simulation workflows including:
- Basic 1x fund simulation
- 2x and 3x leveraged fund simulation
- Custom LIBOR data integration
- Error handling and validation
- Performance with large datasets

### Backtest Runner Integration Tests
**File:** `test_backtest_runner_integration.py`

Tests end-to-end backtesting including:
- Single-asset backtests
- Multi-asset portfolio backtests
- Strategy execution (NoRebalance, Rebalance)
- Date range and duration parameters
- Trade tracking and value history
- Statistics generation

### DCA Optimizer Integration Tests
**File:** `test_dca_optimizer_integration.py`

Tests portfolio optimization workflows:
- Basic DCA optimization
- Multi-ratio optimization
- Grid search parameter sweeps
- Parallel execution
- Result validation

### CLI Integration Tests
**File:** `test_cli_integration.py`

Tests command-line interface:
- Command execution (simulate, backtest, optimize, status)
- Help and version commands
- Input validation
- Output file generation
- Error handling

## Test Data

Integration tests use synthetic test data generated in `conftest.py`:

- **`sample_spy_data`**: 1 year of synthetic SPY price data
- **`sample_tlt_data`**: 1 year of synthetic TLT bond data
- **`sample_multi_asset_data`**: Multi-asset portfolio data
- **`sample_libor_data`**: Synthetic LIBOR rate data

Test data is:
- **Small**: Fast test execution
- **Deterministic**: Reproducible results (fixed random seeds)
- **Realistic**: Mimics real market behavior

## Writing Integration Tests

### Test Structure

```python
def test_workflow_name(fixture1, fixture2):
    """Test complete workflow from start to finish."""
    # 1. Setup - Get test data
    data = fixture1

    # 2. Execute - Run the workflow
    result = run_workflow(data, param1="value")

    # 3. Validate - Assert expected behavior
    assert isinstance(result, ExpectedType)
    assert result.some_metric > 0
    assert_valid_output(result)  # Use helper functions
```

### Best Practices

1. **Use Fixtures**: Leverage shared fixtures from `conftest.py`
2. **Helper Functions**: Use assertion helpers (`assert_valid_backtest_stats`, etc.)
3. **Clear Names**: Test names should describe the workflow being tested
4. **End-to-End**: Test complete workflows, not isolated functions
5. **Validation**: Verify outputs, side effects, and error handling
6. **Performance**: Mark slow tests with `@pytest.mark.slow`

### Example

```python
def test_complete_backtest_workflow(sample_multi_asset_data):
    """Test end-to-end backtest with multiple assets."""
    # Setup
    runner = BacktestRunner(
        price_histories=sample_multi_asset_data,
        init_cash=100000,
        strat=Rebalance,
        strat_kwargs={"rebal_proportions": (0.6, 0.4)},
        # ... other params
    )

    # Execute
    stats = runner.run_backtest()
    trades = runner.get_trades()

    # Validate
    assert_valid_backtest_stats(stats)
    assert len(trades) > 0  # Rebalancing should generate trades
```

## Fixtures Reference

### Data Fixtures

- **`sample_spy_data`**: pd.DataFrame with 252 days of SPY OHLCV data
- **`sample_tlt_data`**: pd.DataFrame with 252 days of TLT OHLCV data
- **`sample_multi_asset_data`**: dict of {"SPY": df, "TLT": df}
- **`sample_libor_data`**: pd.DataFrame with LIBOR rates

### Utility Fixtures

- **`temp_output_dir`**: Temporary directory for file outputs
- **`integration_fixtures_dir`**: Path to fixtures directory
- **`cli_runner`**: Click CliRunner for CLI tests

### Helper Functions

- **`assert_valid_price_dataframe(df, min_rows)`**: Validate price DataFrame
- **`assert_valid_backtest_stats(stats)`**: Validate backtest statistics
- **`assert_valid_optimization_results(results)`**: Validate optimization results

## Performance Considerations

Integration tests are slower than unit tests (acceptable trade-off for comprehensive validation).

**Guidelines:**
- Keep test data small (1 year max)
- Use `@pytest.mark.slow` for tests >5 seconds
- Run fast tests in CI, slow tests periodically
- Consider parallel execution with `pytest-xdist`

**Execution Times (approximate):**
- Fund simulation tests: ~5 seconds
- Backtest runner tests: ~10 seconds
- DCA optimizer tests: ~15 seconds
- CLI tests: ~3 seconds

## CI Integration

Integration tests run in CI on every PR:

```yaml
# .github/workflows/ci.yml
- name: Run integration tests
  run: uv run pytest tests/integration/ -m "not slow" -v
```

Slow tests run on a schedule or manually.

## Troubleshooting

### Tests Fail Intermittently
- Check for non-deterministic behavior
- Verify random seeds are set
- Look for timing-dependent assertions

### Tests Are Too Slow
- Reduce test data size
- Mark slow tests with `@pytest.mark.slow`
- Use parallel execution: `pytest -n auto`

### Import Errors
- Ensure `DYNACONF_ENV=development` is set
- Check that test fixtures are properly imported
- Verify circular import issues are resolved

## See Also

- **Unit Tests**: `tests/unit/` - Fast, isolated component tests
- **Fixtures**: `tests/fixtures/` - Shared test data
- **Contributing Guide**: `CONTRIBUTING.md` - Development guidelines
