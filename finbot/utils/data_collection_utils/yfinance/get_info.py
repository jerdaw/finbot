"""Fetch company/security information from Yahoo Finance.

Retrieves fundamental and descriptive information about securities including:
    - Company name, sector, industry
    - Market cap, shares outstanding
    - Financial ratios (P/E, dividend yield, beta)
    - Analyst recommendations
    - Business description
    - Officers and key personnel

Supports caching to avoid excessive API calls.

Data source: Yahoo Finance
Update frequency: Daily to weekly (depends on metric)
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from finbot.utils.data_collection_utils.yfinance._yfinance_utils import get_yfinance_base


def get_info(symbols: Sequence[str] | str, **kwargs) -> pd.DataFrame:
    """
    Fetches and filters Yahoo Finance data for the given symbols.

    Args:
        symbols (List[str] | str): The symbols to fetch data for.
        start_date (datetime.date | datetime.datetime, optional): The start date of the data range. Defaults to datetime.date(1900, 1, 1).
        end_date (None | datetime.date | datetime.datetime, optional): The end date of the data range. Defaults to None.
        interval (str, optional): The interval of the data. Defaults to "1d".
        prepost (bool, optional): Whether to include pre and post market data. Defaults to False.
        check_update (bool, optional): Whether to check if the data is already up to date. Defaults to False.
        force_update (bool, optional): Whether to force update the data even if it's already up to date. Defaults to False.

    Returns:
        pd.DataFrame: The fetched and filtered data.
    """
    kwargs.update({"request_type": "info"})
    return get_yfinance_base(symbols=symbols, **kwargs)


if __name__ == "__main__":
    # Example
    import datetime as dt

    print(get_info(symbols="SPY", start_date=dt.date(2021, 1, 1), end_date=dt.date(2021, 1, 31)))
