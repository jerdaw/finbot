# Performance Regression Testing

Automated performance regression testing for critical components in finbot.

## Overview

This directory contains the performance benchmark suite that runs in CI to detect performance regressions before they reach production.

**Key Components:**
- `benchmark_runner.py`: Main benchmark script with regression detection
- `baseline.json`: Baseline performance metrics
- `test_performance_regression.py`: Pytest wrapper for integration with test suite

## Quick Start

```bash
# Run benchmarks and compare to baseline
uv run python tests/performance/benchmark_runner.py

# Run benchmarks via pytest
uv run pytest tests/performance/test_performance_regression.py -v

# Update baseline (after intentional performance changes)
uv run python tests/performance/benchmark_runner.py --update-baseline
```

## Benchmarks

### 1. Fund Simulator
**Component:** `finbot.services.simulation.fund_simulator`
**Test Size:** 10 years (2,520 trading days)
**Runs:** 5
**Purpose:** Validate vectorized NumPy performance for leveraged fund simulation

### 2. Backtest Adapter
**Component:** `finbot.services.backtesting.adapters.backtrader_adapter`
**Test Size:** 3 years (756 trading days)
**Runs:** 3
**Purpose:** Validate backtesting engine performance with NoRebalance strategy

## CI Integration

The `performance-regression` job in `.github/workflows/ci.yml` runs on all PRs:

```yaml
- name: Run performance benchmarks
  env:
    DYNACONF_ENV: development
  run: |
    uv run python tests/performance/benchmark_runner.py --threshold 0.20
```

**Regression Threshold:** 20% slower fails the CI check.

## Usage

### Run all benchmarks with regression detection

```bash
uv run python tests/performance/benchmark_runner.py
```

Output:
```
================================================================================
Performance Benchmark Suite
================================================================================

Running: fund_simulator (10 years / 2520 days)
--------------------------------------------------------------------------------
  Duration (mean): 1434.05 ms
  Duration (std):  344.29 ms
  Throughput:      1,757 days/sec
  Memory (mean):   0.05 MB

Running: backtest_adapter (3 years / 756 days)
--------------------------------------------------------------------------------
  Duration (mean): 1524.46 ms
  Duration (std):  261.52 ms
  Throughput:      496 days/sec
  Memory (mean):   0.28 MB

================================================================================
Performance Regression Analysis
================================================================================

📊 fund_simulator:
   Duration: 1434.05 ms (baseline: 1434.05 ms)
   Change:   +0.0%
   Memory:   0.05 MB (baseline: 0.05 MB)
   Change:   +0.0%
   ✅ PASSED (within 20% threshold)

📊 backtest_adapter:
   Duration: 1524.46 ms (baseline: 1524.46 ms)
   Change:   +0.0%
   Memory:   0.28 MB (baseline: 0.28 MB)
   Change:   +0.0%
   ✅ PASSED (within 20% threshold)

================================================================================
✅ All performance benchmarks passed
================================================================================
```

### Run specific benchmark

```bash
# Fund simulator only
uv run python tests/performance/benchmark_runner.py --benchmark fund_simulator

# Backtest adapter only
uv run python tests/performance/benchmark_runner.py --benchmark backtest_adapter
```

### Custom regression threshold

```bash
# Allow up to 30% slower
uv run python tests/performance/benchmark_runner.py --threshold 0.30

# Strict 10% threshold
uv run python tests/performance/benchmark_runner.py --threshold 0.10
```

### Update baseline

**When to update:**
- After intentional performance optimizations
- After architectural changes affecting performance
- When upgrading dependencies that change performance

**How to update:**

1. Run benchmarks to verify current performance:
   ```bash
   uv run python tests/performance/benchmark_runner.py
   ```

2. Update baseline if results are acceptable:
   ```bash
   uv run python tests/performance/benchmark_runner.py --update-baseline
   ```

3. Commit the updated baseline:
   ```bash
   git add tests/performance/baseline.json
   git commit -m "Update performance baseline after [reason]"
   ```

## Baseline Metrics

Current baseline (as of 2026-02-17):

| Benchmark | Duration (mean) | Std Dev | Throughput | Memory (mean) |
|-----------|-----------------|---------|------------|---------------|
| **fund_simulator** | 1434.05 ms | 344.29 ms | 1,757 days/sec | 0.05 MB |
| **backtest_adapter** | 1524.46 ms | 261.52 ms | 496 days/sec | 0.28 MB |

See `baseline.json` for full metrics including min/max times and peak memory.

## Implementation Details

### Memory Tracking

Uses Python's `tracemalloc` module to measure memory allocations:

```python
tracemalloc.start()
# ... run benchmark ...
current, peak = tracemalloc.get_traced_memory()
memory_mb = current / 1024 / 1024
tracemalloc.stop()
```

### Warm-up Runs

First run is discarded to exclude:
- JIT compilation (though we don't use numba/jit)
- Cold cache effects
- One-time initialization overhead

### Synthetic Data

Uses reproducible synthetic price data with fixed seed (42):
- Realistic daily returns: mean ~0.03%, std ~1%
- Business day calendar (no weekends/holidays)
- Consistent across all benchmark runs

### Multiple Runs

Each benchmark runs 3-5 times and reports:
- Mean duration (primary metric)
- Standard deviation (variance indicator)
- Min/max duration (outlier detection)
- Mean and peak memory usage

## Troubleshooting

### No baseline found

```
⚠️  No baseline found. Run with --update-baseline to create one.
```

**Solution:** Create initial baseline:
```bash
uv run python tests/performance/benchmark_runner.py --update-baseline
```

### High variance between runs

If standard deviation is high (>20% of mean):
- Close other applications to reduce system load
- Check for background processes (updates, scans, etc.)
- Ensure consistent Python/NumPy versions
- Run on a quiet system or increase number of runs

### Regression detected

```
❌ REGRESSION: fund_simulator is 35.2% slower (threshold: 20%)
```

**Steps:**
1. Review recent code changes that might affect performance
2. Run benchmarks multiple times to confirm regression
3. Profile the code to identify bottlenecks
4. Fix the regression or update baseline if change is intentional

### Benchmark skipped

```
⚠️  backtest_adapter: SKIPPED
```

**Cause:** Exception during benchmark (e.g., import error, missing data)

**Solution:** Check the error in the baseline.json file and fix the underlying issue.

## See Also

- [Performance Benchmarks Documentation](../../docs/benchmarks.md)
- [CI Configuration](../../.github/workflows/ci.yml)
- [Fund Simulator](../../finbot/services/simulation/fund_simulator.py)
- [Backtest Adapter](../../finbot/services/backtesting/adapters/backtrader_adapter.py)
