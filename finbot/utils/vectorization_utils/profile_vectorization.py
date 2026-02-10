from __future__ import annotations

import time
from collections.abc import Callable

import numpy as np
import pandas as pd


def profile_operation(data: pd.Series | pd.DataFrame, operation: Callable, vectorized_operation: Callable) -> bool:
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
def my_operation(data):
    return [x * 2 for x in data]


def my_vectorized_operation(data):
    return data * 2


data = pd.Series(np.random.randint(0, 100, size=10000))

if profile_operation(data, my_operation, my_vectorized_operation):
    print("Vectorized operation is more efficient.")
else:
    print("Non-vectorized operation is more efficient.")
