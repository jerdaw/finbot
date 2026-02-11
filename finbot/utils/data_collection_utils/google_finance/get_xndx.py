"""Fetch Nasdaq 100 Total Return Index from Google Sheets.

Retrieves historical price data for the Nasdaq 100 Total Return Index (XNDX)
from a Google Sheets data source. Total return includes price appreciation
plus reinvested dividends.

Index: ^XNDX (Nasdaq 100 Total Return)
Data start: 2006-11-08
Update frequency: Daily
Data source: Google Sheets
"""

import datetime as dt

import pandas as pd

from finbot.utils.data_collection_utils.google_finance._utils import get_sheet_base


def get_xndx(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame | pd.Series:
    data_start_date = dt.datetime(2006, 11, 8)
    num_days = (dt.datetime.now() - data_start_date).days
    range_to_get = f"^XNDX!A1:F{num_days}"
    return get_sheet_base(
        range_to_get=range_to_get,
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


if __name__ == "__main__":
    df = get_xndx(check_update=True)
    print(df)
