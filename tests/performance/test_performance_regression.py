"""Pytest wrapper for performance regression testing.

This test file wraps the benchmark_runner.py script to integrate
performance regression testing into the pytest test suite.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Set environment before importing finbot modules
os.environ["DYNACONF_ENV"] = "development"

PERF_DIR = Path(__file__).parent
BASELINE_PATH = PERF_DIR / "baseline.json"


@pytest.mark.slow
def test_performance_regression():
    """Test that performance has not regressed beyond acceptable threshold.

    This test runs the benchmark suite inline and compares results to the baseline.
    Fails if any benchmark is >30% slower than baseline (median-based comparison;
    falls back to mean if the baseline predates median tracking).

    Marked as slow — excluded from the default test run via addopts in pyproject.toml.
    Run explicitly with: uv run pytest tests/performance/ -v -m slow
    """
    if not BASELINE_PATH.exists():
        pytest.skip(f"No baseline found at {BASELINE_PATH}. Run benchmark_runner.py --update-baseline first.")

    with open(BASELINE_PATH) as f:
        baseline = json.load(f)

    baseline_benchmarks = baseline.get("benchmarks", {})

    # Import benchmark functions (they live alongside this file)
    sys.path.insert(0, str(PERF_DIR))
    from benchmark_runner import benchmark_backtest_adapter, benchmark_fund_simulator

    regression_threshold = 0.30  # 30% slower triggers failure

    # --- fund_simulator benchmark ---
    fund_result = benchmark_fund_simulator()
    fund_baseline = baseline_benchmarks.get("fund_simulator")
    assert fund_baseline is not None, "fund_simulator baseline missing"

    current_fund = fund_result.get("duration_median_ms", fund_result["duration_mean_ms"])
    baseline_fund = fund_baseline.get("duration_median_ms", fund_baseline["duration_mean_ms"])
    fund_ratio = current_fund / baseline_fund

    assert fund_ratio <= (1.0 + regression_threshold), (
        f"fund_simulator performance regression: "
        f"{current_fund:.2f} ms vs baseline {baseline_fund:.2f} ms "
        f"({(fund_ratio - 1.0) * 100:+.1f}%, threshold: {regression_threshold * 100:.0f}%). "
        f"To update baseline: python {PERF_DIR / 'benchmark_runner.py'} --update-baseline"
    )

    # --- backtest_adapter benchmark ---
    backtest_result = benchmark_backtest_adapter()

    if backtest_result.get("skipped"):
        pytest.skip(f"backtest_adapter benchmark was skipped: {backtest_result.get('error', 'unknown error')}")

    backtest_baseline = baseline_benchmarks.get("backtest_adapter")
    if backtest_baseline is None or backtest_baseline.get("skipped"):
        pytest.skip("backtest_adapter baseline is missing or was previously skipped; cannot compare")

    current_backtest = backtest_result.get("duration_median_ms", backtest_result["duration_mean_ms"])
    baseline_backtest = backtest_baseline.get("duration_median_ms", backtest_baseline["duration_mean_ms"])
    backtest_ratio = current_backtest / baseline_backtest

    assert backtest_ratio <= (1.0 + regression_threshold), (
        f"backtest_adapter performance regression: "
        f"{current_backtest:.2f} ms vs baseline {baseline_backtest:.2f} ms "
        f"({(backtest_ratio - 1.0) * 100:+.1f}%, threshold: {regression_threshold * 100:.0f}%). "
        f"To update baseline: python {PERF_DIR / 'benchmark_runner.py'} --update-baseline"
    )
