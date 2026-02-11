"""Fetch economic data from FRED (Federal Reserve Economic Data).

Retrieves time series data from the Federal Reserve Bank of St. Louis FRED
database using pandas_datareader. Supports batch fetching, caching, and
automatic updates.

FRED provides over 800,000 economic time series including:
    - GDP and productivity data
    - Interest rates and yields
    - Employment and unemployment
    - Inflation measures (CPI, PCE)
    - Money supply and credit

Find series IDs at: https://fred.stlouisfed.org/

Data source: Federal Reserve Bank of St. Louis FRED
Update frequency: Varies by series (daily, weekly, monthly, quarterly, annual)
"""

from __future__ import annotations

import datetime

import pandas as pd
import pandas_datareader as pdr
from dateutil.relativedelta import relativedelta

from constants.path_constants import FRED_DATA_DIR
from finbot.utils.data_collection_utils.pdr._utils import get_pdr_base


def get_fred_data(
    symbols: list[str] | str,
    update_intervals: dict[str, relativedelta] | None = None,
    start_date: None | datetime.date | datetime.datetime = None,
    end_date: None | datetime.date | datetime.datetime = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame | pd.Series:
    if not symbols:
        raise ValueError("At least one symbol must be provided.")
    if not isinstance(symbols, list):
        symbols = [symbols]

    save_dir = FRED_DATA_DIR

    df = get_pdr_base(
        symbols=symbols,
        save_dir=save_dir,
        pdr_reader_class=pdr.fred.FredReader,
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )

    return df


if __name__ == "__main__":
    # Example
    print(get_fred_data(["SP500"], check_update=True))
