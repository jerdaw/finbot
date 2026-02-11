"""Fetch current (latest) prices from Yahoo Finance.

Retrieves the most recent trading price for one or more securities by
fetching the last 5 days of 1-minute interval data and returning the
most recent close price with timestamp.

Useful for:
    - Real-time price monitoring
    - Portfolio valuation
    - Quick price checks
    - Pre/post market price tracking

Data source: Yahoo Finance
Update frequency: Real-time (1-minute delay)
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from typing import Any

import pandas as pd
import yfinance as yf

from finbot.utils.pandas_utils.filter_by_time import filter_by_time


def get_current_price(
    symbols: Sequence[str] | str,
    prepost: bool = False,
    min_time: dt.time | None = None,
) -> pd.DataFrame:
    if isinstance(symbols, str):
        symbols = [symbols]
    symbols = sorted(symbols)

    if min_time is None:
        min_time = dt.time(4, 0) if prepost else dt.time(9, 30)

    # Initialize dictionary to store closing prices and timestamps
    data: dict[Any, Any] = {}

    for s in symbols:
        history = yf.Ticker(s).history(
            period="5d",
            interval="1m",
            prepost=True,
        )
        if not prepost:
            history = filter_by_time(df=history, start_time=dt.time(9, 30), end_time=dt.time(16, 0))
        if not history.empty:
            # Get the latest closing price and corresponding timestamp
            latest_close = history["Close"].iloc[-1]
            latest_date = history.index[-1]
            data[latest_date] = data.get(latest_date, {})
            data[latest_date][s] = latest_close

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(data, orient="index")

    return df


if __name__ == "__main__":
    # Example
    print(get_current_price(symbols="SPY"))
    print(get_current_price(symbols="SPY", prepost=True))
