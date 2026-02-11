"""Internal utilities for handling missing values in normalization pipelines.

Provides helper functions for filling NaN values before or during normalization/
scaling operations. Supports various fill strategies including forward/backward
fill, interpolation, and constant values.

Typical usage:
    Used internally by scaler and normalizer modules. Generally not called
    directly by end users.

    ```python
    # Forward fill then backward fill (ensures no NaN remain)
    df_filled = _handle_missing_values(df, fillna_option="ffillbfill")

    # Linear interpolation
    df_filled = _handle_missing_values(df, fillna_option="interpolate")

    # Fill with constant value
    df_filled = _handle_missing_values(df, fillna_option=0)
    ```

Fill strategies:
    - 'ffill': Forward fill (propagate last valid value forward)
    - 'bfill': Backward fill (propagate next valid value backward)
    - 'ffillbfill': Forward fill then backward fill (handles leading/trailing NaN)
    - 'bfillffill': Backward fill then forward fill
    - 'interpolate': Linear interpolation between values
    - numeric value: Fill all NaN with specified constant

Features:
    - In-place modification (modifies input DataFrame)
    - Supports all standard pandas filling methods
    - Validation of fillna_option parameter
    - Works with DataFrames (column-wise operation)

Use cases:
    - Preprocessing before scaling/normalization
    - Ensuring no NaN values before transformation
    - Cleaning data for scaler fit operations

Error handling:
    - Raises ValueError for invalid fillna_option
    - Clear error message listing valid options

Relation to other modules:
    - Used by scalers to handle NaN before fitting
    - Complements missing_data_handlers (different use case)
    - Part of internal transformation pipeline

Note: This is an internal utility. For general-purpose missing data handling,
use the more sophisticated modules in missing_data_handlers/ directory.

Related modules: missing_data_handlers/fill_methods (user-facing),
missing_data_handlers/imputation/* (sophisticated methods).
"""

from __future__ import annotations

import pandas as pd


def _handle_missing_values(df: pd.DataFrame, fillna_option: str | float | int) -> pd.DataFrame:
    """
    Handles missing values in the DataFrame based on the specified option.

    Parameters:
        df (pandas.DataFrame): The DataFrame to handle missing values.
        fillna_option (str or numeric): The option to fill missing values.
            Valid options are 'ffill', 'bfill', 'ffill then bfill', 'bfill then ffill',
            'interpolate', or a numeric value.

    Returns:
        pandas.DataFrame: The DataFrame with missing values handled.
    """
    if fillna_option == "ffill":
        df.ffill(inplace=True)
    elif fillna_option == "bfill":
        df.bfill(inplace=True)
    elif fillna_option == "ffillbfill":
        df.ffill(inplace=True)
        df.bfill(inplace=True)
    elif fillna_option == "bfillffill":
        df.bfill(inplace=True)
        df.ffill(inplace=True)
    elif fillna_option == "interpolate":
        df.interpolate(inplace=True)
    elif isinstance(fillna_option, int | float):
        df.fillna(fillna_option, inplace=True)
    else:
        raise ValueError(
            "Invalid fillna_option. Valid options are 'ffill', 'bfill', 'ffillbfill', 'bfillfill', 'interpolate', or a numeric value.",
        )
    return df
