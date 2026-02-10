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
