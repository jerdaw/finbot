"""Directional imputation using forward or backward fill methods.

Fills missing values by propagating the last valid observation forward (ffill)
or the next valid observation backward (bfill). These methods are particularly
effective for time series data where values are expected to persist over time.

Typical usage:
    ```python
    # Forward fill (propagate last valid value forward)
    df_filled = directional_imputation(df, method="ffill")

    # Backward fill (propagate next valid value backward)
    df_filled = directional_imputation(df, method="bfill")

    # Forward fill with leading NaN removal
    df_filled = directional_imputation(df, method="ffill", dropna_start=True)

    # In-place modification
    directional_imputation(df, method="ffill", inplace=True)
    ```

Fill methods:
    - 'ffill' (forward fill): Propagate last valid value forward
      - Use when values persist over time (e.g., stock prices, status flags)
      - Cannot fill leading NaN values (no prior value to propagate)

    - 'bfill' (backward fill): Propagate next valid value backward
      - Use when future values inform past (e.g., backfilling survey results)
      - Cannot fill trailing NaN values (no subsequent value to propagate)

Features:
    - Fast and computationally efficient
    - Preserves temporal ordering
    - Optional dropping of leading NaN values (dropna_start)
    - In-place or copy modification
    - Works with both DataFrames and Series

Use cases:
    - Time series with irregular sampling
    - Categorical data where forward/backward fill is logical
    - Status flags that persist until changed
    - Quick preprocessing when statistical methods are inappropriate

Trade-offs:
    - Does not use statistical properties of data
    - Can propagate errors if last valid value is outlier
    - May introduce bias if missingness is systematic
    - Cannot fill all NaN values (leading/trailing depending on method)

Best practices:
    - Combine ffill and bfill to fill all values: df.ffill().bfill()
    - Use dropna_start=True to remove unfillable leading NaN values
    - Consider if temporal persistence assumption is valid for your data

Related modules: time_series_imputation (more sophisticated temporal methods),
functional_imputation (interpolation-based), simple_imputation (statistical).
"""

from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _validate_df_or_series,
    _validate_parameters,
)


def directional_imputation(
    data: pd.DataFrame | pd.Series,
    method: str = "ffill",
    dropna_start: bool = True,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Fill missing values using directional methods ('ffill' or 'bfill').

    Parameters:
        data (Union[pd.DataFrame, pd.Series]): The DataFrame or Series to be filled.
        method (str): The method used to fill missing values. Options: 'ffill', 'bfill'.
        dropna_start (bool): Whether to drop rows with missing values at the start.
        inplace (bool): Whether to modify the input data in-place.

    Returns:
        Union[pd.DataFrame, pd.Series]: DataFrame or Series with missing values filled.
    """
    valid_methods = {"ffill", "bfill"}
    _validate_parameters(method, valid_methods, "Invalid parameters or method for directional_imputation")
    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)

    if method == "ffill":
        data.ffill(inplace=True)
    elif method == "bfill":
        data.bfill(inplace=True)

    if dropna_start:
        data.dropna(inplace=True)

    return data
