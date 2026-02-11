"""Fetch intraday stock prices from Alpha Vantage.

Retrieves intraday OHLCV data at various intervals (1min, 5min, 15min, 30min,
60min). Useful for day trading analysis and high-frequency strategies.

Data source: Alpha Vantage Intraday API
Update frequency: Real-time during market hours
API function: TIME_SERIES_INTRADAY
"""

from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
from time import sleep
from typing import Any

import pandas as pd
from tqdm.auto import tqdm

from finbot.config import logger
from finbot.constants.path_constants import ALPHA_VANTAGE_DATA_DIR
from finbot.exceptions import ParseError
from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import _make_alpha_vantage_request
from finbot.utils.datetime_utils.daily_time_range import DailyTimeRange
from finbot.utils.datetime_utils.get_latest_us_business_date import get_latest_us_business_date
from finbot.utils.datetime_utils.get_months_between_dates import get_months_between_dates
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.filter_by_time import filter_by_time
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def _get_missing_intraday_months(existing_data: pd.DataFrame, start_date: date, end_date: date) -> set[str]:
    """
    Identifies the months for which intraday data is missing or incomplete in the existing dataset.

    This internal function is used to determine which months of data need to be fetched to complete the dataset for a given date range. It checks the existing data against the desired date range and identifies any gaps.

    Args:
        existing_data (pd.DataFrame): A DataFrame with existing intraday data
        start_date (date): The start date of the desired data range.
        end_date (date): The end date of the desired data range.

    Returns:
        Set[str]: A set of months (in 'YYYY-MM' format) for which data is missing or incomplete.

    Raises:
        Exception: If there's an error in identifying missing months.

    This function is particularly useful in scenarios where intraday data is collected over time and needs to be updated or checked for completeness.
    """
    # Find out if there's actually any missing data
    try:
        all_months = set(
            get_months_between_dates(
                start_date,
                end_date,
                return_type="int",
            ),
        )
        if "month_data_complete" in existing_data.columns:
            complete_entries = existing_data[existing_data["month_data_complete"] == 1]
            complete_months = {(int(dt.year), int(dt.month)) for dt in complete_entries.index}
        else:
            complete_months = set()
        missing_months: set[tuple[int, int]] = all_months - complete_months  # type: ignore
        for yr_mn in missing_months.copy():
            lbd = get_latest_us_business_date(yr_mn[0], yr_mn[1])
            # Set lbdt to the last/max minute for extended hours trading
            lbdt = datetime(
                lbd.year,  # type: ignore
                lbd.month,  # type: ignore
                lbd.day,  # type: ignore
                19,
                59,
                0,
            )
            if lbdt in existing_data.index:
                missing_months.remove(yr_mn)
        return {f"{yr_mn[0]}-{str(yr_mn[1]).zfill(2)}" for yr_mn in missing_months}
    except Exception as e:
        logger.error(f"Error in _get_missing_intraday_months: {e}")
        raise


def _merge_and_save_intraday(
    symbol: str,
    existing_data: pd.DataFrame,
    new_data: dict[str, Any],
    file_path: Path,
) -> pd.DataFrame:
    """
    Merges existing intraday data with newly fetched data for a specific stock symbol and saves it to a file.

    This function is designed to integrate new intraday data with any existing data, with the new data overwriting any overlapping existing data. After merging, the combined dataset is saved to the specified file path.

    Args:
        symbol (str): The stock symbol for which the data is merged.
        existing_data (pd.DataFrame): A DataFrame containing the existing intraday data.
        new_data (Dict[str, Any]): A dictionary containing newly fetched intraday data.
        file_path (Path): The file path where the merged data will be saved.

    Returns:
        pd.DataFrame: The merged DataFrame containing both existing and new intraday data.

    Raises:
        ParserError: If there's an error during the data merging process.
        OSError: If there's an IO error during saving the data.

    This function ensures that the intraday data for a stock symbol is up-to-date and stored securely.
    """
    try:
        logger.info(f"Merging fetched {symbol} intraday data...")

        new_df = pd.DataFrame.from_dict(new_data, orient="index")
        new_df.index = pd.to_datetime(new_df.index)

        # Combine the dataframes with preference to the new dataframe
        combined_df = (
            pd.concat([existing_data, new_df])
            .drop_duplicates(
                subset=new_df.index.name,
                keep="last",
            )
            .sort_index()
        )

        logger.info(f"Finished merging fetched {symbol} intraday data.")

        save_dataframe(df=combined_df, file_path=file_path)
        logger.info(f"{symbol} intraday data saved to {file_path!s}.")
    except pd.errors.ParserError as e:
        logger.error(f"Pandas error in merging data for {symbol}: {e}")
        raise
    except OSError as e:
        logger.error(f"IO error in saving data for {symbol}: {e}")
        raise

    return combined_df


