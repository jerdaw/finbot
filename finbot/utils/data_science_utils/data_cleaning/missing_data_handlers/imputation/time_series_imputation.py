from __future__ import annotations

from typing import Literal

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
    _validate_parameters,
)


def time_series_imputation(
    data: pd.Series,
    limit_direction: Literal["forward", "backward", "both"] = "forward",
    inplace: bool = False,
) -> pd.Series:
    """
    Imputes missing values in a time series using time-based interpolation.

    Parameters:
        data (pd.Series): The time series data with missing values.
        limit_direction (str): Direction for filling missing values, either 'forward' or 'backward'. Defaults to 'forward'.
        inplace (bool): If True, modifies the data in-place. Defaults to False.

    Returns:
        pd.Series: Time series with imputed values.

    Raises:
        TypeError: If 'data' is not a pandas Series.
        ValueError: If 'limit_direction' is invalid.
    """
    if not isinstance(data, pd.Series):
        raise TypeError("The 'data' parameter must be a pandas Series.")

    valid_directions = {"forward", "backward"}
    _validate_parameters(
        limit_direction,
        valid_directions,
        f"Invalid limit_direction. Valid options are {valid_directions}.",
    )

    if not inplace:
        data = data.copy()

    _validate_df_or_series(data)
    _check_numeric(data)

    data.interpolate(
        method="time",
        limit_direction=limit_direction,
        inplace=True,
    )

    return data
