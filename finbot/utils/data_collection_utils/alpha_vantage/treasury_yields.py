from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base
from finbot.utils.validation_utils.validation_helpers import validate_literals


def _get_treasury_yield_for_maturity(
    maturity: str,
    interval: str,
    check_update: bool,
    force_update: bool,
    save_dir: Path | None,
) -> pd.DataFrame:
    """
    Internal helper function to retrieve Treasury yield data for a specific maturity term over a given interval.

    This function is designed to fetch and format U.S. Treasury yields data for a specific maturity term such as '3month', '2year', etc. The data is retrieved for the specified time interval (e.g., 'daily', 'monthly') and can be optionally saved to a directory.

    Args:
        maturity (str): The maturity term for which Treasury yield data is required. For example, '3month', '2year', etc.
        interval (str): The time interval over which the data is retrieved. Can be values like 'daily', 'monthly', etc.
        check_update (bool): If True, checks for an update to the data.
        force_update (bool): If True, the data is fetched afresh even if a cached version exists.
        save_dir (Path | None): The directory where the fetched data should be saved. If None, the data is not saved to disk.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the Treasury yield data for the specified maturity and interval.

    Note:
        This is an internal function typically used within other high-level data retrieval functions in the module and is not meant to be directly exposed to end users.

    Example:
        >>> yield_data = _get_treasury_yield_for_maturity("5year", "monthly", False, None)
        >>> print(yield_data.head())
    """
    data_df = get_avapi_base(
        req_params={
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity,
        },
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )
    return data_df.rename(columns={"value": maturity})


def get_treasury_yields(
    maturity: Literal["all", "3month", "2year", "5year", "7year", "10year", "30year"] = "all",
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert U.S. Treasury yields data into a pandas DataFrame for specified maturities and intervals.

    Treasury yields are the returns on investment for U.S. government debt obligations. These yields are widely used as benchmarks for fixed-income securities and are indicative of the government's borrowing costs. This function allows for the retrieval of treasury yields data for specified maturities and time intervals.

    Args:
        maturity (str): The maturity term of the treasury yields to retrieve. Can be one of 'all', '3month', '2year', '5year', '7year', '10year', '30year'. Defaults to 'all', which retrieves data for all available maturities.
        interval (str): The time interval for retrieving the data. Valid values include 'daily', 'weekly', 'monthly', etc. Defaults to 'daily'.
        check_update (bool): If set to True, checks for an update to the data. Defaults to False.
        force_update (bool): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the treasury yields data for the specified maturities and intervals. Each column represents a different maturity.

    Raises:
        ValueError: If the maturity or interval is not one of the valid options.

    Example:
        >>> treasury_yields = get_treasury_yields(maturity="10year", interval="monthly")
        >>> print(treasury_yields.head())
    """
    available_intervals = ["daily", "weekly", "monthly"]
    validate_literals(interval, "interval", available_intervals)
    available_maturities = ["3month", "2year", "5year", "7year", "10year", "30year"]
    validate_literals(maturity, "maturity", [*available_maturities, "all"])
    maturities_data: dict[str, None | pd.DataFrame] = (
        dict.fromkeys(available_maturities) if maturity == "all" else {maturity: None}
    )

    for mat in maturities_data:
        maturities_data[mat] = _get_treasury_yield_for_maturity(
            maturity=mat,
            interval=interval,
            check_update=check_update,
            force_update=force_update,
            save_dir=save_dir,
        )

    data_frames = [df for df in maturities_data.values() if df is not None]
    if data_frames:
        return pd.concat(data_frames, axis=1).sort_index()
    # Handle the case where all values are None
    raise ValueError("Unable to get treasury yield data.")


if __name__ == "__main__":
    print(get_treasury_yields())
