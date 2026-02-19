# Updating the Performance Baseline

**Created:** 2026-02-17
**Last Updated:** 2026-02-17

This guide explains when and how to update the performance regression testing baseline.

## When to Update the Baseline

Update the performance baseline in these situations:

### ✅ Valid Reasons to Update

1. **Performance Optimizations**
   - Vectorization improvements
   - Algorithm optimizations
   - Dependency upgrades that improve performance
   - **Example:** "Update baseline after switching to faster NumPy BLAS"

2. **Architectural Changes**
   - Migration to new backtesting adapter (e.g., adapter-first architecture)
   - Refactoring that changes performance characteristics
   - **Example:** "Update baseline after adopting BacktraderAdapter"

3. **Dependency Upgrades**
   - Major Python version upgrade (e.g., 3.11 → 3.13)
   - Major library upgrades (NumPy, pandas, backtrader)
   - **Example:** "Update baseline after upgrading to pandas 2.2"

4. **Benchmark Configuration Changes**
   - Changing test data size (e.g., 5 years → 10 years)
   - Adding new benchmarks
   - **Example:** "Update baseline after increasing fund_simulator test to 10 years"

### ❌ Invalid Reasons to Update

1. **Covering Up Regressions**
   - "CI is failing so I'll just update the baseline"
   - "Performance got worse but I don't want to fix it"

2. **System Variance**
   - "It's slower on my laptop"
   - "It's faster on the CI runner"
   - Use consistent hardware or expect variance

3. **One-time Anomalies**
   - Single slow run due to system load
   - Outliers should be investigated, not ignored

## How to Update the Baseline

### Prerequisites

1. **Verify Performance Change is Intentional**
   ```bash
   # Run benchmarks to see current performance
   uv run python tests/performance/benchmark_runner.py
   ```

2. **Review the Changes**
   - Check what code changes led to the performance difference
   - Ensure the change is expected and documented
   - Consider whether the regression can be mitigated

3. **Run Multiple Times**
   ```bash
   # Run 3 times to ensure consistency
   for i in {1..3}; do
       echo "Run $i:"
       uv run python tests/performance/benchmark_runner.py --benchmark fund_simulator
   done
   ```

### Update Procedure

1. **Update the baseline:**
   ```bash
   uv run python tests/performance/benchmark_runner.py --update-baseline
   ```

2. **Verify the new baseline:**
   ```bash
   # Should pass with ~0% change
   uv run python tests/performance/benchmark_runner.py
   ```

3. **Commit with clear message:**
   ```bash
   git add tests/performance/baseline.json
   git commit -m "Update performance baseline after [specific reason]

   - fund_simulator: [explain change]
   - backtest_adapter: [explain change]

   Justification: [why this change is acceptable]
   "
   ```

### Commit Message Examples

#### Good Commit Messages

```
Update performance baseline after NumPy vectorization optimization

- fund_simulator: 30% faster (500ms → 350ms)
- backtest_adapter: No change

Justification: Replaced loop-based calculation with vectorized NumPy
operations in fund_simulator.py, improving throughput to 7,200 days/sec.
```

```
Update performance baseline after Python 3.13 upgrade

- fund_simulator: 5% slower (due to new GIL implementation)
- backtest_adapter: 3% slower (same reason)

Justification: Python 3.13's new GIL adds slight overhead but provides
better thread safety. Trade-off is acceptable for long-term maintainability.
```

```
Update performance baseline after adopting BacktraderAdapter

- backtest_adapter: Renamed from backtest_runner
- Metrics remain similar (~1500ms for 3 years)

Justification: Migrating to adapter-first architecture (ADR-005).
Performance is equivalent to legacy BacktestRunner.
```

#### Bad Commit Messages (Don't Do This)

```
Update baseline

[No explanation of what changed or why]
```

```
Fix CI

[Implies updating baseline to make tests pass without justification]
```

```
Update performance baseline after refactoring

[Vague reason, no specific metrics or justification]
```

## What Gets Updated

The `tests/performance/baseline.json` file contains:

```json
{
  "timestamp": "2026-02-17T00:01:15.075131",
  "benchmarks": {
    "fund_simulator": {
      "name": "fund_simulator",
      "n_days": 2520,
      "n_runs": 5,
      "duration_mean_ms": 1434.05,
      "duration_std_ms": 344.29,
      "duration_min_ms": 1067.58,
      "duration_max_ms": 1953.78,
      "throughput_days_per_sec": 1757.26,
      "memory_mean_mb": 0.05,
      "memory_peak_mb": 0.05,
      "result_shape": [2520, 2]
    },
    "backtest_adapter": {
      "name": "backtest_adapter",
      "n_days": 756,
      "n_runs": 3,
      "duration_mean_ms": 1524.46,
      "duration_std_ms": 261.52,
      "duration_min_ms": 1185.24,
      "duration_max_ms": 1821.67,
      "throughput_days_per_sec": 495.91,
      "memory_mean_mb": 0.28,
      "memory_peak_mb": 0.28
    }
  }
}
```

