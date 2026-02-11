"""Generate rolling time windows at various frequencies.

Creates overlapping time windows (rolling or expanding) for analyzing time series
at different granularities: All Time, Yearly, Quarterly, Monthly, Weekly, Daily.

Uses trading day assumptions (252 periods per year) for window sizing.

Typical usage:
    - Rolling performance analysis at multiple time scales
    - Generate date ranges for sliding window backtests
    - Time-based cross-validation splits
    - Multi-horizon forecasting
"""

import pandas as pd
from dateutil.relativedelta import relativedelta

# Constants
STEP_OPTIONS = ("All Time", "Yearly", "Quarterly", "Monthly", "Weekly", "Daily")
PERIODS_PER_YEAR = 252


def validate_inputs(step: str):
    """Validates the inputs for the step parameter."""
    if step not in STEP_OPTIONS:
        raise ValueError(f"Invalid step option. Expected one of {STEP_OPTIONS}, got {step}.")


def rolling_method(series: pd.Series, step: str) -> pd.DataFrame:
    """Implements the rolling method logic."""
    rolling_spans = [len(series) - 1] + [round(PERIODS_PER_YEAR / n) for n in (1, 4, 12, 52, PERIODS_PER_YEAR)]
    rolling_span = rolling_spans[STEP_OPTIONS.index(step)]
    period_starts = []
    period_ends = []
    cur_start_idx = 0
    while cur_start_idx + rolling_span <= len(series):
        period_starts.append(series.index[cur_start_idx])
        end_idx = cur_start_idx + rolling_span
        period_ends.append(series.index[end_idx] if end_idx < len(series) else None)
        cur_start_idx += 1
    steps_df = pd.DataFrame(series.loc[period_starts]).rename(columns={"Close": "Start Price"})
    steps_df["Period End"] = period_ends
    steps_df["End Price"] = [*series.loc[period_ends[:-1]].to_list(), None]  # type: ignore[index]
    return steps_df


def calendarize_method(series: pd.Series, step: str, start_date, end_date) -> pd.DataFrame:
    """Implements the calendarize method logic."""
    calendarized_steps = [
        lambda x: end_date,
        lambda x: x + relativedelta(years=1),
        lambda x: x + relativedelta(months=3),
        lambda x: x + relativedelta(months=1),
        lambda x: x + relativedelta(days=7),
        lambda x: x + relativedelta(days=1),
    ]
    calendarized_step = calendarized_steps[STEP_OPTIONS.index(step)]
    start_options = [
        start_date,
        pd.Timestamp(start_date.year, 1, 1),
        pd.Timestamp(start_date.year, 3 * start_date.quarter - 2, 1),
        pd.Timestamp(start_date.year, start_date.month, 1),
        start_date - pd.Timedelta(days=(start_date.dayofweek + 3) % 7),
        pd.Timestamp(start_date.year, start_date.month, start_date.day),
    ]
    calendarized_start = start_options[STEP_OPTIONS.index(step)]

    steps = [start_date] if calendarized_start > start_date else []
    cur_dt = calendarized_start
    while cur_dt < end_date:
        series_step_dt = series.truncate(before=cur_dt).index[0]
        if not steps or series_step_dt != steps[-1]:
            steps.append(series_step_dt)
        cur_dt = calendarized_step(cur_dt)
    if steps and steps[-1] != end_date:
        steps.append(end_date)

    steps_df = pd.DataFrame(series.loc[steps]).rename(columns={"Close": "Start Price"})
    steps_df["Period End"] = [steps_df.index[i + 1] for i in range(len(steps_df) - 1)] + [None]
    steps_df["End Price"] = [*steps_df["Start Price"].loc[steps_df["Period End"].dropna()].to_list(), None]
    return steps_df


def step_datetimes(
    series: pd.Series,
    step: str,
    align_to_calendar: bool = True,
    include_prices: bool = True,
) -> pd.DataFrame:
    """
    Segments a pandas Series with a datetime index into specified time steps using either a rolling or a calendar-aligned approach.

    The 'step' parameter defines the granularity of the segmentation. The 'align_to_calendar' parameter determines the type of segmentation: calendar-aligned if True, rolling if False.

    The calendar-aligned method segments the data into periods that align with calendar units (e.g., months, weeks). The rolling method creates overlapping periods starting at regular intervals as defined by the 'step' parameter.

    The resulting DataFrame includes the start and end dates of each period. If 'include_prices' is set to True, it also includes the start and end prices for each period.

    Parameters:
    - series (pd.Series): A pandas Series with a datetime index, typically representing time-series data.
    - step (str): The granularity of the segmentation, chosen from predefined options.
    - align_to_calendar (bool): If True, aligns periods to the calendar. If False, uses a rolling approach. Default is True.
    - include_prices (bool): If True, includes start and end prices in the resulting DataFrame. Default is True.

    Returns:
    - pd.DataFrame: A DataFrame with columns for period start, period end, and optionally start and end prices.

    Example:
    ```python
    from finbot.constants.data_constants import DEMO_DATA

    # Segmenting data on a monthly basis, aligned to the calendar
    monthly_data = step_datetimes(DEMO_DATA["Close"], "Monthly", True, True)
    print(monthly_data)

    # Segmenting data on a monthly basis using a rolling approach
    monthly_rolling_data = step_datetimes(DEMO_DATA["Close"], "Monthly", False, True)
    print(monthly_rolling_data)
    ```
    """
    validate_inputs(step)
    start_date = series.index[0]
    end_date = series.index[-1]

    if align_to_calendar:
        steps_df = calendarize_method(series, step, start_date, end_date)
    else:
        steps_df = rolling_method(series, step)

    steps_df.index.name = "Period Start"
    if not include_prices:
        steps_df.drop(columns=["Start Price", "End Price"], inplace=True)

    return steps_df


if __name__ == "__main__":
    from finbot.constants.data_constants import DEMO_DATA

    for align in [True, False]:
        for step_option in STEP_OPTIONS:
            print("Calendarized" if align else "Rolling", step_option)
            res = step_datetimes(DEMO_DATA["Close"], step_option, align)
            print(res)
            print()
