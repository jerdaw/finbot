from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base
from finbot.utils.validation_utils.validation_helpers import validate_literals


def get_federal_funds_rate(
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert Federal Funds Rate data for a specified interval into a pandas DataFrame.

    The Federal Funds Rate is a critical economic indicator representing the interest rate at which depository institutions lend reserve balances to other depository institutions on an overnight basis. It is a key tool used by central banks to steer monetary policy and influence economic conditions.

    Parameters:
    interval (str | None): The time interval for the Federal Funds Rate data. Defaults to 'daily'. Valid values are 'daily', 'weekly', and 'monthly'.
    check_update (bool | None): If True, checks for an update to the data. Defaults to True.
    force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
    save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the Federal Funds Rate data for the specified interval.

    Raises:
    ValueError: If the interval is not one of the valid options.

    Example:
    >>> federal_funds_rate_data = get_federal_funds_rate(interval="monthly")
    >>> print(federal_funds_rate_data.head())
    """
    # https://www.alphavantage.co/documentation/#interest-rate
    available_intervals = ["daily", "weekly", "monthly"]
    validate_literals(interval, "interval", available_intervals)

    return get_avapi_base(
        req_params={"function": "FEDERAL_FUNDS_RATE", "interval": interval},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    # Example usage
    print(get_federal_funds_rate())
