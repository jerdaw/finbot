"""Simple function execution timer using perf_counter.

Measures wall-clock execution time of a function. Uses time.perf_counter()
for high-resolution timing suitable for performance measurement.

Simple utility for quick timing measurements. For more sophisticated timing,
consider using Python's timeit module or a profiler.

Typical usage:
    - Quick performance checks during development
    - Benchmark simple operations
    - Log execution times for monitoring
"""

import time
from collections.abc import Callable


def measure_execution_time(func: Callable[[], object]) -> float:
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    return end_time - start_time
