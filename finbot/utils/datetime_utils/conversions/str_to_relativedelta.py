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
