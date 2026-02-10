from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_unemployment(
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert unemployment rate data into a pandas DataFrame.

    The unemployment rate is a key economic indicator that shows the percentage of the total labor force that is unemployed but actively seeking employment and willing to work. This function allows for the retrieval of unemployment data for specified intervals, offering insights into labor market trends and economic health.

    Parameters:
    check_update (bool | None): If True, checks for an update to the data. Defaults to True.
    force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
    save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the unemployment rate data for the specified interval.

    Raises:
    ValueError: If the interval is not 'monthly' or 'annually'.

    Example:
    >>> unemployment_data = get_unemployment(interval="annually")
    >>> print(unemployment_data.head())
    """
    # https://www.alphavantage.co/documentation/#unemployment
    return get_avapi_base(
        req_params={"function": "UNEMPLOYMENT"},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_unemployment())
