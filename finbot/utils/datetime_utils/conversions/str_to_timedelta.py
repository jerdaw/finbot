"""Convert pandas frequency strings to Timedelta objects.

Parses pandas-style frequency strings (e.g., 'D', 'W', 'H', '30min') into
pandas.Timedelta objects representing fixed durations.

Useful for converting user-specified frequencies into time offsets. Raises
ValueError for calendar-dependent frequencies (months, years) that can't be
represented as fixed Timedeltas - use str_to_relativedelta.py for those.

Part of the datetime_utils/conversions module for time representation conversions.

Typical usage:
    - Parse user input for time intervals
    - Convert config file frequency settings to Timedelta
    - Support dynamic resampling frequencies
"""

from __future__ import annotations

import pandas as pd


def str_to_timedelta(freq: str, default: pd.Timedelta | None = None) -> pd.Timedelta:
    """
    Converts a frequency string to a pandas Timedelta object.

    Args:
        freq (str): Frequency string (e.g., 'D', 'W', 'M', etc.).
        default (pd.Timedelta | None): Default Timedelta object to return if the frequency is not recognized. Defaults to None.

    Returns:
        pd.Timedelta: Corresponding Timedelta object.

    Raises:
        ValueError: If the frequency does not correspond to a known Timedelta.
    """
    freq = freq.upper()
    if freq in ("S", "SEC", "SECOND"):
        return pd.Timedelta(seconds=1)
    elif freq in ("T", "MIN", "MINUTE"):
        return pd.Timedelta(minutes=1)
    elif freq in ("H", "HR", "HOUR", "HOURLY"):
        return pd.Timedelta(hours=1)
    elif freq in ("D", "DAY", "DAILY"):
        return pd.Timedelta(days=1)
    elif freq in ("W", "WEEK", "WEEKLY"):
        return pd.Timedelta(weeks=1)
    elif freq in ("M", "MO", "MONTH", "MONTHLY"):
        return pd.Timedelta(days=30)  # Approximation for month
    elif freq in ("Q", "QUARTER", "QUARTERLY"):
        return pd.Timedelta(days=91)  # Approximation for quarter
    elif freq in ("A", "Y", "YEAR", "ANNUAL", "ANNUALLY"):
        return pd.Timedelta(days=365)  # Approximation for year
    else:
        if default is not None:
            return default
        raise ValueError(
            "The given frequency does not correspond to a known Timedelta.",
        )