**Key Metrics:**
- `duration_mean_ms`: Primary performance metric
- `throughput_days_per_sec`: Processing rate
- `memory_mean_mb`: Memory usage (mean)
- `memory_peak_mb`: Memory usage (peak)

## Baseline History

Track major baseline updates in this section for historical reference.

### 2026-02-17: Initial Baseline
- **fund_simulator:** 1434ms (1,757 days/sec)
- **backtest_adapter:** 1524ms (496 days/sec)
- **Platform:** Linux WSL2, Python 3.13
- **Reason:** Initial implementation of performance regression testing (Priority 5 Item 33)

### Future Updates
Add entries here when updating the baseline, following this format:

```
### YYYY-MM-DD: [Brief Description]
- **fund_simulator:** [duration] ([throughput])
- **backtest_adapter:** [duration] ([throughput])
- **Platform:** [OS, Python version]
- **Reason:** [Why the baseline was updated]
- **Reference:** [PR number or commit hash]
```

## Monitoring Baseline Changes

### PR Review Checklist

When reviewing PRs that update the baseline:

- [ ] Commit message explains what changed and why
- [ ] Performance change is intentional and documented
- [ ] Change is acceptable (optimization or necessary trade-off)
- [ ] Baseline metrics are reasonable (not wildly different)
- [ ] Code changes support the performance change claim
- [ ] Alternative approaches were considered (if regression)

### Red Flags

Watch for these signs of improper baseline updates:

- 🚩 No explanation in commit message
- 🚩 "Fix CI" or "Update baseline" without context
- 🚩 Large regression (>50% slower) without justification
- 🚩 Frequent baseline updates (should be rare)
- 🚩 Baseline updated without code changes
- 🚩 Memory usage dramatically increased (>2x)

## Regression Threshold

**Current Threshold:** 20% slower

The 20% threshold is a balance between:
- **Strictness:** Catches meaningful regressions
- **Flexibility:** Allows for system variance and minor changes

### Adjusting the Threshold

The threshold can be adjusted per-run:

```bash
# Stricter threshold (10%)
uv run python tests/performance/benchmark_runner.py --threshold 0.10

# More lenient (30%)
uv run python tests/performance/benchmark_runner.py --threshold 0.30
```

**Do not adjust the CI threshold (20%) without team discussion.**

## Best Practices

1. **Update Infrequently**
   - Baseline should be stable
   - Updates should be rare and well-justified
   - Aim for <5 updates per year

2. **Document Everything**
   - Clear commit messages
   - Update this guide's history section
   - Add comments in code if relevant

3. **Consider Alternatives First**
   - Can the regression be fixed?
   - Is there a performance optimization to be made?
   - Can the change be staged differently?

4. **Run Multiple Times**
   - Ensure consistency
   - Account for system variance
   - Verify the change is real

5. **Update Documentation**
   - Update `docs/benchmarks.md` if metrics change significantly
   - Update README files if benchmark configuration changes
   - Add notes to ADRs if architectural change

## Troubleshooting

### "No baseline found" Error

**Symptom:**
```
⚠️  No baseline found. Run with --update-baseline to create one.
```

**Cause:** `tests/performance/baseline.json` doesn't exist

**Solution:**
```bash
uv run python tests/performance/benchmark_runner.py --update-baseline
```

### High Variance in Results

**Symptom:** Standard deviation is >20% of mean

**Causes:**
- System load (other processes running)
- Thermal throttling
- Background updates
- Inconsistent Python/NumPy builds

**Solutions:**
- Close other applications
- Run on a quiet system
- Increase number of runs in benchmark script
- Use consistent environment (same Python/NumPy versions)

### Baseline Seems Wrong

**Symptom:** Baseline metrics don't match current performance

**Causes:**
- Baseline from different hardware
- Baseline from different Python version
- Baseline corrupted

**Solution:**
```bash
# Regenerate baseline on current system
uv run python tests/performance/benchmark_runner.py --update-baseline
```

## See Also

- [Performance Benchmarks Documentation](../benchmarks.md)
- [Performance Testing README](../../tests/performance/README.md)
- [CI Configuration](../../.github/workflows/ci.yml)
- [ADR-005: Backtesting Live-Readiness Transition](../adr/ADR-005-backtesting-live-readiness-transition.md)
