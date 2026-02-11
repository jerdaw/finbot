"""Fetch real-time stock quote data from Alpha Vantage.

Retrieves current price, volume, and other quote data for a specific ticker.
Includes open, high, low, close, volume, and previous close.

Data source: Alpha Vantage Global Quote API
Update frequency: Real-time
API function: GLOBAL_QUOTE
"""

from __future__ import annotations

import pandas as pd

from finbot.config import logger
from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import _make_alpha_vantage_request


def get_global_quote(symbol: str) -> pd.DataFrame:
    """
    Retrieve and convert the global quote data for a specified stock symbol into a pandas DataFrame.

    Global quote data provides key financial information about a stock, including its latest price, volume, and percent changes. This data is essential for investors and analysts to understand the current market position of a stock.

    Args:
        symbol (str): The stock symbol for which the global quote data is to be retrieved. For example, 'AAPL' for Apple Inc.

    Returns:
        pd.DataFrame: A DataFrame containing the global quote data for the specified stock symbol. The DataFrame includes fields such as 'price', 'volume', 'latest trading day', 'previous close', 'change', 'change percent', etc.

    Raises:
        ValueError: If no data is returned for the specified symbol, or if the data is in an unexpected format.
        Exception: If an error occurs during the data retrieval process.

    Example:
        >>> global_quote_data = get_global_quote("AAPL")
        >>> print(global_quote_data)
    """
    # https://www.alphavantage.co/documentation/#latestprice
    try:
        response = _make_alpha_vantage_request(
            {"function": "GLOBAL_QUOTE", "symbol": symbol.upper()},
        )
        data = response.get("Global Quote", {})
        if not data:
            raise ValueError(f"No data returned for symbol: {symbol}")

        # Flexible data formatting
        formatted = {k.split(". ")[1]: v for k, v in data.items() if ". " in k}
        return pd.DataFrame([formatted])
    except Exception as e:
        logger.error(f"Error in get_global_quote: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Example usage
    print(get_global_quote("SPY"))