def _intraday_loop(
    symbol: str,
    existing_data: pd.DataFrame,
    missing_months: set[str],
    file_path: Path,
    rate_lim_per_min: int = 5,
    incremental_save: bool = True,
) -> pd.DataFrame:
    """
    Executes a loop to fetch intraday data for each month where data is missing, respecting API rate limits.

    This function iterates through a list of months for which intraday data is missing and makes API requests to fetch the data. It respects the specified rate limit and optionally saves the data incrementally.

    Args:
        symbol (str): The stock symbol for which the data is being fetched.
        existing_data (pd.DataFrame): DataFrame containing the existing intraday data.
        missing_months (Set[str]): A list of months (in 'YYYY-MM' format) for which intraday data needs to be fetched.
        file_path (Path): The file path where the updated data will be saved.
        rate_lim_per_min (int): The maximum number of API requests allowed per minute.
        incremental_save (bool): If True, saves the data incrementally during the fetching process.

    Returns:
        pd.DataFrame: DataFrame updated with the newly fetched intraday data.

    Raises:
        Exception: For any errors encountered during the API request or data processing.

    This function is a key part of the process to ensure that intraday stock data is comprehensive and up-to-date.
    """
    logger.info(f"Starting intraday request loop for {symbol}...")

    # Setup params for API call
    req_params: dict[str, str] = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "adjusted": "true",
        "extended_hours": "true",
        "output_size": "full",
        "datatype": "json",
        "month": "",  # Will be replaced/set in loop
    }

    # Need these sorted descending so we can stop searching the first time the api says date isn't available
    missing_months_descending = sorted(missing_months, reverse=True)
    cur_month_str = datetime.now().strftime("%Y-%m")
    new_data: dict = {}

    for month_str in tqdm(missing_months_descending):
        # Wait to stay under api rate limit
        if len(new_data) >= 2:
            sleep(60 / rate_lim_per_min)

        req_params["month"] = month_str
        logger.info(f"Fetching intraday data for {symbol} in {month_str}.")

        try:
            data = _make_alpha_vantage_request(req_params)
            # If data successfully received for month_str
            if "Time Series (1min)" in data:
                # Has the month completed so we know we have all the data?
                _month_data_complete = int(month_str < cur_month_str)
                for ts, ohlcv in data["Time Series (1min)"].items():
                    ohlcv["month_data_complete"] = _month_data_complete
                    ohlcv["earliest_datum"] = 0
                    new_data[ts] = ohlcv
                if new_data and incremental_save:
                    _merge_and_save_intraday(
                        symbol,
                        existing_data,
                        new_data,
                        file_path,
                    )
            # len(new_data) here makes sure that we've had at least one successful call to the api
            # this rules out that the api call is invalid for some other reason
            # unfortunately, AV doesn't just tell us no data is available for such months
            elif len(new_data) and "Error Message" in data and "Invalid API call" in data["Error Message"]:
                # Looks like this month of data isn't available.
                # Likely that means there is no more data available for this symbol.
                logger.warning(
                    f"No data available for {symbol} in {month_str}.",
                )
                new_data[min(new_data)]["earliest_datum"] = 1
                break
            else:
                raise ParseError(
                    f"Error parsing intraday data for {symbol} in {month_str}. Data received:\n{data}",
                )
        except Exception as e:
            logger.error(
                f"Error during API request for {symbol} in {month_str}: {e}",
            )
            raise

    logger.info(f"Finished fetching {symbol} intraday data.")

    # Merge and save any changes
    if new_data:
        return _merge_and_save_intraday(symbol, existing_data, new_data, file_path)
    return existing_data


