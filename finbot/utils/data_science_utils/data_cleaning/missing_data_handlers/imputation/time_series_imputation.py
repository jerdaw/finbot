"""Time-aware interpolation for time series data with DatetimeIndex.

Imputes missing values using time-based interpolation that accounts for
irregular time spacing. Unlike linear interpolation which treats indices as
evenly spaced, this method uses actual time distances between observations.

Typical usage:
    ```python
    # Forward time interpolation (default)
    series_filled = time_series_imputation(series, limit_direction="forward")

    # Backward time interpolation
    series_filled = time_series_imputation(series, limit_direction="backward")

    # Bidirectional time interpolation
    series_filled = time_series_imputation(series, limit_direction="both")

    # In-place modification
    time_series_imputation(series, limit_direction="forward", inplace=True)
    ```

Time interpolation vs linear interpolation:
    - Linear: Assumes equal spacing between indices (ignores actual time gaps)
    - Time: Weights by actual time differences (accounts for irregular sampling)

    Example with irregular spacing:
        Index:  [0h, 1h, 5h]  (uneven time gaps)
        Values: [10, 20, ?]

        Linear interpolation: Treats 5h as "index 2" → interpolates as if evenly spaced
        Time interpolation: Uses actual 4-hour gap → produces different value

Fill directions:
    - 'forward': Fill forward in time (cannot fill leading NaN)
    - 'backward': Fill backward in time (cannot fill trailing NaN)
    - 'both': Fill in both directions (fills more values)

Features:
    - Time-aware interpolation using pandas DatetimeIndex
    - Accounts for irregular sampling intervals
    - Directional control over fill strategy
    - In-place or copy modification
    - Numeric data validation

Use cases:
    - Time series with irregular sampling (sensor data, user events)
    - Financial data with gaps (weekends, holidays, trading halts)
    - IoT sensor readings with variable intervals
    - Log files with irregular event timestamps

Requirements:
    - Series must have DatetimeIndex for time-based interpolation
    - Data must be numeric
    - At least two non-NaN values needed for interpolation

Trade-offs:
    - More accurate than linear for irregular time series
    - Requires DatetimeIndex (more restrictive than linear)
    - Cannot extrapolate beyond data range (leading/trailing NaN may remain)
    - Assumes smooth transition between time points

Best practices:
    - Use 'both' direction to maximize filled values
    - Verify DatetimeIndex is properly formatted before calling
    - Combine with directional fill to handle leading/trailing NaN values
    - Consider seasonal patterns if present (see seasonal_imputation)

Error handling:
    - TypeError if data is not pd.Series
    - ValueError for invalid limit_direction
    - Numeric validation via _check_numeric

Related modules: functional_imputation (various interpolation methods),
directional_imputation (simpler forward/backward fill), seasonal_imputation
(handles seasonal patterns).
"""

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
