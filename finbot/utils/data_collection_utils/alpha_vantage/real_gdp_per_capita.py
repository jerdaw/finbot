from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_real_gdp_per_capita(
    interval: str = "quarterly",
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert real Gross Domestic Product (GDP) per capita data into a pandas DataFrame for a specified interval.

    Real GDP per capita is a key economic indicator that represents the inflation-adjusted value of all goods and services produced by an economy per person. This measure is crucial for assessing the economic performance of a country relative to its population size, providing insights into the standard of living and economic well-being of its residents.

    Args:
        check_update (bool | None): If True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the real GDP per capita data for the specified interval. The DataFrame typically includes metrics such as GDP per capita value, changes over time, and other relevant statistics.

    Raises:
        ValueError: If the interval is not one of the valid options.

    Example:
        >>> real_gdp_per_capita_data = get_real_gdp_per_capita(interval="annually")
        >>> print(real_gdp_per_capita_data.head())
    """
    # https://www.alphavantage.co/documentation/#real-gdp-per-capita
    return get_avapi_base(
        req_params={"function": "REAL_GDP_PER_CAPITA", "interval": interval},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_real_gdp_per_capita())
