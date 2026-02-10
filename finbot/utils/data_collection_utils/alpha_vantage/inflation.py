from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_inflation(
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert inflation rate data into a pandas DataFrame for a specified interval.

    Inflation rate data is a critical economic indicator that reflects the rate at which the general level of prices for goods and services is rising, leading to a decrease in the purchasing power of money. This function allows for the retrieval of inflation data for different intervals, typically on a yearly basis, but can be adjusted based on the 'interval' parameter.

    Args:
        check_update (bool | None): If True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the inflation rate data for the specified interval. The DataFrame typically includes metrics such as inflation rate percentages and their changes over time.

    Raises:
        ValueError: If the interval is not one of the valid options.

    Example:
        >>> inflation_data = get_inflation(interval="monthly")
        >>> print(inflation_data.head())
    """
    # https://www.alphavantage.co/documentation/#inflation
    return get_avapi_base(
        req_params={"function": "INFLATION"},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_inflation())
