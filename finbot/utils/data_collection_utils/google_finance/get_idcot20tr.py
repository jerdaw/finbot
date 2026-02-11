"""Fetch ICE U.S. Treasury 20+ Year Bond Index from Google Sheets.

Retrieves historical price data for the ICE U.S. Treasury 20+ Year Bond
Total Return Index. Tracks the performance of U.S. Treasury bonds with
20+ year maturities including coupon payments.

Index: ^IDCOT20TR (ICE 20+ Year Treasury Total Return)
Data start: 2016-01-04
Update frequency: Daily
Data source: Google Sheets
"""

import datetime as dt

import pandas as pd

from finbot.utils.data_collection_utils.google_finance._utils import get_sheet_base


def get_idcot20tr(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame | pd.Series:
    data_start_date = dt.datetime(2016, 1, 4)
    num_days = (dt.datetime.now() - data_start_date).days
    range_to_get = f"^IDCOT20TR!A1:F{num_days}"
    return get_sheet_base(
        range_to_get=range_to_get,
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


if __name__ == "__main__":
    df = get_idcot20tr()
    print(df)
