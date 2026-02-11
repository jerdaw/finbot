"""Fetch Robert Shiller's IE (Irrational Exuberance) dataset.

Downloads the actively maintained Irrational Exuberance dataset from
Robert Shiller's Yale website. Contains comprehensive S&P 500 historical
data including the famous Shiller CAPE ratio (Cyclically Adjusted P/E).

Includes:
    - S&P Composite prices, dividends, earnings
    - CAPE ratio (P/E10) and TR CAPE
    - Real prices and total return prices
    - Consumer Price Index (CPI)
    - Long-term interest rates (GS10)
    - 10-year annualized returns (stocks and bonds)
    - Excess CAPE yield

This is the primary source for CAPE ratio calculations used in market
valuation analysis.

Data source: Yale University - Robert Shiller's website
Update frequency: Monthly
File format: Excel (.xls)
URL: http://www.econ.yale.edu/~shiller/data/ie_data.xls
"""

import datetime as dt

import pandas as pd

from finbot.constants.path_constants import SHILLER_DATA_DIR
from finbot.utils.data_collection_utils.google_finance._utils import is_file_outdated, load_dataframe
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def _download_shiller_ie_data():
    print("Requesting Shiller ie_data from Shiller's website...")
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    df = pd.read_excel(
        url,
        sheet_name="Data",
        engine="xlrd",
        skiprows=7,
        skipfooter=1,
        index_col=0,
        usecols="A:M,O,Q:V",
    )
    if df.empty:
        raise ValueError("Unable to read Shiller ie_data from Shiller's website.")
    renames = {
        "P": "S&P Comp. P",
        "D": "Dividend D",
        "E": "Earnings E",
        "CPI": "Consumer Price Index CPI",
        "Fraction": "Date Fraction",
        "Rate GS10": "Long Interest Rate GS10",
        "Price": "Real Price",
        "Dividend": "Real Dividend",
        "Price.1": "Real Total Return Price",
        "Earnings": "Real Earnings",
        "Earnings.1": "Real TR Scaled Earnings",
        "CAPE": "Cyclically Adjusted Price Earnings Ratio P/E10 or CAPE",
        "TR CAPE": "Cyclically Adjusted Total Return Price Earnings Ratio TR P/E10 or TR CAPE",
        "Yield": "Excess CAPE Yield",
        "Returns": "Monthly Total Bond Returns",
        "Returns.1": "Total Bond Returns",
        "Real Return": "10 Year Annualized Stock Real Return",
        "Real Return.1": "10 Year Annualized Bonds Real Return",
        "Returns.2": "Real 10 Year Excess Annualized  Returns",
    }
    if set(renames.keys()) != set(df.columns):
        raise ValueError("Column names have changed. Update renames.")
    df.rename(columns=renames, inplace=True)
    df.index = pd.Index([pd.Timestamp(int(d), int(d * 100) - int(d) * 100, 1) for d in df.index])
    df = df.drop_duplicates().dropna(how="all").sort_index()
    return df


def get_shiller_ie_data(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
):
    # Prep params
    file_name_stem = "ie_data.parquet"
    file_path = SHILLER_DATA_DIR / file_name_stem

    # determine outdated data
    if force_update:
        is_outdated = True
    elif not check_update:
        is_outdated = not file_path.exists()
    else:
        is_outdated = is_file_outdated(file_path=file_path, analyze_pandas=True, file_not_found_error=False)

    # fetch data if outdated
    if is_outdated:
        df = _download_shiller_ie_data()
        # save newly updated data
        save_dataframe(df=df, file_path=file_path)
    else:
        # load up-to-date data
        df = load_dataframe(file_path=file_path)

    # filter and sort data
    filtered_df = filter_by_date(df=df, start_date=start_date, end_date=end_date)

    return filtered_df.drop_duplicates().dropna(how="all").sort_index()


if __name__ == "__main__":
    shiller_data = get_shiller_ie_data()
    print(shiller_data)
