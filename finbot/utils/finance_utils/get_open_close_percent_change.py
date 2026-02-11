"""Intraday percentage change calculation (open to close).

Calculates the percentage change from opening price to closing price for each
trading day. This captures intraday price movement, distinct from day-to-day
changes which compare consecutive closing prices.

Useful for:
    - Analyzing intraday volatility patterns
    - Identifying gap vs intraday movement
    - Day-trading strategy development
"""

import pandas as pd

from finbot.constants.data_constants import DEMO_DATA


def calculate_open_close_percent_change(data: pd.DataFrame, open_col="Open", close_col="Close"):
    """
    Calculate percent changes in a timeseries based on the 'open_col' and 'close_col' values.

    Parameters:
    data (pd.DataFrame): The input data.
    open_col (str, optional): The column name for the 'open' value. Defaults to 'Open'.
    close_col (str, optional): The column name for the 'close' value. Defaults to 'Close'.

    Returns:
    pd.Series: A series with percent changes.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if open_col not in data.columns:
        raise ValueError(f"Column '{open_col}' not found in DataFrame")
    if close_col not in data.columns:
        raise ValueError(f"Column '{close_col}' not found in DataFrame")

    return (data[close_col] - data[open_col]) / data[open_col]


if __name__ == "__main__":
    gspc = DEMO_DATA
    print(gspc)
    pct_changes_df = calculate_open_close_percent_change(gspc)
    print(pct_changes_df)
