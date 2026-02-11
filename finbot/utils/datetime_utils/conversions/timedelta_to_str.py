"""Convert Timedelta objects to pandas frequency strings.

Reverse operation of str_to_timedelta.py. Converts pandas.Timedelta objects
back into pandas frequency string notation (e.g., '7D', '4H', '30min').

Maps common Timedelta durations to their canonical frequency strings.
Returns default value for Timedeltas that don't match standard frequencies.

Part of the datetime_utils/conversions module for time representation conversions.

Typical usage:
    - Serialize Timedelta for config files or logs
    - Display human-readable frequency labels
    - Convert between different time representation systems
"""

from __future__ import annotations

import pandas as pd


def timedelta_to_str(td: pd.Timedelta, default: str | None = None) -> str:
    """
    Converts a pandas Timedelta object to a frequency string.

    Args:
        td (pd.Timedelta): The Timedelta object to convert.

        default (str | None, optional): The default value to return if the timedelta does not correspond to a known frequency.
            Defaults to None.

    Returns:
        str: Corresponding frequency string.

    Raises:
        ValueError: If the timedelta does not correspond to a known frequency.
    """
    if td >= pd.Timedelta(days=365):
        return "A"
    elif td >= pd.Timedelta(days=91):
        return "Q"
    elif td >= pd.Timedelta(days=30):
        return "M"
    elif td >= pd.Timedelta(weeks=1):
        return "W"
    elif td >= pd.Timedelta(days=1):
        return "D"
    elif td >= pd.Timedelta(hours=1):
        return "H"
    elif td >= pd.Timedelta(minutes=1):
        return "T"
    elif td >= pd.Timedelta(seconds=1):
        return "S"
    else:
        if default is not None:
            return default
        raise ValueError(
            "The given Timedelta does not correspond to a known frequency.",
        )
