from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base
from finbot.utils.validation_utils.validation_helpers import validate_literals


def get_cpi(
    interval: Literal["monthly", "semiannual"] = "monthly",
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert Consumer Price Index (CPI) data for a specified interval into a pandas DataFrame.

    The Consumer Price Index (CPI) measures the average change over time in the prices paid
    by urban consumers for a market basket of consumer goods and services. This function allows
    the retrieval of CPI data for either a monthly or yearly interval, based on the 'interval'
    parameter.

    Parameters:
    interval (str | None): The time interval for the CPI data. Defaults to 'monthly'.
                             Other valid value is 'semiannual'.
    check_update (bool | None): If True, checks for an update to the data. Defaults to True.
    force_update (bool | None): If True, forces a fresh retrieval of the data, ignoring any
                                   cached results. Defaults to False.
    save_dir (Path | None): The directory to save the retrieved data. If None, the
                                          data will not be saved locally. Defaults to None.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the CPI data for the specified interval.

    Note:
    The data is retrieved using an internal API function `_get_avapi_simple`.

    Example:
    >>> cpi_data = get_cpi(interval="yearly")
    >>> print(cpi_data.head())
    """
    # https://www.alphavantage.co/documentation/#cpi
    available_intervals = ["monthly", "semiannual"]
    validate_literals(interval, "interval", available_intervals)

    return get_avapi_base(
        req_params={"function": "CPI", "interval": interval},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    # Example usage
    print(get_cpi())
