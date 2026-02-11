"""Fetch durable goods orders data from Alpha Vantage.

Retrieves monthly durable goods orders, an economic indicator measuring
new orders for long-lasting manufactured goods (cars, appliances, etc.).
Leading indicator of manufacturing sector health.

Data source: U.S. Census Bureau via Alpha Vantage
Update frequency: Monthly
API function: DURABLES
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_durables(
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert durable goods orders data into a pandas DataFrame.

    Durable Goods Orders data offers insights into new orders placed with domestic manufacturers for the delivery of hard goods. These goods are generally characterized by their longevity and include items such as appliances, vehicles, and heavy machinery. The data is an important economic indicator, reflecting the manufacturing sector's health and consumer confidence.

    Parameters:
    check_update (bool | None): If True, checks for an update to the data. Defaults to False.
    force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
    save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the durable goods orders data for the specified interval.

    Raises:
    ValueError: If the interval is not 'monthly' or 'annually'.

    Example:
    >>> durables_data = get_durables(interval="annually")
    >>> print(durables_data.head())
    """
    # https://www.alphavantage.co/documentation/#durable-goods
    return get_avapi_base(
        req_params={"function": "DURABLES"},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_durables())
