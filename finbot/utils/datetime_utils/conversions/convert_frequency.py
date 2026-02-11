"""Convert frequency strings to timedelta or relativedelta objects.

Unified interface for converting pandas-style frequency strings (e.g., 'D', 'W',
'M', 'Y') into either timedelta (fixed duration) or relativedelta (calendar-aware
duration) objects.

This is the dispatcher function that routes to the appropriate converter:
    - str_to_timedelta: For fixed-duration frequencies (days, hours, etc.)
    - str_to_relativedelta: For calendar-aware frequencies (months, years)

Typical usage:
    - Parse user-specified frequencies in backtesting
    - Convert between different time representation systems
    - Handle both fixed and variable-length periods uniformly
"""

from __future__ import annotations

import pandas as pd
from dateutil.relativedelta import relativedelta

from finbot.utils.datetime_utils.conversions.str_to_relativedelta import str_to_relativedelta
from finbot.utils.datetime_utils.conversions.str_to_timedelta import str_to_timedelta


def convert_frequency(freq: str, return_type: str) -> pd.Timedelta | relativedelta:
    """
    Converts a frequency string to the specified return type (Timedelta or relativedelta).

    Args:
        freq (str): Frequency string (e.g., 'D', 'W', 'M', etc.).
        return_type (str): Type of return value ('timedelta' or 'relativedelta').

    Returns:
        pd.Timedelta or relativedelta: The converted frequency.
    """
    if return_type == "timedelta":
        return str_to_timedelta(freq)
    elif return_type == "relativedelta":
        return str_to_relativedelta(freq)
    else:
        raise ValueError("return_type must be 'timedelta' or 'relativedelta'.")
