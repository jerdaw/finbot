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
