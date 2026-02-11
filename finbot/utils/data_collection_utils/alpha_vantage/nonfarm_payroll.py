"""Fetch nonfarm payrolls data from Alpha Vantage.

Retrieves monthly nonfarm payroll employment figures, a key labor market
indicator measuring job creation across all sectors except farms, private
households, and non-profit organizations.

Data source: U.S. Bureau of Labor Statistics via Alpha Vantage
Update frequency: Monthly
API function: NONFARM_PAYROLL
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import get_avapi_base


def get_nonfarm_payroll(
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve and convert nonfarm payroll data into a pandas DataFrame for a specified interval.

    Nonfarm Payroll data is an important economic indicator that measures the total number of paid U.S. workers, excluding several categories such as farm employees, government employees, private household employees, and employees of nonprofit organizations. This data is a key metric in understanding the health of the labor market and the overall economy, especially in the non-agricultural sectors.

    Args:
        check_update (bool | None): If True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If set to True, forces the retrieval of fresh data, bypassing any cached results. Defaults to False.
        save_dir (Path | None): The directory to save the retrieved data. If None, the data is not saved locally. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the nonfarm payroll data for the specified interval. The DataFrame typically includes metrics such as total nonfarm payroll numbers, changes over time, and other relevant statistics.

    Raises:
        ValueError: If the interval is not 'monthly'.

    Example:
        >>> nonfarm_payroll_data = get_nonfarm_payroll()
        >>> print(nonfarm_payroll_data.head())
    """
    # https://www.alphavantage.co/documentation/#nonfarm-payroll
    return get_avapi_base(
        req_params={"function": "NONFARM_PAYROLL"},
        check_update=check_update,
        force_update=force_update,
        save_dir=save_dir,
    )


if __name__ == "__main__":
    print(get_nonfarm_payroll())
