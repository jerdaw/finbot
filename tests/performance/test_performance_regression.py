"""Pytest wrapper for performance regression testing.

This test file wraps the benchmark_runner.py script to integrate
performance regression testing into the pytest test suite.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_performance_regression():
    """Test that performance has not regressed beyond acceptable threshold.

    This test runs the benchmark suite and compares results to the baseline.
    Fails if any benchmark is >20% slower than baseline.
    """
    benchmark_script = Path(__file__).parent / "benchmark_runner.py"

    # Run benchmark script
    result = subprocess.run(
        [sys.executable, str(benchmark_script), "--threshold", "0.20"],
        capture_output=True,
        text=True,
    )

    # Print output for visibility
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Check exit code
    assert result.returncode == 0, (
        f"Performance regression detected. "
        f"See output above for details. "
        f"To update baseline: python {benchmark_script} --update-baseline"
    )
