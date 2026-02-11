"""Convert pandas frequency strings to relativedelta objects.

Parses pandas-style frequency strings (e.g., 'M', 'Q', 'Y') into dateutil
relativedelta objects representing calendar-aware durations.

Unlike str_to_timedelta.py which handles fixed durations, this handles
variable-length periods like months (28-31 days) and years (365-366 days).

Part of the datetime_utils/conversions module for time representation conversions.

Typical usage:
    - Parse monthly/quarterly/yearly frequencies
    - Handle calendar-aware date arithmetic
    - Support business period calculations
"""

from __future__ import annotations

from dateutil.relativedelta import relativedelta


def str_to_relativedelta(freq: str, default: relativedelta | None = None) -> relativedelta:
    """
    Converts a frequency string to a relativedelta object.

    Args:
        freq (str): Frequency string (e.g., 'D', 'W', 'M', etc.).
        default (relativedelta | None): Default relativedelta object to return if the frequency is not recognized. Defaults to None.

    Returns:
        relativedelta: Corresponding relativedelta object.

    Raises:
        ValueError: If the frequency does not correspond to a known relativedelta.
    """
    freq = freq.upper()
    if freq in ("S", "SEC", "SECOND"):
        return relativedelta(seconds=1)
    elif freq in ("T", "MIN", "MINUTE"):
        return relativedelta(minutes=1)
    elif freq in ("H", "HR", "HOUR", "HOURLY"):
        return relativedelta(hours=1)
    elif freq in ("D", "DAY", "DAILY"):
        return relativedelta(days=1)
    elif freq in ("W", "WEEK", "WEEKLY"):
        return relativedelta(weeks=1)
    elif freq in ("M", "MO", "MONTH", "MONTHLY"):
        return relativedelta(months=1)
    elif freq in ("Q", "QUARTER", "QUARTERLY"):
        return relativedelta(months=3)
    elif freq in ("A", "Y", "YEAR", "ANNUAL", "ANNUALLY"):
        return relativedelta(years=1)
    else:
        print(f"Unable to get relativedelta from freq: {freq}")
        if default is not None:
            return default
        raise ValueError(
            "The given frequency does not correspond to a known relativedelta.",
        )
