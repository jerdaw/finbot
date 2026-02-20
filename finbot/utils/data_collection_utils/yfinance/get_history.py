"""Fetch historical price data from Yahoo Finance.

Retrieves historical OHLCV (Open, High, Low, Close, Volume) data for stocks,
ETFs, and other securities via the yfinance library. Supports multiple
symbols, date ranges, and various time intervals.

Features:
    - Batch symbol fetching (efficient for multiple tickers)
    - Automatic caching to parquet files
    - Adjusted close prices (dividend/split adjusted)
    - Multiple intervals (1m, 5m, 1h, 1d, 1wk, etc.)
    - Pre/post market data support
    - Incremental updates (only fetches new data)

Data source: Yahoo Finance
Update frequency: Real-time to daily (depends on interval)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from finbot.utils.data_collection_utils.yfinance._yfinance_utils import get_yfinance_base


def get_history(symbols: Sequence[str] | str, **kwargs: Any) -> pd.DataFrame:
    """
    Fetches and filters Yahoo Finance data for the given symbols.

    Args:
        symbols (List[str] | str): The symbols to fetch data for.
        start_date (datetime.date | None): The start date of the data range. Defaults to datetime.date(1900, 1, 1).
        end_date (None | datetime.date | None): The end date of the data range. Defaults to None.
        interval (str, optional): The interval of the data. Defaults to "1d".
        prepost (bool, optional): Whether to include pre and post market data. Defaults to False.
        check_update (bool, optional): Whether to check if the data is already up to date. Defaults to False.
        force_update (bool, optional): Whether to force update the data even if it's already up to date. Defaults to False.

    Returns:
        pd.DataFrame: The fetched and filtered data.
    """
    kwargs.update({"request_type": "history"})
    return get_yfinance_base(symbols=symbols, **kwargs)


if __name__ == "__main__":
    # Example
    import datetime as dt

    print(get_history(symbols="SPY", start_date=dt.date(2021, 1, 1), end_date=dt.date(2021, 1, 31)))
