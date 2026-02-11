"""Seasonal decomposition imputation for time series with seasonal patterns.

Imputes missing values by decomposing time series into trend, seasonal, and
residual components, filling each separately, then reconstructing. Particularly
effective for data with strong seasonal patterns (e.g., daily, weekly, yearly).

Typical usage:
    ```python
    # Additive seasonal imputation with auto-detected frequency
    df_filled = seasonal_decomposition_imputation(df, model="additive")

    # Multiplicative model for data with increasing seasonal variation
    df_filled = seasonal_decomposition_imputation(df, model="multiplicative")

    # Specify seasonal frequency explicitly
    df_filled = seasonal_decomposition_imputation(
        df,
        model="additive",
        freq=12,  # Monthly data with yearly seasonality
    )

    # In-place modification
    seasonal_decomposition_imputation(df, model="additive", freq=7, inplace=True)
    ```

Decomposition models:
    - 'additive': Y = Trend + Seasonal + Residual
      - Use when seasonal variation is constant over time
      - Example: Temperature, retail sales in stable markets

    - 'multiplicative': Y = Trend * Seasonal * Residual
      - Use when seasonal variation increases with trend
      - Example: Exponentially growing sales with seasonality

How it works:
    1. Decompose time series into three components:
       - Trend: Long-term upward/downward movement
       - Seasonal: Repeating short-term cycles
       - Residual: Random noise after removing trend and seasonality
    2. Fill missing values in each component using forward/backward fill
    3. Reconstruct imputed series based on model:
       - Additive: sum components
       - Multiplicative: multiply components

Parameters:
    - model: Decomposition type ('additive' or 'multiplicative')
    - freq: Seasonal period (e.g., 12 for monthly with yearly seasonality)
      - If None, pandas will attempt auto-detection from index frequency
      - Must be positive integer if specified
    - inplace: Modify data in-place or return copy

Features:
    - Preserves seasonal patterns during imputation
    - Handles complex time series structures
    - Automatic or manual frequency specification
    - Forward/backward fill for component NaN values

Use cases:
    - Time series with strong seasonal patterns
    - Economic indicators (GDP, unemployment with seasonal trends)
    - Retail sales data (holiday effects, seasonal demand)
    - Weather/climate data (temperature, rainfall)
    - Web traffic with weekly/daily patterns

Requirements:
    - Sufficient data points for decomposition (typically ≥ 2 full periods)
    - Regular time series index for auto frequency detection
    - Numeric data only

Trade-offs:
    - Requires longer time series (≥ 2 seasonal periods)
    - Computationally more expensive than simple methods
    - Assumes stable seasonal pattern throughout series
    - May not work well with irregular seasonality

Best practices:
    - Ensure time series has DatetimeIndex for auto frequency detection
    - Choose additive vs. multiplicative based on variance pattern
    - Specify freq explicitly if auto-detection fails
    - Combine with other methods if decomposition incomplete

Dependencies: statsmodels (statsmodels.tsa.seasonal.seasonal_decompose)

Related modules: time_series_imputation (simpler time-based methods),
functional_imputation (interpolation without seasonality), mice_imputation
(multivariate imputation).
"""

from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
    _validate_parameters,
)


def seasonal_decomposition_imputation(
    data: pd.DataFrame,
    model: str = "additive",
    freq: int | None = None,
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Perform seasonal decomposition imputation on the given data.

    Seasonal decomposition imputation is a technique used to fill missing values in time series data by decomposing the series into its trend, seasonal, and residual components. The missing values in each component are then filled using forward fill and backward fill methods. Finally, the imputed data is reconstructed by combining the imputed components based on the specified model.

    Parameters:
        data (pd.DataFrame): The input data to be imputed.
        model (str): The type of seasonal decomposition model to use. Options: 'additive', 'multiplicative'.
        freq (int | None): The frequency of the data. Default is None.
        inplace (bool): Whether to perform the imputation in-place. Default is False.

    Returns:
        pd.DataFrame: The imputed data.

    Raises:
        TypeError: If not all columns in the DataFrame are numeric.
    """
    valid_models = {"additive", "multiplicative"}
    _validate_parameters(
        model,
        valid_models,
        "Invalid model for seasonal decomposition. Valid options are 'additive' and 'multiplicative'.",
    )

    if freq is not None and not isinstance(freq, int):
        raise ValueError("Frequency must be a positive integer.")

    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)
    _check_numeric(data)

    decomposed = seasonal_decompose(data, model=model, period=freq)
    trend = decomposed.trend.fillna(method="ffill").fillna(method="bfill")
    seasonal = decomposed.seasonal.fillna(
        method="ffill",
    ).fillna(method="bfill")
    residual = decomposed.resid.fillna(method="ffill").fillna(method="bfill")

    data = trend + seasonal + residual if model == "additive" else trend * seasonal * residual

    return data
