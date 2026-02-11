"""Interpolation-based imputation using various functional methods.

Fills missing values by fitting smooth curves through existing data points.
Supports linear, polynomial, spline, quadratic, and cubic interpolation methods.
Particularly effective for time series and continuous data with smooth trends.

Typical usage:
    ```python
    # Linear interpolation (default)
    df_filled = interpolate_data(df, method="linear")

    # Quadratic interpolation for smoother curves
    df_filled = interpolate_data(df, method="quadratic")

    # Polynomial interpolation with custom order
    df_filled = interpolate_data(df, method="polynomial", order=3)

    # Cubic spline interpolation
    df_filled = interpolate_data(df, method="cubic")

    # In-place modification
    interpolate_data(df, method="linear", inplace=True)
    ```

Interpolation methods:
    - 'linear': Straight line between points (default)
      - Fast, simple, no overfitting
      - Best for data with linear trends

    - 'quadratic': Second-degree polynomial curve
      - Smoother than linear, fits parabolic patterns
      - Shorthand for polynomial with order=2

    - 'cubic': Third-degree polynomial curve
      - Very smooth, fits S-curves and inflection points
      - Shorthand for polynomial with order=3

    - 'polynomial': Nth-degree polynomial (requires order parameter)
      - Flexible curve fitting
      - Higher order = smoother but more overfitting risk

    - 'spline': Piecewise cubic polynomial
      - Smoothest interpolation
      - Good for irregular spacing

Features:
    - Multiple interpolation methods for different data patterns
    - Column-wise interpolation for DataFrames
    - Automatic numeric validation
    - In-place or copy modification
    - Works with both DataFrames and Series

Use cases:
    - Time series with irregular missing patterns
    - Continuous numerical data with smooth trends
    - Sensor data with occasional dropouts
    - Financial time series (prices, returns)
    - Environmental measurements with gaps

Trade-offs:
    - Assumes smooth underlying function (may not fit discontinuous data)
    - Cannot extrapolate beyond data range (leading/trailing NaN remain)
    - Higher-order methods risk overfitting with sparse data
    - Requires sufficient surrounding points for accurate interpolation

Best practices:
    - Start with linear, increase complexity only if needed
    - Avoid high-order polynomials (order > 5) to prevent overfitting
    - Check if data has discontinuities before applying smooth methods
    - Combine with directional fill to handle leading/trailing NaN values

Error handling:
    - ValueError for invalid method or missing order parameter
    - TypeError for non-numeric data
    - Validates method against allowed options

Related modules: time_series_imputation (time-aware interpolation),
directional_imputation (simpler forward/backward fill), seasonal_imputation
(handles seasonality).
"""

from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
    _validate_parameters,
)


def _apply_interpolation(data, method, order=None):
    if method == "quadratic":
        return data.interpolate(method="polynomial", order=2)
    elif method == "cubic":
        return data.interpolate(method="polynomial", order=3)
    else:
        return data.interpolate(method=method, order=order)


def interpolate_data(data, method="linear", order=None, inplace=False):
    """
    Interpolates missing values in a DataFrame or Series using various methods.

    Parameters:
        data (pd.DataFrame or pd.Series): The data with missing values.
        method (str): Interpolation method - 'linear', 'polynomial', 'spline', 'quadratic', 'cubic'.
        order (int): The order for 'polynomial' interpolation. Required if method is 'polynomial'.
        inplace (bool): Whether to perform interpolation in-place. Default is False.

    Returns:
        pd.DataFrame or pd.Series: Data with missing values interpolated.

    Raises:
        ValueError: For invalid 'method' or if 'order' not specified when required.
        TypeError: If data is not all numeric.
    """
    valid_methods = {"linear", "polynomial", "spline", "quadratic", "cubic"}
    _validate_parameters(
        method,
        valid_methods,
        "Invalid interpolation method. Valid options: " + ", ".join(valid_methods),
    )

    if method == "polynomial" and (order is None or order < 1):
        raise ValueError(
            "Order must be specified and greater than 0 for polynomial interpolation.",
        )

    _validate_df_or_series(data)
    _check_numeric(data)

    if not inplace:
        data = data.copy()

    if isinstance(data, pd.Series):
        return _apply_interpolation(data, method, order)
    else:  # DataFrame
        for col in data.columns:
            data[col] = _apply_interpolation(data[col], method, order)

        return data
