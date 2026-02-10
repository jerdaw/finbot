from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base
from finbot.utils.validation_utils.validation_helpers import validate_literals


def get_real_gdp(
    interval: Literal["quarterly", "annual"] = "quarterly",
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert real Gross Domestic Product (GDP) data into a pandas DataFrame for a specified interval.

    Real GDP is an essential economic indicator that measures the value of all goods and services produced by an economy, adjusted for inflation. This inflation-adjusted measure provides a more accurate reflection of an economy's size and how it is growing over time. The data can be retrieved for different intervals, typically on a quarterly or annual basis.

    Args:
        interval (str | None): The time interval for the real GDP data. Valid options include 'quarterly' and 'annual'. Defaults to 'quarterly'.
        check_update (bool | None): If True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the real GDP data for the specified interval. The DataFrame typically includes metrics such as GDP value, percentage changes, and other relevant statistics.

    Raises:
        ValueError: If the interval is not one of the valid options.

    Example:
        >>> real_gdp_data = get_real_gdp(interval="annually")
        >>> print(real_gdp_data.head())
    """
    # https://www.alphavantage.co/documentation/#real-gdp
    available_intervals = ["quarterly", "annual"]
    validate_literals(interval, "interval", available_intervals)

    return get_avapi_base(
        req_params={"function": "REAL_GDP", "interval": interval},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_real_gdp())
