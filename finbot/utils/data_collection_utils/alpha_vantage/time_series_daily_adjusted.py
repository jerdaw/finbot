"""Fetch daily adjusted stock prices from Alpha Vantage.

Retrieves daily OHLCV (Open, High, Low, Close, Volume) data with adjustments
for splits and dividends. Essential for accurate historical analysis.

Data source: Alpha Vantage Time Series API
Update frequency: Daily (end of day)
API function: TIME_SERIES_DAILY_ADJUSTED
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_time_series_daily_adjusted(
    symbol: str,
    transpose: bool = True,
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert daily adjusted time series data for a specified stock symbol into a pandas DataFrame.

    This function focuses on daily time series data that has been adjusted for corporate actions like dividends, stock splits, and new share issuance, providing a more accurate representation of the stock's value over time. The data includes key metrics such as open, high, low, close prices, and adjusted close prices.

    Args:
        symbol (str): The stock symbol for which the daily adjusted time series data is to be retrieved, e.g., 'AAPL' for Apple Inc.
        transpose (bool | None): If True, transposes the DataFrame so that dates are columns and metrics are rows. Defaults to True.
        check_update (bool | None): If True, checks if the data is up-to-date before fetching it. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the daily adjusted time series data for the specified stock symbol. The DataFrame's structure depends on the 'transpose' parameter.

    Raises:
        ValueError: If the stock symbol is not recognized or if there are issues with data retrieval.

    Example:
        >>> daily_adjusted_data = get_time_series_daily_adjusted("AAPL")
        >>> print(daily_adjusted_data.head())
    """
    interval = "daily"
    return get_avapi_base(
        req_params={
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "interval": interval,
            "symbol": symbol,
        },
        parse_res_params={
            "data_key": "Time Series (Daily)",
            "transpose_data": transpose,
        },
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_time_series_daily_adjusted("SPY"))
