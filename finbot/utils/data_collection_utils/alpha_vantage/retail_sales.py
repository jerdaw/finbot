"""Fetch retail sales data from Alpha Vantage.

Retrieves monthly retail sales figures measuring consumer spending at retail
stores. Leading indicator of consumer confidence and economic health.

Data source: U.S. Census Bureau via Alpha Vantage
Update frequency: Monthly
API function: RETAIL_SALES
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_retail_sales(
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert retail sales data into a pandas DataFrame.

    Retail sales data is a crucial economic indicator that reflects consumer spending on retail goods during a specific period. This information is vital for analyzing consumer behavior and the overall health of the retail sector. The data can be retrieved for different time intervals, typically on a monthly basis.

    Args:
        check_update (bool | None): If set to True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the retail sales data for the specified interval. The DataFrame typically includes metrics such as total sales, percentage changes, and other relevant statistics.

    Raises:
        ValueError: If the interval is not one of the valid options.

    Example:
        >>> retail_sales_data = get_retail_sales(interval="annually")
        >>> print(retail_sales_data.head())
    """
    # https://www.alphavantage.co/documentation/#retail-sales
    return get_avapi_base(
        req_params={"function": "RETAIL_SALES"},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_retail_sales())
