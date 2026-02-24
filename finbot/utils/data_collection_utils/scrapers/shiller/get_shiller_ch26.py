"""Fetch Robert Shiller's Chapter 26 dataset.

Downloads historical market data from Robert Shiller's book "Irrational
Exuberance" Chapter 26 Excel file. Contains stock prices, dividends,
earnings, interest rates, and CPI data dating back to the 1800s.

Includes:
    - S&P Composite stock price index
    - Dividends and earnings
    - Interest rates (1-year and 10-year)
    - Consumer Price Index (CPI)
    - Real values and present value calculations
    - P/E ratios (1-year and 10-year CAPE)

Note: Chapter 26 data only goes to 2016. For more recent data,
use get_shiller_ie_data instead.

Data source: Yale University - Robert Shiller's website
Update frequency: Static (historical dataset to 2016)
File format: Excel (.xlsx)
"""

import pandas as pd

from finbot.constants.path_constants import SHILLER_DATA_DIR
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def get_shiller_ch26(force_update: bool = False) -> pd.DataFrame:
    url = "http://www.econ.yale.edu/~shiller/data/chapt26.xlsx"
    file_name = "chapt26.parquet"
    file_path = SHILLER_DATA_DIR / file_name

    # Ch26 data only goes to 2016, changed this to only request file from website if there's no local copy
    if not force_update and file_path.is_file():
        print("Pulling Shiller chapt26 data from shiller_data data_storage...")
        return load_dataframe(file_path)

    print("Requesting Shiller chapt26 data from Shiller's website...")
    df = pd.read_excel(
        url,
        sheet_name="Data",
        engine="openpyxl",
        skiprows=7,
        skipfooter=7,
        index_col=0,
        usecols="A:I, K:U",
    )
    if df.empty:
        raise ValueError("Unable to read Shiller chapt26 data from Shiller's website.")
    renames = {
        "Index": "S&P Composite Stock Price Index",
        "Unnamed: 2": "Dividends Accruing to Index",
        "Unnamed: 3": "Earnings Accruing to Index",
        "Unnamed: 4": "One-Year Interest Rate",
        "10yrpost53": "Long Government Bond Yield 10yrpost53",
        "Unnamed: 6": "Consumer Price Index",
        "Unnamed: 7": "Real One-Year Interest Rate",
        "Consumption": "Real Per Capita Consumption",
        "Unnamed: 10": "RealP Stock Price",
        "Const r": "Present Value of Real Dividends Const r",
        "Market r": "Present Value of Real Dividends Market r",
        "Cons disc.": "Present Value of Real Dividends Cons disc.",
        "Unnamed: 14": "RealD S&P Dividend",
        "Unnamed: 15": "Return on S&P Composite",
        "Unnamed: 16": "ln(1+ret)",
        "Unnamed: 17": "RealE Earnings",
        "Earnings": "Price Earnings Ratio One-Year Earnings",
        "Earnings.1": "Ten-Year Average  of Real  Earnings",
        "Earnings.2": "Price Earnings Ratio Ten-Year Earnings",
    }

    if set(renames.keys()) != set(df.columns):
        raise ValueError(f"Expected columns: {set(renames.keys())}, got: {set(df.columns)}")

    df.rename(columns=renames, inplace=True)
    df.index = pd.DatetimeIndex([pd.Timestamp(n, 1, 1) for n in df.index])
    df["Real Per Capita Consumption"] = pd.to_numeric(df["Real Per Capita Consumption"], errors="coerce")
    df = df.drop_duplicates().dropna(how="all").sort_index()
    save_dataframe(df=df, file_path=file_path)
    return df


if __name__ == "__main__":
    shiller_data = get_shiller_ch26()
    print(shiller_data)
