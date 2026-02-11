from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from tqdm.contrib.concurrent import thread_map

from config import settings_accessors
from finbot.utils.pandas_utils.load_dataframe import load_dataframe

MAX_THREADS = settings_accessors.MAX_THREADS


def load_dataframes(file_paths: Sequence[Path | str]):
    """
    Load multiple DataFrames from Parquet files using multithreading.

    Args:
        file_paths: List of file paths from where DataFrames should be loaded.

    Returns:
        List of DataFrames or Series.
    """
    # Using thread_map from tqdm for progress bar
    return list(thread_map(lambda path: load_dataframe(path), file_paths, max_workers=MAX_THREADS))
