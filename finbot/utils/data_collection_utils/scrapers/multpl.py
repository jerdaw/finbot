"""Scrape financial data from multpl.com.

Scrapes S&P 500 fundamental data, treasury rates, and economic indicators
from multpl.com using BeautifulSoup. Provides historical valuation metrics
and macro data in convenient pandas DataFrames.

Available data includes:
    - S&P 500 earnings, P/E ratios, dividends, book value
    - Shiller PE (CAPE ratio)
    - Treasury yields (1M-30Y) and real rates
    - GDP, CPI, population statistics
    - Median income and home prices

Typical usage:
    - Market valuation analysis
    - Building economic indicators dashboard
    - Historical backtesting with fundamentals

Data source: multpl.com (aggregates from various government sources)
Update frequency: Monthly to quarterly (depends on metric)
Scraping method: BeautifulSoup
"""

import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from finbot.constants.path_constants import MULTPL_DATA_DIR
from finbot.utils.file_utils.is_file_outdated import is_file_outdated
from finbot.utils.finance_utils.get_number_from_suffix import get_number_from_suffix
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def _scrape_multpl(url: str) -> pd.DataFrame:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Error fetching data from {url}: {e}") from e

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", id="datatable")
        if not table:
            raise ValueError("Table not found in the HTML content")

        headers = [th.text for th in table.find_all("th")]  # type: ignore
        rows = [[td.text.strip() for td in tr.find_all("td")] for tr in table.find_all("tr")[1:]]  # type: ignore

        df = pd.DataFrame(rows, columns=headers)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Value"] = (
            df["Value"].str.replace(",", "").str.replace("\n", "").str.replace("†", "").apply(get_number_from_suffix)
        )
        df.set_index("Date", inplace=True)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Error processing data from {url}: {e}") from e


