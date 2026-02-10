from __future__ import annotations

from dateutil.relativedelta import relativedelta


def relativedelta_to_str(rel_delta: relativedelta, default: str | None = None) -> str:
    """
    Converts a relativedelta object to a frequency string.

    Args:
        rel_delta (relativedelta): The relativedelta object to convert.
        default (str | None): The default value to return if the relativedelta does not correspond to a known frequency.
                              Defaults to None.

    Returns:
        str: Corresponding frequency string.

    Raises:
        ValueError: If the relativedelta does not correspond to a known frequency.
    """
    if rel_delta.years >= 1:
        return "A"
    elif rel_delta.months >= 3:
        return "Q"
    elif rel_delta.months >= 1:
        return "M"
    elif rel_delta.weeks >= 1:
        return "W"
    elif rel_delta.days >= 1:
        return "D"
    elif rel_delta.hours >= 1:
        return "H"
    elif rel_delta.minutes >= 1:
        return "T"
    elif rel_delta.seconds >= 1:
        return "S"
    else:
        if default is not None:
            return default
        raise ValueError(
            "The given relativedelta does not correspond to a known frequency.",
        )
