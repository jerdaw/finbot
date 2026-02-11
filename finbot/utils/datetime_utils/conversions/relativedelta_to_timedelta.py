"""Convert calendar-aware relativedelta to fixed Timedelta.

Converts dateutil.relativedelta (calendar-aware duration) to datetime.timedelta
(fixed duration) using a reference date to resolve variable-length periods.

Required because months and years have variable lengths - the reference date
determines the actual duration (e.g., February's month length depends on year).

Part of the datetime_utils/conversions module for time representation conversions.

Typical usage:
    - Convert monthly/yearly periods to day counts
    - Calculate exact duration of calendar periods
    - Bridge between relativedelta-based and timedelta-based code
"""

from __future__ import annotations

import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta


def relativedelta_to_timedelta(
    rel_delta: relativedelta,
    reference_date: pd.Timestamp | None = None,
) -> datetime.timedelta:
    """
    Converts a relativedelta to a Timedelta using a reference date.

    Args:
        rel_delta (relativedelta): The relativedelta object to convert.
        reference_date (pd.Timestamp): A reference date for the conversion.

    Returns:
        pd.Timedelta: Corresponding Timedelta object.
    """
    if reference_date is None:
        reference_date = pd.Timestamp("2000-01-01")
    return reference_date + rel_delta - reference_date
