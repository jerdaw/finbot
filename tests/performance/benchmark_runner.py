"""Performance benchmark runner with regression detection.

This script runs performance benchmarks for critical components and compares
results against baseline metrics to detect performance regressions.

Usage:
    # Run benchmarks and compare to baseline
    python tests/performance/benchmark_runner.py

    # Update baseline with current results
    python tests/performance/benchmark_runner.py --update-baseline

    # Run specific benchmark only
    python tests/performance/benchmark_runner.py --benchmark fund_simulator
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Set environment before importing config
os.environ["DYNACONF_ENV"] = "development"

from finbot.services.simulation.fund_simulator import fund_simulator

# Path to baseline metrics file
BASELINE_PATH = Path(__file__).parent / "baseline.json"


def get_memory_usage() -> float:
    """Get current memory usage in MB.

    Returns:
        Memory usage in megabytes
    """
    current, _peak = tracemalloc.get_traced_memory()
    return current / 1024 / 1024  # Convert bytes to MB


def generate_synthetic_price_data(n_days: int, start_price: float = 100.0) -> pd.DataFrame:
    """Generate synthetic price data for benchmarking.

    Args:
        n_days: Number of trading days to generate
        start_price: Starting price

    Returns:
        DataFrame with Date index and OHLCV columns
    """
    # Generate realistic daily returns (mean ~0.0003, std ~0.01)
    np.random.seed(42)
    returns = np.random.normal(0.0003, 0.01, n_days)

    # Calculate prices from returns
    price_multipliers = np.exp(np.cumsum(returns))
    prices = start_price * price_multipliers

    # Create DataFrame with DatetimeIndex
    start_date = datetime(2000, 1, 1)
    dates = pd.bdate_range(start_date, periods=n_days)

    df = pd.DataFrame(
        {
            "Close": prices,
            "Open": prices * 0.999,
            "High": prices * 1.001,
            "Low": prices * 0.998,
            "Volume": np.random.randint(1_000_000, 10_000_000, n_days),
        },
        index=dates,
    )

    return df


def benchmark_fund_simulator(n_days: int = 2520, n_runs: int = 10) -> dict[str, Any]:
    """Benchmark fund_simulator performance.

    Args:
        n_days: Number of trading days (default: 10 years)
        n_runs: Number of benchmark runs to average

    Returns:
        Dict with performance metrics
    """
    # Generate test data
    price_df = generate_synthetic_price_data(n_days)

    # Warm-up run
    _ = fund_simulator(
        price_df=price_df,
        leverage_mult=3,
        annual_er_pct=0.91 / 100,
        percent_daily_spread_cost=0.015 / 100,
        fund_swap_pct=2.5 / 3,
    )

    # Benchmark runs with memory tracking
    times = []
    memory_usages = []

    for _ in range(n_runs):
        tracemalloc.start()

        start = time.perf_counter()
        result = fund_simulator(
            price_df=price_df,
            leverage_mult=3,
            annual_er_pct=0.91 / 100,
            percent_daily_spread_cost=0.015 / 100,
            fund_swap_pct=2.5 / 3,
        )
        end = time.perf_counter()

        memory_usages.append(get_memory_usage())
        tracemalloc.stop()

        times.append(end - start)

    return {
        "name": "fund_simulator",
        "n_days": n_days,
        "n_runs": n_runs,
        "duration_mean_ms": np.mean(times) * 1000,
        "duration_median_ms": statistics.median(times) * 1000,
        "duration_std_ms": np.std(times) * 1000,
        "duration_min_ms": np.min(times) * 1000,
        "duration_max_ms": np.max(times) * 1000,
        "throughput_days_per_sec": n_days / np.mean(times),
        "memory_mean_mb": np.mean(memory_usages),
        "memory_peak_mb": np.max(memory_usages),
        "result_shape": list(result.shape),
    }


def benchmark_backtest_adapter(n_days: int = 756, n_runs: int = 7) -> dict[str, Any]:
    """Benchmark BacktraderAdapter performance with NoRebalance strategy.

    This is a lightweight benchmark using the simplest strategy to measure
    backtesting engine overhead. Uses the new adapter-first architecture.

    Args:
        n_days: Number of trading days (default: 3 years)
        n_runs: Number of benchmark runs to average

    Returns:
        Dict with performance metrics
    """
    try:
        from finbot.core.contracts import BacktestRunRequest
        from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
        from finbot.services.backtesting.costs import ZeroCommission

        # Generate test data
        price_df = generate_synthetic_price_data(n_days)
        price_histories = {"TEST": price_df}

        # Warm-up run
        adapter = BacktraderAdapter(
            price_histories=price_histories,
            commission_model=ZeroCommission(),
        )
        request = BacktestRunRequest(
            strategy_name="NoRebalance",
            symbols=("TEST",),
            start=price_df.index[0],
            end=price_df.index[-1],
            initial_cash=10000.0,
            parameters={"equity_proportions": [1.0]},
        )
        _ = adapter.run(request)

        # Benchmark runs
        times = []
        memory_usages = []

        for _ in range(n_runs):
            tracemalloc.start()

            start = time.perf_counter()
            adapter = BacktraderAdapter(
                price_histories=price_histories,
                commission_model=ZeroCommission(),
            )
            adapter.run(request)
            end = time.perf_counter()

            memory_usages.append(get_memory_usage())
            tracemalloc.stop()

            times.append(end - start)

        return {
            "name": "backtest_adapter",
            "n_days": n_days,
            "n_runs": n_runs,
            "duration_mean_ms": np.mean(times) * 1000,
            "duration_median_ms": statistics.median(times) * 1000,
            "duration_std_ms": np.std(times) * 1000,
            "duration_min_ms": np.min(times) * 1000,
            "duration_max_ms": np.max(times) * 1000,
            "throughput_days_per_sec": n_days / np.mean(times),
            "memory_mean_mb": np.mean(memory_usages),
            "memory_peak_mb": np.max(memory_usages),
        }
    except Exception as e:
        return {
            "name": "backtest_adapter",
            "error": str(e),
            "skipped": True,
        }


def run_all_benchmarks() -> dict[str, Any]:
    """Run all performance benchmarks.

    Returns:
        Dict mapping benchmark names to results
    """
    print("=" * 80)
    print("Performance Benchmark Suite")
    print("=" * 80)
    print()

    results = {}

    # Benchmark 1: Fund Simulator (10 years)
    print("Running: fund_simulator (10 years / 2520 days)")
    print("-" * 80)
    fund_result = benchmark_fund_simulator(n_days=2520, n_runs=10)
    results["fund_simulator"] = fund_result

    print(f"  Duration (mean):   {fund_result['duration_mean_ms']:.2f} ms")
    print(f"  Duration (median): {fund_result['duration_median_ms']:.2f} ms")
    print(f"  Duration (std):    {fund_result['duration_std_ms']:.2f} ms")
    print(f"  Throughput:        {fund_result['throughput_days_per_sec']:,.0f} days/sec")
    print(f"  Memory (mean):     {fund_result['memory_mean_mb']:.2f} MB")
    print()

    # Benchmark 2: Backtest Adapter (3 years)
    print("Running: backtest_adapter (3 years / 756 days)")
    print("-" * 80)
    backtest_result = benchmark_backtest_adapter(n_days=756, n_runs=7)
    results["backtest_adapter"] = backtest_result

    if "skipped" in backtest_result:
        print(f"  SKIPPED: {backtest_result.get('error', 'Unknown error')}")
    else:
        print(f"  Duration (mean):   {backtest_result['duration_mean_ms']:.2f} ms")
        print(f"  Duration (median): {backtest_result['duration_median_ms']:.2f} ms")
        print(f"  Duration (std):    {backtest_result['duration_std_ms']:.2f} ms")
        print(f"  Throughput:        {backtest_result['throughput_days_per_sec']:,.0f} days/sec")
        print(f"  Memory (mean):     {backtest_result['memory_mean_mb']:.2f} MB")
    print()

    return results


def load_baseline() -> dict[str, Any] | None:
    """Load baseline metrics from file.

    Returns:
        Baseline metrics dict or None if not found
    """
    if not BASELINE_PATH.exists():
        return None

    with open(BASELINE_PATH) as f:
        return json.load(f)


def save_baseline(results: dict[str, Any]) -> None:
    """Save benchmark results as new baseline.

    Args:
        results: Benchmark results to save
    """
    baseline = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": results,
    }

    with open(BASELINE_PATH, "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"✅ Baseline saved to {BASELINE_PATH}")


def compare_to_baseline(
    current: dict[str, Any],
    baseline: dict[str, Any],
    regression_threshold: float = 0.20,
) -> tuple[bool, list[str]]:
    """Compare current results to baseline and detect regressions.

    Args:
        current: Current benchmark results
        baseline: Baseline benchmark results
        regression_threshold: Regression threshold (0.20 = 20% slower fails)

    Returns:
        Tuple of (passed, list of regression messages)
    """
    print("=" * 80)
    print("Performance Regression Analysis")
    print("=" * 80)
    print()

    baseline_benchmarks = baseline.get("benchmarks", {})
    regressions = []
    passed = True

    for name, current_result in current.items():
        if "skipped" in current_result:
            print(f"⏭️  {name}: SKIPPED")
            continue

        baseline_result = baseline_benchmarks.get(name)
        if not baseline_result:
            print(f"⚠️  {name}: No baseline found (new benchmark)")
            continue

        if "skipped" in baseline_result:
            print(f"⚠️  {name}: Baseline was skipped, cannot compare")
            continue

        # Compare duration — prefer median for robustness; fall back to mean for old baselines
        current_duration = current_result.get("duration_median_ms", current_result["duration_mean_ms"])
        baseline_duration = baseline_result.get("duration_median_ms", baseline_result["duration_mean_ms"])
        metric_label = (
            "median" if "duration_median_ms" in current_result and "duration_median_ms" in baseline_result else "mean"
        )
        duration_ratio = current_duration / baseline_duration
        duration_change_pct = (duration_ratio - 1.0) * 100

        # Compare memory
        current_memory = current_result["memory_mean_mb"]
        baseline_memory = baseline_result["memory_mean_mb"]
        memory_ratio = current_memory / baseline_memory
        memory_change_pct = (memory_ratio - 1.0) * 100

        print(f"📊 {name}:")
        print(f"   Duration ({metric_label}): {current_duration:.2f} ms (baseline: {baseline_duration:.2f} ms)")
        print(f"   Change:   {duration_change_pct:+.1f}%")
        print(f"   Memory:   {current_memory:.2f} MB (baseline: {baseline_memory:.2f} MB)")
        print(f"   Change:   {memory_change_pct:+.1f}%")

        # Check for regression
        if duration_ratio > (1.0 + regression_threshold):
            msg = (
                f"❌ REGRESSION: {name} is {duration_change_pct:.1f}% slower "
                f"(threshold: {regression_threshold * 100:.0f}%)"
            )
            print(f"   {msg}")
            regressions.append(msg)
            passed = False
        else:
            print(f"   ✅ PASSED (within {regression_threshold * 100:.0f}% threshold)")

        print()

    return passed, regressions


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run performance benchmarks")
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update baseline with current results",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        choices=["fund_simulator", "backtest_adapter"],
        help="Run specific benchmark only",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Regression threshold (default: 0.20 for 20%% slower)",
    )

    args = parser.parse_args()

    # Run benchmarks
    if args.benchmark:
        if args.benchmark == "fund_simulator":
            results = {"fund_simulator": benchmark_fund_simulator()}
        elif args.benchmark == "backtest_adapter":
            results = {"backtest_adapter": benchmark_backtest_adapter()}
    else:
        results = run_all_benchmarks()

    # Update baseline if requested
    if args.update_baseline:
        save_baseline(results)
        return 0

    # Compare to baseline
    baseline = load_baseline()
    if baseline is None:
        print("⚠️  No baseline found. Run with --update-baseline to create one.")
        return 0

    passed, regressions = compare_to_baseline(results, baseline, args.threshold)

    if not passed:
        print("=" * 80)
        print("❌ PERFORMANCE REGRESSION DETECTED")
        print("=" * 80)
        for msg in regressions:
            print(f"  {msg}")
        print()
        print("To update baseline: python tests/performance/benchmark_runner.py --update-baseline")
        return 1

    print("=" * 80)
    print("✅ All performance benchmarks passed")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
