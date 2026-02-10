from __future__ import annotations

import concurrent.futures
import datetime
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

from config import Config, logger
from constants.path_constants import YFINANCE_DATA_DIR
from finbot.utils.file_utils.are_files_outdated import are_files_outdated
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.load_dataframes import load_dataframes
from finbot.utils.pandas_utils.save_dataframes import save_dataframes
from finbot.utils.pandas_utils.sort_dataframe_columns import sort_dataframe_multiindex

MAX_THREADS = Config.MAX_THREADS


def _get_yf_req_params(**kwargs) -> dict[str, str | bool | None]:
    """
    Construct a dictionary of parameters for Yahoo Finance API requests,
    applying defaults where necessary.

    Keyword Arguments:
    - period (str): The time period for the data. Default is "max".
    - interval (str): The interval between data points. Default is "1d".
    - start (str or datetime): The start date for the data. Default is "1000-01-01".
    - end (str or datetime): The end date for the data. Default is "3000-01-01".
    - prepost (bool): Whether to include pre and post market data. Default is True.
    - auto_adjust (bool): Whether to adjust the data for dividends and stock splits. Default is True.
    - actions (bool): Whether to include stock dividends and stock splits events. Default is True.
    - proxy (str or None): The proxy URL to use for the request. Default is None.
    - progress (bool): Whether to show progress while downloading. Default is True.
    - group_by (str): The grouping method for multi-symbol download. Default is "ticker".
    - threads (bool): Whether to use multiple threads for downloading. Default is True.


    Keyword Arguments:
    - Various parameters are accepted (e.g., period, interval, start, end, etc.).

    Returns:
    Dict[str, Union[str, bool, datetime.date]]: A dictionary containing the Yahoo Finance API request parameters.
    """
    params: dict[str, str | bool | None] = {
        "period": "max",  # 1d, 5d, 1wk, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        # "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
        "interval": "1d",
        "start": "1900-01-01",  # "YYYY-MM-DD" string or datetime
        # "YYYY-MM-DD" string or datetime
        "end": str(datetime.date.today().strftime("%Y-%m-%d")),
        "prepost": False,  # YF Default is False
        "auto_adjust": False,  # YF Default is True for symbol and False for multi-symbol download
        # YF Default is True (Downloads stock dividends and stock splits events)
        "actions": True,
        "proxy": None,  # YF Default is None
        "progress": True,  # YF Default is True
        # There are for multi-symbol download
        "group_by": "ticker",  # group by symbol or column
        "threads": True,  # YF Default is True
    }
    params.update(kwargs)
    return params


def _map_yf_time_strs_to_relativedelta(time_str: str) -> relativedelta:
    letters = "".join([i for i in time_str if not i.isdigit()]).lower()
    numbers = int("".join([i for i in time_str if i.isdigit()]))

    func_map = {
        "m": relativedelta(minutes=numbers),
        "h": relativedelta(hours=numbers),
        "d": relativedelta(days=numbers),
        "wk": relativedelta(weeks=numbers),
        "mo": relativedelta(months=numbers),
        "q": relativedelta(months=3 * numbers),
        "y": relativedelta(years=numbers),
    }

    if letters not in func_map:
        raise ValueError(
            f"Invalid time string: {time_str}. Must be one of {list(func_map.keys())}",
        )

    return func_map[letters]


def _prep_params(
    symbols: Sequence[str] | str,
    start_date: datetime.date | datetime.datetime,
    end_date: datetime.date | datetime.datetime | None,
    interval: str,
    request_type: str,
) -> tuple[list[str], datetime.date, datetime.date]:
    """
    Validate and prepare parameters for Yahoo Finance data requests.

    Args:
    symbols (List[str] | str): List of symbols or a single symbol.
    start_date (datetime.date | datetime.datetime): Start date for data retrieval.
    end_date (None | datetime.date | datetime.datetime): End date for data retrieval. If None, defaults to today.
    interval (str): The frequency of data points (e.g., '1d' for daily).
    request_type (str): Type of data request ('history' or 'info').

    Returns:
    Tuple[List[str], datetime.date, datetime.date, Dict[str, Path]]: A tuple containing the processed list of symbols, start date, end date, and a dictionary mapping symbols to file paths.
    """
    symbols = (
        [symbols.upper()]
        if isinstance(
            symbols,
            str,
        )
        else sorted({s.upper() for s in symbols})
    )
    start_date = (
        start_date.date()
        if isinstance(
            start_date,
            datetime.datetime,
        )
        else start_date
    )
    end_date = datetime.date.today() if end_date is None else end_date
    end_date = (
        end_date.date()
        if isinstance(
            end_date,
            datetime.datetime,
        )
        else end_date
    )
    valid_intervals = {
        None,
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    }
    if interval not in valid_intervals:
        raise ValueError(
            f"interval: {interval} must be one of {valid_intervals}",
        )
    valid_req_types = {"history", "info"}
    if request_type not in valid_req_types:
        raise ValueError(
            f"request_type: {request_type} must be one of {valid_req_types}",
        )
    return symbols, start_date, end_date


