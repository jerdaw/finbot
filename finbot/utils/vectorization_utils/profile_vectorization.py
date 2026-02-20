"""Benchmark vectorized vs non-vectorized operations to guide optimization.

Dynamically profiles operations on sample data to determine whether vectorization
provides performance benefits. Useful for making data-driven decisions about
when to vectorize operations.

Typical usage:
    ```python
    import numpy as np
    import pandas as pd
    from finbot.utils.vectorization_utils.profile_vectorization import profile_operation


    # Define operations
    def loop_operation(data):
        return [x * 2 for x in data]


    def vectorized_operation(data):
        return data * 2


    # Profile on your data
    data = pd.Series(np.random.randint(0, 100, size=10000))
    if profile_operation(data, loop_operation, vectorized_operation):
        print("Use vectorized version")
        result = vectorized_operation(data)
    else:
        print("Use loop version")
        result = loop_operation(data)
    ```

How it works:
    1. Samples data (min of 100 rows or full data)
    2. Times non-vectorized operation
    3. Times vectorized operation
    4. Returns True if vectorized is faster

Sample size:
    - Uses min(100, len(data)) rows
    - Enough for timing comparison
    - Not full data (faster profiling)
    - Adjustable by modifying sample size in code

Use cases:
    - Deciding whether to vectorize custom operations
    - Performance optimization guidance
    - Adaptive algorithm selection
    - Educational/demonstration purposes
    - When unsure if vectorization helps

Example decision workflow:
    ```python
    def process_data(data, force_vectorize=None):
        def slow_op(d):
            return [complex_calculation(x) for x in d]

        def fast_op(d):
            return np.vectorize(complex_calculation)(d)

        if force_vectorize is None:
            # Auto-decide based on profiling
            use_vectorized = profile_operation(data, slow_op, fast_op)
        else:
            use_vectorized = force_vectorize

        return fast_op(data) if use_vectorized else slow_op(data)
    ```

When vectorization helps:
    - Simple arithmetic operations
    - NumPy/pandas operations on arrays
    - Element-wise transformations
    - Large datasets (>1000 elements)

When vectorization doesn't help:
    - Complex per-element logic
    - Operations with conditionals
    - Function calls that aren't vectorizable
    - Small datasets (<100 elements)

Example scenarios:
    ```python
    # Scenario 1: Simple arithmetic (vectorized wins)
    data = pd.Series(range(10000))
    loop_op = lambda d: [x**2 for x in d]
    vec_op = lambda d: d**2
    profile_operation(data, loop_op, vec_op)  # Returns True


    # Scenario 2: Complex function (may not help)
    def complex_calc(x):
        if x > 0:
            return math.log(x)
        return 0


    loop_op = lambda d: [complex_calc(x) for x in d]
    vec_op = lambda d: np.vectorize(complex_calc)(d)
    profile_operation(data, loop_op, vec_op)  # May return False
    ```

Performance characteristics:
    - Profiling overhead: ~0.01 seconds
    - Sample-based (fast even for large data)
    - Single run (no warm-up, no averaging)
    - Timing includes function call overhead

Limitations:
    - Single sample (no statistical significance)
    - No warm-up runs (JIT compilation not considered)
    - Sample may not be representative
    - Doesn't account for memory usage
    - Timing granularity (time.time() precision)

Improvements for production use:
    ```python
    # Add multiple runs for statistical significance
    # Add warm-up runs for JIT-compiled operations
    # Use timeit for more accurate timing
    # Profile on full data, not just sample
    # Consider memory usage in addition to speed
    ```

Why this exists:
    - Educational tool for understanding vectorization
    - Quick profiling for optimization decisions
    - Demonstrates performance differences
    - Helps identify vectorization opportunities

Real-world usage note:
    In production finbot code, vectorization decisions are typically made
    upfront based on operation type rather than dynamic profiling. This
    utility is more useful for experimentation and optimization work.

Dependencies: numpy, pandas, time

Related modules: fund_simulator (uses vectorized numpy throughout),
data_science_utils (vectorized operations), dca_optimizer (multiprocessing
instead of vectorization).
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from typing import Any

import numpy as np
import pandas as pd


def profile_operation(
    data: pd.Series | pd.DataFrame,
    operation: Callable[[pd.Series | pd.DataFrame], object],
    vectorized_operation: Callable[[pd.Series | pd.DataFrame], object],
) -> bool:
    """
    Dynamically profile an operation on a sample of data to decide if vectorization is beneficial.

    Parameters:
    data (Union[pd.Series, pd.DataFrame]): The data to be profiled.
    operation (Callable): The non-vectorized version of the operation.
    vectorized_operation (Callable): The vectorized version of the operation.

    Returns:
    bool: True if vectorized operation is faster, False otherwise.
    """
    # Sample data - can be adjusted based on data size and diversity
    sample = data.sample(min(100, len(data)))

    # Measure performance of non-vectorized operation
    start_time = time.time()
    operation(sample)
    non_vectorized_time = time.time() - start_time

    # Measure performance of vectorized operation
    start_time = time.time()
    vectorized_operation(sample)
    vectorized_time = time.time() - start_time

    # Return True if vectorized operation is faster
    return vectorized_time < non_vectorized_time


# Example usage
def my_operation(data: pd.Series | pd.DataFrame) -> list[object]:
    iterable: Iterable[Any] = data.to_numpy().ravel() if isinstance(data, pd.DataFrame) else data
    return [x * 2 for x in iterable]


def my_vectorized_operation(data: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return data * 2


if __name__ == "__main__":
    data = pd.Series(np.random.randint(0, 100, size=10000))
    if profile_operation(data, my_operation, my_vectorized_operation):
        print("Vectorized operation is more efficient.")
    else:
        print("Non-vectorized operation is more efficient.")
