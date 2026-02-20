"""Save multiple DataFrames in parallel using multithreading.

Batch saving of pandas DataFrames with parallel execution for performance.
Uses thread_map for concurrent I/O operations with progress bar.

Wraps save_dataframe.py to save multiple files simultaneously. Particularly
beneficial when saving many files to network storage or slow disks.

Typical usage:
    - Save results from batch backtesting
    - Export multiple time series to files
    - Persist simulation outputs
    - Bulk data export operations
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import thread_map

from finbot.config import settings_accessors
from finbot.utils.pandas_utils.save_dataframe import save_dataframe

MAX_THREADS = settings_accessors.MAX_THREADS


def save_dataframes(
    dataframes: Sequence[pd.DataFrame | pd.Series],
    file_paths: Sequence[Path | str] | None = None,
    save_dir: Path | str | None = None,
    compression: str = "zstd",
    smart_backup: bool = True,
) -> None:
    """
    Save multiple pandas DataFrames or Series to files using multithreading.

    Args:
        dataframes: List of DataFrames or Series to be saved.
        file_paths: Corresponding list of file paths.
        save_dir: Directory to save the files.
        compression: Compression method for the Parquet files.
        smart_backup: If True, creates backups if safety check fails.

    Raises:
        ValueError: If the number of DataFrames/Series doesn't match the number of file paths.
    """
    if file_paths is None and save_dir is None:
        raise ValueError("Either file_paths or save_dir must be provided")

    if file_paths and (len(dataframes) != len(file_paths)):
        raise ValueError(
            "The number of dataframes must match the number of file paths",
        )

    resolved_paths: Sequence[Path | str | None] = [None] * len(dataframes) if file_paths is None else file_paths

    def save_single_df(single_df: pd.DataFrame | pd.Series, single_path: Path | str | None) -> None:
        save_dataframe(
            df=single_df,
            file_path=single_path,
            save_dir=save_dir,
            compression=compression,
            smart_backup=smart_backup,
        )

    list(
        thread_map(
            save_single_df,
            dataframes,
            resolved_paths,
            max_workers=MAX_THREADS,
        ),
    )
