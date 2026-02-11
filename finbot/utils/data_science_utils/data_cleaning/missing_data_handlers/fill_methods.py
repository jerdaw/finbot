"""Simple missing value filling methods for pandas DataFrames and Series.

Provides basic imputation techniques using forward/backward fill and summary
statistics (mean, median, mode). These are computationally efficient methods
suitable for quick data cleaning when sophisticated imputation is not required.

Typical usage:
    ```python
    # Forward fill missing values
    filled_df = fill_missing_values(df, method="ffill")

    # Fill with column means
    filled_df = fill_missing_values(df, method="mean", dropna_start=True)

    # In-place median filling
    fill_missing_values(df, method="median", inplace=True)
    ```

Available fill methods:
    - 'ffill': Forward fill (propagate last valid value)
    - 'bfill': Backward fill (propagate next valid value)
    - 'mean': Fill with column mean
    - 'median': Fill with column median
    - 'mode': Fill with column mode (most frequent value)

Features:
    - Optional dropping of leading NaN values (dropna_start)
    - In-place or copy modification
    - Numeric data validation
    - Works with both DataFrames and Series

For more sophisticated imputation methods (MICE, KNN, iterative), see the
imputation/ subdirectory modules.
"""

from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
    _validate_parameters,
)


def fill_missing_values(
    data: pd.DataFrame | pd.Series,
    method: str = "ffill",
    dropna_start: bool = True,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Fill missing values in a DataFrame or Series using various methods.

    Parameters:
        data (Union[pd.DataFrame, pd.Series]): The DataFrame or Series containing missing values.
        method (str): The method used to fill missing values. Options: 'ffill', 'bfill', 'mean', 'median', 'mode'.
        dropna_start (bool): Whether to drop rows with missing values at the start. Default is True.
        inplace (bool): Whether to modify the input data in-place. Default is False.

    Returns:
        Union[pd.DataFrame, pd.Series]: The DataFrame or Series with missing values filled according to the specified method.
    """
    valid_methods = {"ffill", "bfill", "mean", "median", "mode"}
    _validate_parameters(
        method,
        valid_methods,
        f"Invalid fill method. Valid options are: {', '.join(valid_methods)}",
    )

    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)
    _check_numeric(data)

    if method == "mean":
        data.fillna(data.mean(), inplace=True)
    elif method == "median":
        data.fillna(data.median(), inplace=True)
    elif method == "mode":
        data.fillna(data.mode().iloc[0], inplace=True)
    elif method == "ffill":
        data.ffill(inplace=True)
    elif method == "bfill":
        data.bfill(inplace=True)
    else:
        raise ValueError(
            f"Invalid fill method. Valid options are: {', '.join(valid_methods)}",
        )

    if dropna_start and (isinstance(data, pd.DataFrame | pd.Series)):
        data.dropna(inplace=True)

    return data
