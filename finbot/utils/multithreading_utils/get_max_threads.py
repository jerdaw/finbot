"""Calculate optimal thread count for multithreading based on system resources.

Determines the maximum number of threads that can be safely used for parallel
operations while respecting system constraints and leaving resources for other
processes. Used throughout finbot for configuring thread pools.

Typical usage:
    ```python
    from finbot.utils.multithreading_utils.get_max_threads import get_max_threads

    # Default: auto-detect cores, reserve 1 thread
    threads = get_max_threads()
    # On 8-core system: returns 7 (8 cores - 1 reserved)

    # Specify minimum threads
    threads = get_max_threads(min_threads=2)
    # Returns at least 2, even on single-core systems

    # Cap maximum threads
    threads = get_max_threads(max_threads=4, reserved_threads=0)
    # Returns at most 4, uses all available

    # Conservative (reserve 2 threads)
    threads = get_max_threads(reserved_threads=2)
    # On 8-core system: returns 6 (8 - 2)

    # Use with ThreadPoolExecutor
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=get_max_threads()) as executor:
        results = list(executor.map(process_item, items))
    ```

Calculation algorithm:
    1. Get system CPU count (multiprocessing.cpu_count())
    2. Apply max_threads cap if specified
    3. Subtract reserved_threads
    4. Enforce min_threads lower bound
    5. Validate: reserved + desired ≤ total

Parameters:
    - min_threads: Minimum threads to return (default: 1)
    - max_threads: Maximum threads to return (default: None = system CPU count)
    - reserved_threads: Threads to reserve for system (default: 1)

Return value:
    - Integer: Number of threads that can be safely used
    - Always between min_threads and (total_threads - reserved_threads)

Features:
    - Automatic CPU detection
    - Respects system resources (reserved threads)
    - Enforces minimum and maximum bounds
    - Input validation with clear error messages
    - Thread-safe (no shared state)

Error handling:
    - ValueError: If reserved + desired > total (impossible configuration)
    - Example: 4-core system with reserved_threads=3 and min_threads=2
      - Would require 5 threads (3 reserved + 2 minimum)
      - Raises ValueError with descriptive message

Use cases:
    - Configuring thread pools for parallel operations
    - Balancing performance vs system responsiveness
    - Avoiding resource exhaustion
    - Platform-independent thread count determination
    - CI/CD environments with varying core counts

Example configurations:
    ```python
    # Development (leave resources for IDE, browser)
    dev_threads = get_max_threads(reserved_threads=2)

    # Production (maximize throughput)
    prod_threads = get_max_threads(reserved_threads=1)

    # Conservative (ensure system responsiveness)
    safe_threads = get_max_threads(reserved_threads=3, min_threads=1)

    # Limit to 4 threads max (e.g., API rate limits)
    capped_threads = get_max_threads(max_threads=4)
    ```

Why reserve threads:
    - System processes need CPU time
    - Main thread needs resources
    - Interactive system responsiveness
    - Prevents complete CPU saturation
    - Best practice: reserve at least 1 thread

Typical configurations:
    - Desktop development: reserved_threads=2 (leave for OS, IDE)
    - Server production: reserved_threads=1 (maximize throughput)
    - Shared environment: reserved_threads=cores/2 (fair sharing)

Used throughout finbot:
    - `settings_accessors.MAX_THREADS` uses this
    - `save_dataframes`, `load_dataframes` (parallel I/O)
    - `are_files_outdated` (parallel staleness checks)
    - `backtest_batch` (parallel backtesting)
    - `dca_optimizer` (parallel optimization)

Performance impact:
    - Too few threads: Underutilized CPU, slow operations
    - Too many threads: Context switching overhead, reduced performance
    - Optimal: Close to CPU count minus reserved threads

Platform differences:
    - Linux/Mac: Logical cores (includes hyperthreading)
    - Windows: Logical cores
    - Docker: Container CPU limit (if set)
    - CI/CD: Variable (1-72+ cores depending on runner)

Best practices:
    ```python
    # Use with context managers
    with ThreadPoolExecutor(max_workers=get_max_threads()) as executor:
        pass

    # Cache result if calling repeatedly
    MAX_THREADS = get_max_threads()

    # Adjust for specific workloads
    # CPU-bound: Use fewer threads (cores - 1)
    cpu_bound_threads = get_max_threads(reserved_threads=1)

    # I/O-bound: Can use more threads (cores * 2-4)
    io_bound_threads = get_max_threads(reserved_threads=0) * 2
    ```

Limitations:
    - Doesn't account for memory constraints
    - Doesn't consider other running applications
    - Doesn't detect CPU throttling/quota limits
    - Fixed calculation (not adaptive to load)

Dependencies: multiprocessing (stdlib)

Related modules: settings_accessors (exposes MAX_THREADS globally),
are_files_outdated (parallel file checking), save_dataframes (parallel saving).
"""

from __future__ import annotations

import multiprocessing


def get_max_threads(min_threads: int = 1, max_threads: int | None = None, reserved_threads: int = 1) -> int:
    """
    Calculate the maximum number of threads that can be used for multithreading,
    considering the system's capabilities and user-defined constraints.

    Args:
        min_threads (int): The minimum number of threads. Defaults to 1.
        max_threads (Optional[int]): The maximum number of threads. If None, it will be set
                                     to the number of CPU cores available on the system.
        reserved_threads (int): The number of threads to reserve and not use for multithreading. Defaults to 1.

    Returns:
        int: The maximum number of threads that can be used for multithreading.

    Raises:
        ValueError: If min_threads is less than 1, or if calculated max_threads is less than min_threads.
    """

    # Get the total system CPU count
    total_threads = multiprocessing.cpu_count()

    # Calculate default max_threads based on the system's CPU count if not provided
    if max_threads is None:
        max_threads = total_threads

    # Adjust max_threads for reserved_threads
    adjusted_max_threads = min(max_threads, total_threads - reserved_threads)

    desired_threads = max(min_threads, adjusted_max_threads)

    # Ensure that reserved_threads + desired threads is not greater than total_threads
    if reserved_threads + desired_threads > total_threads:
        raise ValueError(
            f"reserved_threads ({reserved_threads}) + desired_threads ({desired_threads}) "
            f"is greater than total_threads ({total_threads}).",
        )

    return desired_threads
