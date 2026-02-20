"""Fetch U.S. Consumer Price Index (CPI) from BLS.

Convenience wrapper for fetching the most commonly used CPI series:
CUUR0000SA0 - CPI for All Urban Consumers (CPI-U), U.S. City Average,
All Items, Not Seasonally Adjusted.

This is the headline CPI number used to measure inflation.

Data source: U.S. Bureau of Labor Statistics
Update frequency: Monthly
Series ID: CUUR0000SA0
"""

import datetime

import pandas as pd

from finbot.utils.data_collection_utils.bls.get_bls_data import get_bls_data


def get_bls_usa_cpi(
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return get_bls_data(
        "CUUR0000SA0",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


if __name__ == "__main__":
    print(get_bls_usa_cpi())
