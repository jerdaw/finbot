"""Fetch DataFrames for popular FRED economic series.

Convenience wrapper that scrapes the FRED website for currently popular
series IDs, then fetches their complete historical data in one batch.

Popular series typically include:
    - S&P 500 stock index
    - Unemployment rate
    - GDP and industrial production
    - Interest rates and yields
    - Consumer sentiment indexes

Useful for getting a broad snapshot of current economic conditions.
"""

import pandas as pd

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data
from finbot.utils.data_collection_utils.fred.get_popular_fred_symbols import get_popular_fred_symbols


def get_popular_fred_symbol_dfs(
    force_update_symbols: bool = False,
    force_update_data: bool = False,
    check_update_data: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Get the popular FRED database names and their corresponding DataFrames.
    """
    fred_symbols = get_popular_fred_symbols(force_update=force_update_symbols)

    return get_fred_data(symbols=fred_symbols, check_update=check_update_data, force_update=force_update_data)


if __name__ == "__main__":
    # Can set check_update_data to True to check if the data is up to date, but it will take a while to grab
    res = get_popular_fred_symbol_dfs(force_update_symbols=True, check_update_data=False)
    print(res)
