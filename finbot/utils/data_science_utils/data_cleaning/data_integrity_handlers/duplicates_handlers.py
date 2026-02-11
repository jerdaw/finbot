"""Detect and remove duplicate rows from pandas DataFrames.

Provides utilities for identifying and eliminating duplicate rows, which can
arise from data collection errors, merging datasets, or repeated observations.
Removing duplicates is a critical data cleaning step to ensure data quality
and prevent bias in analysis.

Typical usage:
    ```python
    # Remove duplicate rows and log count
    df_clean = remove_duplicates(df)
    # Output: "Removed X duplicates"

    # Keep first occurrence (default pandas behavior)
    df_clean = df.drop_duplicates(keep="first")

    # Keep last occurrence
    df_clean = df.drop_duplicates(keep="last")

    # Remove all duplicates (keep none)
    df_clean = df.drop_duplicates(keep=False)
    ```

Duplicate handling:
    - Identifies rows with identical values across all columns
    - Removes duplicate rows while keeping one occurrence
    - Logs number of duplicates removed for audit trail
    - Returns cleaned DataFrame

Features:
    - Automatic duplicate detection
    - Logging of duplicate count
    - Simple wrapper around pandas drop_duplicates
    - Returns copy (does not modify original)

Use cases:
    - Data cleaning before analysis
    - Removing accidentally repeated records
    - Cleaning merged datasets
    - Preventing double-counting in aggregations
    - Data quality reporting

Best practices:
    - Check for duplicates before analysis
    - Investigate why duplicates exist (may indicate data quality issues)
    - Consider subset parameter for partial duplicates (duplicates in specific columns)
    - Document duplicate removal in data cleaning pipeline

Advanced duplicate handling:
    ```python
    # Duplicates based on specific columns only
    df_clean = df.drop_duplicates(subset=["id", "date"], keep="first")

    # Identify duplicates without removing
    duplicates = df[df.duplicated()]

    # Count duplicates per group
    duplicate_counts = df.groupby(df.columns.tolist()).size().reset_index(name="count")
    ```

Related modules: irrelevant_data_handler (remove rows by criteria),
identify_corrupted_data (find data quality issues).
"""

from __future__ import annotations

import pandas as pd

from finbot.config import logger


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.
    """
    original_count = len(data)
    data = data.drop_duplicates()
    logger.info(f"Removed {original_count - len(data)} duplicates")
    return data
