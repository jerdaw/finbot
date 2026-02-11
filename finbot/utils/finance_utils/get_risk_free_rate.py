"""Risk-free rate retrieval from FRED (3-month T-bill rates).

Fetches the current or historical risk-free rate (DTB3 series) from the Federal Reserve
Economic Data (FRED) database. The 3-month Treasury bill rate is the standard proxy for
the risk-free rate in financial modeling.

Cached using LRU cache to minimize API calls.

Typical usage:
    - Calculate Sharpe ratios and risk-adjusted returns
    - Discount future cash flows
    - Benchmark portfolio performance
"""

from functools import lru_cache

import pandas as pd

from finbot.config import logger
from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data


@lru_cache(maxsize=10)
def get_risk_free_rate(full_series: bool = False) -> float | pd.DataFrame | pd.Series:
    """
    Retrieves the latest 3-month T-bill rates from the FRED database.
    If full_series is True, returns the entire series; otherwise, returns the latest rate.

    Parameters:
    full_series (bool): Determines whether to return the full series or the latest rate only.

    Returns:
    Union[float, pd.DataFrame]: The latest 3-month T-bill rate or the entire series.

    Raises:
    ValueError: If no data is available or data format is incorrect.
    """
    try:
        three_month_tbill_rates = get_fred_data(symbols="DTB3")
        if three_month_tbill_rates.empty:
            raise ValueError("No data available for 3-month T-bill rates.")

        if not isinstance(three_month_tbill_rates, pd.DataFrame):
            raise ValueError("Unexpected data format for 3-month T-bill rates.")

        # rename column to "Values" for consistency
        three_month_tbill_rates.rename(columns={"DTB3": "Data"}, inplace=True)

        return three_month_tbill_rates if full_series else three_month_tbill_rates.iloc[-1]
    except Exception as e:
        logger.error(f"Error fetching 3-month T-bill rates: {e}")
        raise


if __name__ == "__main__":
    try:
        print(get_risk_free_rate())
        print(get_risk_free_rate(full_series=True))
    except Exception as e:
        logger.error(f"Failed to retrieve risk-free rate: {e}")