def _get_multpl_base(
    url: str,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    url = url.lower()
    save_dir = Path(MULTPL_DATA_DIR)
    file_stem = url.split(".com/")[1].replace("table/", "").replace("/", "_")
    file_path = save_dir / f"{file_stem}.parquet"

    if force_update:
        is_outdated = True
    elif not check_update:
        is_outdated = not file_path.exists()
    else:
        is_outdated = is_file_outdated(
            file_path=file_path,
            analyze_pandas=True,
            align_to_period_start=False,
            file_not_found_error=False,
        )

    if is_outdated:
        data = _scrape_multpl(url=url)
        save_dataframe(df=data, file_path=file_path)
    else:
        data = load_dataframe(file_path=file_path)

    data = pd.DataFrame(filter_by_date(df=data, start_date=start_date, end_date=end_date))

    return data


def get_sp_500_dividend_yield(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-dividend-yield/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_book_value_per_share(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-book-value/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_dividend(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(url="https://www.multpl.com/s-p-500-dividend/table/by-month")


def get_sp_500_dividend_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-dividend-growth/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_earnings(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-earnings/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_earnings_yield(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-earnings-yield/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_earnings_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-earnings-growth/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_real_earnings_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-real-earnings-growth/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_pe_ratio(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-pe-ratio/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_historical_prices(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-historical-prices/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_inflation_adjusted_prices(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/inflation-adjusted-s-p-500/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_price_to_book_value(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-price-to-book/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_price_to_sales_ratio(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-price-to-sales/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_shiller_pe_ratio(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/shiller-pe/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_sales_per_share(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-sales/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_sales_per_share_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-sales-growth/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_real_sales_per_share(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-real-sales/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_sp_500_real_sales_per_share_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/s-p-500-real-sales-growth/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_1_month_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/1-month-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_6_month_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/6-month-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_1_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/1-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_2_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/2-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_3_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/3-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_5_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/5-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_10_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/10-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_20_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/20-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_30_year_treasury_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/30-year-treasury-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_5_year_real_interest_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/5-year-real-interest-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_10_year_real_interest_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/10-year-real-interest-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_20_year_real_interest_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/20-year-real-interest-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_30_year_real_interest_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/30-year-real-interest-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_consumer_price_index(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/cpi/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_federal_debt_percent(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/u-s-federal-debt-percent/table/by-year",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_gdp(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-gdp/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_gdp_growth_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-gdp-growth-rate/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_real_gdp(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-gdp-inflation-adjusted/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_real_gdp_growth_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-real-gdp-growth-rate/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_real_gdp_per_capita(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-real-gdp-per-capita/table/by-quarter",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_case_shiller_real_home_price_index(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/case-shiller-home-price-index-inflation-adjusted/table/by-month",
    )


def get_us_average_income(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-average-income/table/by-year",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_median_income(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-median-income/table/by-year",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_median_income_growth(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-median-income-growth/table/by-year",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_median_real_income(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-median-real-income/table/by-year",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_inflation_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/inflation/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_population(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/united-states-population/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_us_population_growth_rate(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    return _get_multpl_base(
        url="https://www.multpl.com/us-population-growth-rate/table/by-month",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


def get_all(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
    multiprocessing=True,
) -> list[pd.DataFrame]:
    """Runs all the other functions in the module, optionally using multiprocessing."""
    # List of all functions to call
    functions = [
        get_sp_500_dividend_yield,
        get_sp_500_book_value_per_share,
        get_sp_500_dividend,
        get_sp_500_dividend_growth,
        get_sp_500_earnings,
        get_sp_500_earnings_yield,
        get_sp_500_earnings_growth,
        get_sp_500_real_earnings_growth,
        get_sp_500_pe_ratio,
        get_sp_500_historical_prices,
        get_sp_500_inflation_adjusted_prices,
        get_sp_500_price_to_book_value,
        get_sp_500_price_to_sales_ratio,
        get_shiller_pe_ratio,
        get_sp_500_sales_per_share,
        get_sp_500_sales_per_share_growth,
        get_sp_500_real_sales_per_share,
        get_sp_500_real_sales_per_share_growth,
        get_1_month_treasury_rate,
        get_6_month_treasury_rate,
        get_1_year_treasury_rate,
        get_2_year_treasury_rate,
        get_3_year_treasury_rate,
        get_5_year_treasury_rate,
        get_10_year_treasury_rate,
        get_20_year_treasury_rate,
        get_30_year_treasury_rate,
        get_5_year_real_interest_rate,
        get_10_year_real_interest_rate,
        get_20_year_real_interest_rate,
        get_30_year_real_interest_rate,
        get_consumer_price_index,
        get_us_federal_debt_percent,
        get_us_gdp,
        get_us_gdp_growth_rate,
        get_us_real_gdp,
        get_us_real_gdp_growth_rate,
        get_us_real_gdp_per_capita,
        get_case_shiller_real_home_price_index,
        get_us_average_income,
        get_us_median_income,
        get_us_median_income_growth,
        get_us_median_real_income,
        get_us_inflation_rate,
        get_us_population,
        get_us_population_growth_rate,
    ]

    results = []

    # If multiprocessing is enabled, use ThreadPoolExecutor for parallel execution
    if multiprocessing:
        with ThreadPoolExecutor() as executor:
            # Wrap the executor.map with tqdm for a progress bar
            results = list(
                tqdm(
                    executor.map(
                        lambda f: f(
                            start_date=start_date,
                            end_date=end_date,
                            check_update=check_update,
                            force_update=force_update,
                        ),
                        functions,
                    ),
                    total=len(functions),
                ),
            )
    else:
        # Wrap the sequential execution with tqdm for a progress bar
        for function in tqdm(functions):
            results.append(
                function(
                    start_date=start_date,
                    end_date=end_date,
                    check_update=check_update,
                    force_update=force_update,
                ),
            )

    return results


if __name__ == "__main__":
    all_data = get_all()
    for data in all_data:
        print(data.loc[[data.index.min(), data.index.max()]])