def _process_intraday_date_range(
    today: date,
    earliest_start_date: date,
    date_range: pd.DatetimeIndex | None = None,
    existing_data: pd.DataFrame | None = None,
) -> pd.DatetimeIndex:
    """
    Processes and validates the start and end dates for fetching intraday stock data.

    This internal function ensures that the start and end dates for intraday data retrieval are within acceptable ranges and adjusts them if necessary based on the available data.

    Args:
        today (date): The current date.
        earliest_start_date (date): The earliest possible start date for data retrieval.
        date_range (pd.date_range | None): The date range for data retrieval. Defaults to the earliest available date through current date inclusive if None.
        existing_data (pd.DataFrame | None): Existing data to check for the earliest datum available.

    Returns:
        pd.date_range: The adjusted and validated date range for data retrieval.

    Raises:
        ValueError: If the provided dates are outside the permissible range or if there are inconsistencies with the existing data.

    This function plays a critical role in ensuring the correctness and completeness of the data retrieval process for intraday stock analysis.
    """
    start_date = date_range.min() if date_range else earliest_start_date
    if start_date < earliest_start_date:
        raise ValueError(
            f"start date {start_date} cannot be before earliest_start_date {earliest_start_date}",
        )

    end_date = date_range.max() if date_range else today
    if end_date > today:
        raise ValueError(f"end date {end_date} cannot be a future date")

    # Make sure start date isn't prior to earliest datum available on AV
    if existing_data is not None:
        if not isinstance(existing_data, pd.DataFrame):
            raise TypeError("existing_data must be a pandas DataFrame")

        if "earliest_datum" in existing_data.columns:
            earliest_datum_date = existing_data[existing_data["earliest_datum"] == 1].index.min().date()
            start_date = max(start_date, earliest_datum_date)
        else:
            raise ValueError(
                "'earliest_datum' column not found in existing_data",
            )

    return pd.date_range(start_date, end_date)


def get_time_series_intraday(
    symbol: str,
    date_range: pd.DatetimeIndex | None = None,
    time_range: DailyTimeRange | None = None,
    incremental_save: bool = True,
    rate_lim_per_min: int = 5,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    """
    Retrieves and processes intraday stock data for a specified symbol, within a given date and time range.

    This function is designed to fetch intraday stock market data, which includes price and volume information at minute-level intervals throughout the trading day. It handles the identification of missing data, respects API rate limits during data fetching, and can incrementally save the data to a specified directory.

    Args:
        symbol (str): The stock symbol for which the intraday data is being fetched, e.g., 'AAPL' for Apple Inc.
        date_range (pd.date_range | None): The date range for data. Defaults to the earliest available date through current date inclusive if None.
        time_range (DailyTimeRange | None): The time range for data. Defaults to market open (9:30 AM) through market close (4:00 PM) inclusive if none.
        incremental_save (bool | None): If True, saves data incrementally during the data fetching process. Defaults to True.
        rate_lim_per_min (int | None): The maximum number of API requests allowed per minute. Defaults to 5.
        check_update (bool | None): If True, checks for an update to the data. Defaults to False.
        force_update (bool | None): If True, forces a fresh retrieval of the data, ignoring any cached results. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame containing the fetched intraday stock data for the specified symbol, within the given date and time range.

    Raises:
        ValueError: If start_date is before the earliest_start_date or end_date is in the future.
        Exception: For any errors encountered during data fetching or processing.

    Example:
        >>> intraday_data = get_intraday("SPY")
        >>> print(intraday_data.head())
    """
    logger.info(f"Fetching intraday data for symbol: {symbol}")

    api_data_start_date = date(2000, 1, 1)
    symbol = symbol.upper()
    today = date.today()

    if time_range is None:
        time_range = DailyTimeRange(time(9, 30), time(16, 0))

    # Validate and set date ranges
    date_range = _process_intraday_date_range(today, api_data_start_date, date_range)
    start_date = date_range.min().date()  # type: ignore
    end_date = date_range.max().date()  # type: ignore

    # Setup paths
    save_dir: Path = ALPHA_VANTAGE_DATA_DIR / "time_series_intraday"
    file_path = Path(save_dir) / f"{symbol}_intraday.parquet"

    # Load any saved existing data
    existing_data: pd.DataFrame = load_dataframe(file_path, raise_exception=False)
    # Check if we should fetch data
    if not any([check_update, existing_data.empty, force_update]):
        logger.info(f"Using existing data for symbol: {symbol}")
        full_data = existing_data
    else:
        # Get set of months missing/incomplete from existing_data
        # Using an empty df will return all months as missing
        missing_months = _get_missing_intraday_months(
            pd.DataFrame() if force_update else existing_data,
            start_date,
            end_date,
        )

        # Get any missing data by looping from end_month back until start month or until api errors
        full_data = _intraday_loop(
            symbol=symbol,
            existing_data=existing_data,
            missing_months=missing_months,
            file_path=file_path,
            rate_lim_per_min=rate_lim_per_min,
            incremental_save=incremental_save,
        )

    logger.info(f"Intraday data retrieval complete for symbol: {symbol}")

    # return data trimmed to specified start/end date and time (extended hours)
    trimmed_df = filter_by_date(df=full_data, start_date=start_date, end_date=end_date)
    trimmed_df = filter_by_time(df=trimmed_df, start_time=time_range.start, end_time=time_range.end)

    return pd.DataFrame(trimmed_df)


if __name__ == "__main__":
    # Example usage
    data = get_time_series_intraday("SPY")
    print(data)
