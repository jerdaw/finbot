"""Parse NBER recession data into dated periods.

Converts boolean recession indicators from NBER/FRED into structured date ranges
for both recession and non-recession (expansion) periods. Returns a dictionary
with separate lists for each cycle type.

This is the core parser used by get_us_gdp_recession_dates.py and
get_us_gdp_non_recession_dates.py convenience wrappers.

Returns:
    dict with keys:
        - "recessions": list of (start, end) tuples for recession periods
        - "non_recessions": list of (start, end) tuples for expansion periods

Typical usage:
    - Regime-based backtesting (compare strategies in different economic climates)
    - Economic cycle analysis
    - Filter time series by economic conditions
"""

import pandas as pd

from finbot.utils.finance_utils.get_us_gdp_recessions_bools import get_us_gdp_recessions_bools


def get_us_gdp_cycle_dates(df: pd.DataFrame | None = None):
    """
    Identifies recession and non-recession periods from a DataFrame.

    :param df: DataFrame with a boolean recession column.
    :return: Tuple of two lists containing the start and end dates for recessions and non-recessionary periods.
    """
    # Initialize variables
    if df is None:
        df = get_us_gdp_recessions_bools()

    recession_periods = []
    non_recession_periods = []
    previous_state = None
    period_start = df.index[0]

    for date, row in df.iterrows():
        current_state = row.iloc[0]

        # Check for state change
        if current_state != previous_state and previous_state is not None:
            period_end = date
            if previous_state:  # End of recession
                recession_periods.append((period_start, period_end))
            else:  # End of non-recession
                non_recession_periods.append((period_start, period_end))
            period_start = date

        previous_state = current_state

    # Handle the last period
    if previous_state:  # Recession
        recession_periods.append((period_start, df.index[-1]))
    else:  # Non-recession
        non_recession_periods.append((period_start, df.index[-1]))

    return {"recessions": recession_periods, "non_recessions": non_recession_periods}


if __name__ == "__main__":
    print(get_us_gdp_cycle_dates())