def _request_yfinance_info(symbols: Sequence[str]) -> pd.DataFrame:
    """
    Fetch and aggregate information data for a list of symbols using Yahoo Finance.

    Args:
    symbols (List[str]): A list of symbols to fetch information for.

    Returns:
    pd.DataFrame: A DataFrame where each column represents a symbol and rows contain various information attributes.
    """
    logger.info(f"Fetching info data for {symbols}")

    def fetch_info(symbol: str) -> dict[str, Any]:
        return yf.Ticker(symbol).info

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = list(
            tqdm(executor.map(fetch_info, symbols), total=len(symbols)),
        )

    res_dict = {t: result for t, result in zip(symbols, results, strict=False)}
    df = pd.DataFrame.from_dict(res_dict, orient="index").transpose()

    # Convert mixed-type columns to string
    for col in df.columns:
        if df[col].apply(lambda x: str(type(x))).nunique() > 1:  # If mixed types
            df[col] = df[col].astype(str)

    return df


def _request_yfinance_history(symbols: Sequence[str], interval: str) -> pd.DataFrame:
    """
    Fetch historical data for a list of symbols from Yahoo Finance.

    Args:
    symbols (List[str]): List of symbols.
    interval (str): Data interval (e.g., '1d' for daily).

    Returns:
    pd.DataFrame: A DataFrame containing the historical data for the specified symbols.
    """
    logger.info(f"Fetching price history for {symbols}")
    default_params = _get_yf_req_params(interval=interval)
    # Request data from Yahoo Finance
    res_df = yf.download(tickers=symbols, **default_params)
    # If "Adj Close" and "Close" are both column names, rename "Close" to "Unadj Close" to avoid confusion
    if "Adj Close" in res_df.columns and "Close" in res_df.columns:
        res_df.rename(columns={"Close": "Unadj Close"}, inplace=True)
    if not isinstance(res_df.columns, pd.MultiIndex):
        res_df.columns = pd.MultiIndex.from_product([symbols, res_df.columns])
    return res_df


def _request_yfinance_data(symbols: Sequence[str], interval: str, request_type: str) -> pd.DataFrame:
    """
    Requests Yahoo Finance data based on the given symbols, interval, and request type.

    Args:
        symbols (List[str]): List of symbols.
        interval (str): Interval for the data (e.g., "1d" for daily, "1h" for hourly).
        request_type (str): Type of request ("info" for company information, "history" for historical data).

    Returns:
        pd.DataFrame: DataFrame containing the requested data.
    """

    if request_type == "info":
        return _request_yfinance_info(symbols)
    return _request_yfinance_history(symbols, interval)


def _save_updated_data(updated_data: pd.DataFrame, file_paths: dict[str, Path], to_update: Sequence[str]) -> None:
    """
    Save updated data for specified symbols to their respective file paths.

    Args:
        updated_data (pd.DataFrame): DataFrame containing updated data for all symbols.
        file_paths (Dict[str, Path]): Dictionary mapping symbols to file paths.
        to_update (List[str]): List of symbols whose data needs to be saved.

    Raises:
        KeyError: If a symbol in to_update is not found in updated_data or file_paths.
    """
    # If there is no updated data or nothing to get, return
    if not to_update or updated_data.empty:
        return

    try:
        symbol_names = tuple(to_update)  # immutable
        symbol_paths = tuple(file_paths[s] for s in symbol_names)  # immutable
        symbol_datas = tuple(updated_data[s].dropna() for s in symbol_names)  # immutable

        save_dataframes(dataframes=symbol_datas, file_paths=symbol_paths)
    except KeyError as e:
        # Handle the case where a symbol is missing in updated_data or file_paths
        raise KeyError(f"Missing symbol data or path for: {e}") from e


def _load_yfinance_data(symbols_to_load: Sequence[str], file_paths: dict[str, Path], request_type) -> pd.DataFrame:
    """
    Load Yahoo Finance data from local files, if available, for given symbols.

    Args:
    symbols_to_load (List[str]): List of symbols to load data for.
    file_paths (Dict[str, Path]): Dictionary mapping symbols to their respective file paths.
    request_type (str): Type of request ('history' or 'info') indicating the nature of data.

    Returns:
    pd.DataFrame: A DataFrame containing the loaded data.
    """
    if not symbols_to_load:
        return pd.DataFrame()

    try:
        symbol_names = tuple(sorted(symbols_to_load))  # immutable
        symbol_paths = tuple(file_paths[s] for s in symbol_names)  # immutable
        symbol_data = load_dataframes(list(symbol_paths))

        # check to make sure the order of the loaded_dfs matches the order of the immutable_ids
        if any(
            [
                isinstance(symbol_data[i], pd.Series) and symbol_data[i].name != symbol_names[i]
                for i in range(len(symbol_names))
            ],
        ):
            raise ValueError("Loaded DataFrames do not match the order of the requested IDs.")

        # This avoids the info double header problems.
        merged_dict = symbol_data
        if request_type != "info":
            merged_dict = {
                name: data
                for name, data in zip(
                    symbol_names,
                    symbol_data,
                    strict=False,
                )
            }

        merged_df = (
            pd.concat(
                merged_dict,
                axis=1,
            )
            if merged_dict
            else pd.DataFrame()
        )
        if request_type != "info" and not isinstance(merged_df.columns, pd.MultiIndex):
            merged_df.columns = pd.MultiIndex.from_product(
                [merged_df.columns, [s for s in symbol_names]],
            )

        return merged_df
    except KeyError as e:
        # Handle the case where a symbol is missing in updated_data or file_paths
        raise KeyError(f"Missing file path for symbol: {e}") from e


