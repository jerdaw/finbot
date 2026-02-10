from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

from finbot.utils.datetime_utils.get_latest_us_business_date import get_latest_us_business_date
from finbot.utils.datetime_utils.is_datetime_in_period import is_datetime_in_period
from finbot.utils.file_utils.get_file_datetime import get_file_datetime
from finbot.utils.pandas_utils.get_timeseries_frequency import get_timeseries_frequency
from finbot.utils.pandas_utils.load_dataframe import load_dataframe


def is_file_outdated(
    file_path: Path | str,
    threshold: datetime | date | None = None,
    time_period: str | relativedelta | timedelta | None = None,
    analyze_pandas: bool = False,
    file_time_type: str | None = None,
    align_to_period_start: bool = False,
    file_not_found_error: bool = True,
) -> bool:
    """
    Check if a file is outdated based on the specified criteria.

    Args:
        file_path (Path): The path to the file.
        threshold (datetime | date | None, optional): The threshold date to compare the file's modification time to.
            If specified, the file's modification date must be earlier than the threshold date to be considered outdated.
            Defaults to None.
        time_period (str | relativedelta | timedelta | None, optional): The time period to check against. It can be a string representing
            a pre-defined period ("minutely", "hourly", "daily", "weekly", "monthly", "quarterly", "yearly"), or a
            relativedelta or timedelta object representing a custom period. If specified, the file's modification date must be outside
            the specified time period to be considered outdated. Defaults to None.
        analyze_pandas (bool, optional): Whether to check if the file is outdated by opening and analyzing the pandas file's index.
        file_time_type (str, optional): The type of time to use for comparison. Can be "mtime" (modification time),
        align_to_period_start (bool, optional): Whether to align the minimum datetime to the start of the time period.
            If True, the file's modification date will be aligned to the start of the specified time period before
            comparison. Defaults to False.
        file_not_found (bool, optional): Whether to raise an error if the file does not exist. Defaults to True.

    Returns:
        bool: True if the file is outdated, False otherwise.

    Raises:
        ValueError: If both threshold and time_period are specified, or if neither is specified.

    """
    last_bday = get_latest_us_business_date(min_time=time(9, 30))
    if file_time_type is None:
        file_time_type = "mtime"

    if sum((threshold is not None, time_period is not None, analyze_pandas)) != 1:
        raise ValueError(
            "Exactly one of threshold, time_period, or check_pandas must be specified.",
        )

    file_path = Path(file_path)

    if not file_path.exists():
        if file_not_found_error:
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        return True

    last_file_update = get_file_datetime(file_path, file_time_type)

    if analyze_pandas:
        df = load_dataframe(file_path=file_path)
        if df.empty:
            return True
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.set_index(
                pd.DatetimeIndex(
                    df["Date"] if "Date" in df.columns else df.index,
                ),
            )
        # Set variables based on the dataframe index
        time_period = get_timeseries_frequency(df)
        last_file_update = df.index.max()

    # If the file was updated after the last business day, it is not outdated
    if last_file_update.date() >= last_bday:
        return True

    if threshold:
        return last_file_update.date() < threshold

    if isinstance(time_period, timedelta):
        time_period_start = datetime.now() - time_period
        return last_file_update < time_period_start

    if time_period is not None:  # This conditional is mainly here to satisfy mypy
        return not is_datetime_in_period(
            datetime_obj=last_file_update,
            time_period=time_period,
            align_to_period_start=align_to_period_start,
        )
    else:
        raise ValueError(
            "Either threshold, time_period, or analyze_pandas must be specified.",
        )
