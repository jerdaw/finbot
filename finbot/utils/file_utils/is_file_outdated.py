"""Check if files need updating based on sophisticated staleness criteria.

Determines whether a file is outdated using multiple strategies: fixed
thresholds, time periods, or pandas DataFrame index analysis. Includes
US business day awareness for financial data freshness checking.

Typical usage:
    ```python
    from finbot.utils.file_utils.is_file_outdated import is_file_outdated
    from datetime import datetime, timedelta

    # Check if file older than specific date
    if is_file_outdated("data.csv", threshold=datetime(2025, 1, 1)):
        print("Need to update data.csv")

    # Check if file older than 7 days
    if is_file_outdated("cache.parquet", time_period=timedelta(days=7)):
        refresh_cache()

    # Check if DataFrame's data is outdated (pandas mode)
    if is_file_outdated("prices.parquet", analyze_pandas=True):
        update_prices()

    # Check with custom file time type
    if is_file_outdated("log.txt", time_period="daily", file_time_type="atime"):
        archive_log()
    ```

Three staleness detection modes (mutually exclusive):

1. **Threshold mode** (threshold parameter):
   - File outdated if modification time < threshold date
   - Use for: "data must be after Jan 1, 2025"
   - Example: `is_file_outdated(file, threshold=datetime(2025, 1, 1))`

2. **Time period mode** (time_period parameter):
   - File outdated if modification time outside period from now
   - Accepts: timedelta, relativedelta, or period string
   - Period strings: "minutely", "hourly", "daily", "weekly", "monthly",
     "quarterly", "yearly"
   - Use for: "data must be from last week"
   - Example: `is_file_outdated(file, time_period=timedelta(days=7))`

3. **Pandas analysis mode** (analyze_pandas=True):
   - Opens DataFrame and checks index dates
   - Auto-detects DataFrame frequency (daily, monthly, etc.)
   - Checks if latest date in DataFrame is current
   - Use for: "does this DataFrame have today's data?"
   - Example: `is_file_outdated("prices.parquet", analyze_pandas=True)`

US business day awareness:
    - Always considers US market hours (9:30 AM ET cutoff)
    - Files updated after latest US business day are never outdated
    - Accounts for weekends and holidays automatically
    - Critical for financial data that only updates on trading days

Parameters:
    - file_path: Path to file to check
    - threshold: Fixed datetime threshold (mode 1)
    - time_period: Period from now (mode 2)
    - analyze_pandas: Enable pandas analysis (mode 3)
    - file_time_type: "mtime" (default), "ctime", or "atime"
    - align_to_period_start: Align datetime to period start for comparison
    - file_not_found_error: Raise error if file missing (else return True)

Features:
    - Three complementary staleness detection strategies
    - US business day awareness for financial data
    - Pandas DataFrame index analysis
    - Flexible time period specifications
    - Automatic period alignment options
    - Configurable error handling for missing files

Use cases:
    - Cache invalidation (check if cache needs refresh)
    - Data pipeline triggers (update if source outdated)
    - Daily data updates (check if today's data present)
    - Financial data freshness (respect trading days)
    - Automated backup decisions (backup if old enough)

Example workflows:
    ```python
    # Daily data update check
    if is_file_outdated("prices.parquet", analyze_pandas=True):
        fetch_latest_prices()
        # Only fetches if DataFrame missing today's data

    # Weekly report generation
    if is_file_outdated("report.pdf", time_period="weekly"):
        generate_weekly_report()

    # Cache expiration (7-day TTL)
    if is_file_outdated("cache.json", time_period=timedelta(days=7)):
        refresh_cache()

    # Specific deadline check
    deadline = datetime(2026, 3, 1)
    if is_file_outdated("submission.pdf", threshold=deadline):
        print("File too old for submission")
    ```

Pandas mode details:
    - Opens DataFrame and reads index
    - Auto-detects frequency (daily, monthly, etc.)
    - Compares max date in DataFrame to current period
    - Accounts for DataFrame's natural frequency
    - Returns True if DataFrame empty
    - Automatically converts to DatetimeIndex if needed

Period alignment:
    - align_to_period_start=True: Aligns comparison to period boundaries
    - Example: For weekly period, aligns to Monday start
    - Useful for consistent period-based checks
    - Prevents false positives from mid-period checks

Missing file handling:
    - file_not_found_error=True (default): Raises FileNotFoundError
    - file_not_found_error=False: Returns True (consider missing = outdated)
    - Choose based on application needs

Error handling:
    - FileNotFoundError: File missing (when file_not_found_error=True)
    - ValueError: Invalid parameter combination (must specify exactly one mode)

Performance considerations:
    - Threshold/period modes: Fast (just file stat)
    - Pandas mode: Slower (loads DataFrame header)
    - Use threshold/period for simple checks
    - Use pandas mode for financial time series

Limitations:
    - Pandas mode loads entire DataFrame (could optimize)
    - US business day logic US-specific (not international markets)
    - Timezone-naive (uses local time)

Dependencies: pandas, dateutil, file_utils, datetime_utils, pandas_utils

Related modules: are_files_outdated (batch checking), get_file_datetime
(file times), get_latest_us_business_date (trading days), get_timeseries_frequency
(DataFrame frequency detection).
"""

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


def is_file_outdated(  # noqa: C901 - Multiple threshold type checks and optional parameters
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
