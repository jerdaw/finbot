# Benchmarks

Performance benchmarksfor key finbot components.

## Available Benchmarks

| Script | Component | Purpose |
|--------|-----------|---------|
| `benchmark_fund_simulator.py` | Fund Simulator | Measure vectorized NumPy performance |
| `benchmark_dca_optimizer.py` | DCA Optimizer | Measure multiprocessing efficiency |

## Running Benchmarks

```bash
# Set environment
export DYNACONF_ENV=development

# Run individual benchmarks
uv run python benchmarks/benchmark_fund_simulator.py
uv run python benchmarks/benchmark_dca_optimizer.py
```

## Results

See [docs/benchmarks.md](../docs/benchmarks.md) for detailed results and analysis.

## Adding New Benchmarks

When adding a new benchmark script:

1. **Use consistent structure:**
   ```python
   def generate_synthetic_data(size: int) -> pd.DataFrame:
       """Generate test data."""
       pass

   def benchmark_function(size: int, n_runs: int = 5) -> dict:
       """Run benchmark with timing."""
       pass

   def run_benchmarks():
       """Run all benchmark configurations."""
       pass
   ```

2. **Include:**
   - Multiple data sizes (small, medium, large)
   - Multiple runs (5+) for statistical validity
   - Warm-up run to exclude cold start
   - Fixed random seed for reproducibility

3. **Report:**
   - Mean, std, min, max times
   - Throughput (items/second)
   - Scaling characteristics
   - System environment

4. **Document:**
   - Update [docs/benchmarks.md](../docs/benchmarks.md) with results
   - Include interpretation and recommendations
