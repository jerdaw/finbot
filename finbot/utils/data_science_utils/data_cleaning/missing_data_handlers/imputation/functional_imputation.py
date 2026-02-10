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