def _filter_yfinance_data(
    df: pd.DataFrame,
    start_date: datetime.date,
    end_date: datetime.date,
    interval: str,
    prepost: bool,
) -> pd.DataFrame:
    """
    Apply filters to the Yahoo Finance data based on date range, interval, and market hours.

    Args:
    df (pd.DataFrame): The DataFrame containing Yahoo Finance data.
    start_date (datetime.date): The start date for filtering the data.
    end_date (datetime.date): The end date for filtering the data.
    interval (str): The data interval.
    prepost (bool): Flag to include or exclude pre-post market data.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        return df

    # Filter the data based on the start and end dates
    df = pd.DataFrame(filter_by_date(df, start_date, end_date))

    # Filter the data based on prepost if the interval shorted than daily
    if not prepost and interval.endswith(("s", "m", "h")):
        df = df.loc[(df.index.time >= datetime.time(9, 30)) & (df.index.time <= datetime.time(16, 0))]  # type: ignore

    return df


def _get_files_to_update(
    symbols: list[str],
    file_paths: dict[str, Path],
) -> list[str]:
    """
    Get the list of files to update based on the given symbols, file paths, interval, and force_update flag.

    Args:
        symbols (List[str]): The list of symbols.
        file_paths (Dict[str, Path]): The dictionary mapping symbols to file paths.

    Returns:
        List[Path]: The list of file paths to update.
    """
    # analyzes pandas datetimeindex from the stored .parquet files to see if they are outdated
    fp_immutable = tuple(Path(file_paths[s]) for s in symbols)  # immutable
    outdated = are_files_outdated(
        file_paths=fp_immutable,
        analyze_pandas=True,
        align_to_period_start=False,
        raise_error=False,
    )
    return [s for s, o in zip(symbols, outdated, strict=False) if o]


def get_yfinance_base(
    symbols: Sequence[str] | str,
    request_type: str = "history",
    start_date: datetime.date | datetime.datetime = datetime.date(1900, 1, 1),
    end_date: None | datetime.date | datetime.datetime = None,
    interval: str = "1d",
    prepost: bool = False,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame:
    """
    Fetches and filters Yahoo Finance data for the given symbols.

    Args:
        symbols (List[str] | str): The symbols to fetch data for.
        request_type (str, optional): The type of data to fetch. Defaults to "history".
        start_date (datetime.date | datetime.datetime, optional): The start date of the data range. Defaults to datetime.date(1900, 1, 1).
        end_date (None | datetime.date | datetime.datetime, optional): The end date of the data range. Defaults to None.
        interval (str, optional): The interval of the data. Defaults to "1d".
        prepost (bool, optional): Whether to include pre and post market data. Defaults to False.
        check_update (bool, optional): Whether to check if the data is up to date. Defaults to False.
        force_update (bool, optional): Whether to force update the data even if it's already up to date. Defaults to False.

    Returns:
        pd.DataFrame: The fetched and filtered data.
    """
    # Validate input arguments and prepare parameters
    symbols, start_date, end_date = _prep_params(
        symbols,
        start_date,
        end_date,
        interval,
        request_type,
    )

    # Determine which symbols need to be updated
    file_paths = {s: YFINANCE_DATA_DIR / request_type / f"{s}_{request_type}_{interval}.parquet" for s in symbols}

    if force_update:
        to_update = symbols
    elif not check_update:
        to_update = [sym for sym in symbols if not file_paths[sym].exists()]
    else:
        to_update = _get_files_to_update(
            symbols=symbols,
            file_paths=file_paths,
        )

    # Fetch data for symbols that need to be updated
    updated_data = (
        _request_yfinance_data(
            to_update,
            interval,
            request_type,
        )
        if to_update
        else pd.DataFrame()
    )

    # Save the updated data
    _save_updated_data(updated_data, file_paths, to_update)

    # Load data for symbols that don't need to be updated
    symbols_to_load = sorted(set(symbols) - set(to_update))
    loaded_data = _load_yfinance_data(
        symbols_to_load,
        file_paths,
        request_type,
    )

    # Combine the data
    combined_df = pd.concat([updated_data, loaded_data], axis=1)

    # Filter the data
    filtered_df = _filter_yfinance_data(
        combined_df,
        start_date,
        end_date,
        interval,
        prepost,
    )

    # Sort the data, if it is a multiindex dataframe
    sorted_df = (
        sort_dataframe_multiindex(filtered_df)
        if isinstance(
            filtered_df.columns,
            pd.MultiIndex,
        )
        else filtered_df
    )

    # Remove the outer level of columns if there is only one symbol
    final_df = sorted_df[symbols[0]] if len(symbols) == 1 else sorted_df

    return final_df
