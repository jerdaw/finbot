"""Load pandas DataFrame or Series from parquet files.

Simple loader for parquet files with optional error handling. Validates file
extension and provides informative logging. Returns empty DataFrame instead
of raising when raise_exception=False.

Parquet format benefits:
    - Fast loading compared to CSV
    - Type preservation (no need to specify dtypes)
    - Compressed storage
    - Safer than pickle

Complements save_dataframe.py for data persistence.

Typical usage:
    - Load cached computation results
    - Restore backtest data
    - Read downloaded price histories
    - Load simulation outputs
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import logger


def load_dataframe(file_path: Path | str, raise_exception: bool = True) -> pd.DataFrame:
    """
    Load a DataFrame from a parquet file.

    Args:
        file_path: Path to the '.parquet' file.
        raise_exception: If True, re-raises the exception after logger.

    Returns:
        A loaded DataFrame.

    Raises:
        ValueError: If the file_path does not end with '.parquet'.
        FileNotFoundError: If the specified file is not found.
    """
    file_path = Path(file_path)
    if file_path.suffix != ".parquet":
        raise ValueError("file_name must end with .parquet")

    try:
        logger.info(f"Loading DataFrame or Series from {file_path}...")
        return pd.read_parquet(file_path)
    except FileNotFoundError as e:
        if raise_exception:
            logger.error(f"File not found {file_path}: {e}")
            raise
        logger.warning(f"File not found {file_path}: {e}")
        return pd.DataFrame()
