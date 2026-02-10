from __future__ import annotations

import datetime
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
import pandas_datareader as pdr

from config import Config, logger
from constants.path_constants import DATA_DIR
from finbot.utils.file_utils.are_files_outdated import are_files_outdated
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.load_dataframes import load_dataframes
from finbot.utils.pandas_utils.save_dataframes import save_dataframes

MAX_THREADS = Config.MAX_THREADS


def _get_pdr_req_params(**kwargs) -> dict[str, Any]:
    """
    Get the request parameters for the Pandas DataReader function.

    Args:
        **kwargs: Additional keyword arguments to override the default parameters.

    Returns:
        dict[str, any]: The request parameters.

    """
    params = {
        "symbols": [],
        "start": datetime.date(1800, 1, 1),
        "end": datetime.date.today(),
        "retry_count": 3,
        "pause": 0.1,
        "timeout": 30,
        "session": None,
        "freq": None,
    }
    params.update(kwargs)
    return params


def _prep_params(
    symbols: list[str] | str,
    start_date: None | datetime.date | datetime.datetime,
    end_date: None | datetime.date | datetime.datetime,
    save_dir: Path | str,
) -> tuple[list[str], datetime.date | None, datetime.date, Path]:
    """
    Prepare the parameters for fetching FRED data.

    Args:
        symbols (list[str] | str): The symbols to fetch data for.
        start_date (datetime.date | datetime.datetime): The start date of the data.
        end_date (None | datetime.date | datetime.datetime): The end date of the data.
        save_dir (Path | str): The directory to save the fetched data.

    Returns:
        tuple[list[str], datetime.date | None, datetime.date, Path]: The prepared parameters.
    """
    symbols = (
        [symbols.upper()]
        if isinstance(
            symbols,
            str,
        )
        else sorted({s.upper() for s in symbols})
    )
    if start_date is not None:
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
    save_dir = Path(save_dir)
    if DATA_DIR not in save_dir.parents:
        raise ValueError(f"save_dir must be a subdirectory of {DATA_DIR}")
    save_dir.mkdir(parents=True, exist_ok=True)
    return symbols, start_date, end_date, save_dir


def _request_pdr_data(pdr_reader_class, symbols: Sequence[str]) -> pd.DataFrame:
    """
    Fetches data for the given symbols using the specified PDR reader class.

    Args:
        pdr_reader_class: The PDR reader class to use for fetching data.
        symbols: A list of symbols for which data needs to be fetched.

    Returns:
        A pandas DataFrame containing the fetched data.
    """
    logger.info(f"Fetching data for {len(symbols)} symbols: {symbols}")
    system_params = _get_pdr_req_params(symbols=symbols)
    PdrReader = pdr_reader_class(**system_params)
    return PdrReader.read()


def _save_updated_data(updated_data: pd.DataFrame, file_paths: dict[str, Path], to_update: Sequence[str]) -> None:
    """
    Save the updated data for the specified symbols to their respective file paths.

    Args:
        updated_data (pd.DataFrame): The updated data to be saved.
        file_paths (dict[str, Path]): A dictionary mapping symbols to their file paths.
        to_update (list[str]): A list of symbols to update.

    Raises:
        KeyError: If a symbol in `to_update` is not found in `file_paths`.

    Returns:
        None
    """
    if updated_data.empty or not to_update:
        return

    try:
        symbol_names = tuple(to_update)  # immutable
        symbol_paths = tuple(file_paths[symbol] for symbol in to_update)  # immutable
        symbol_data = tuple(updated_data[s].dropna() for s in symbol_names)  # immutable

        save_dataframes(dataframes=symbol_data, file_paths=symbol_paths)
    except KeyError as e:
        raise KeyError(f"Missing symbol data or path for: {e}") from e


def _load_pdr_data(symbols_to_load: Sequence[str], file_paths: dict[str, Path]) -> pd.DataFrame:
    """
    Load PDR data for the given symbols from the specified file paths.

    Args:
        symbols_to_load (list[str]): List of symbols to load data for.
        file_paths (dict[str, Path]): Dictionary mapping symbols to file paths.

    Returns:
        pd.DataFrame: Merged dataframe containing the loaded data.

    Raises:
        KeyError: If symbol data or path is missing for any symbol.
    """
    if not symbols_to_load:
        return pd.DataFrame()

    try:
        symbol_names = tuple(sorted(symbols_to_load))  # immutable
        symbol_paths = tuple(file_paths[symbol] for symbol in symbol_names)  # immutable
        symbol_data = load_dataframes(
            file_paths=list(symbol_paths),
        )  # immutable

        # check to make sure the order of the loaded_dfs matches the order of the immutable_ids
        if any(
            [
                (symbol_data[i].name if isinstance(symbol_data[i], pd.Series) else symbol_data[i].columns[0])
                != symbol_names[i]
                for i in range(len(symbol_names))
            ],
        ):
            raise ValueError("Loaded DataFrames do not match the order of the requested IDs.")

        merged_df = (
            pd.concat(
                symbol_data,
                axis=1,
            )
            if symbol_data
            else pd.DataFrame()
        )

        return merged_df
    except KeyError as e:
        raise KeyError(f"Missing symbol data or path for: {e}") from e


def _get_files_to_update(
    symbols: list[str],
    file_paths: dict[str, Path],
) -> list[str]:
    """
    Determines the files that need to be updated based on the given symbols, file paths, update intervals, and force update flag.

    Args:
        symbols (list[str]): The symbols to update.
        file_paths (dict[str, Path]): The file paths corresponding to the symbols.

    Returns:
        list[Path]: The list of file paths that need to be updated.
    """
    # update_intervals analyzes pandas datetimeindex from the stored .parquet files to see if they are outdated
    fp_immutable = tuple(file_paths[s] for s in symbols)  # immutable
    outdated_mask = are_files_outdated(
        file_paths=fp_immutable,
        analyze_pandas=True,
        align_to_period_start=False,
        raise_error=False,
    )
    return [s for s, o in zip(symbols, outdated_mask, strict=False) if o]


def get_pdr_base(
    symbols: list[str] | str,
    save_dir: Path | str,
    pdr_reader_class: pdr.base._BaseReader,
    start_date: None | datetime.date | datetime.datetime = None,
    end_date: None | datetime.date | datetime.datetime = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Fetches and combines data from various sources for the given symbols.

    Args:
        symbols (list[str] | str): The symbols to fetch data for.
        save_dir (Path | str): The directory to save the data.
        pdr_reader_class (pdr.base._BaseReader): The Pandas DataReader class to use for fetching data.
        start_date (datetime.date | datetime.datetime, optional): The start date for the data. Defaults to None.
        end_date (None | datetime.date | datetime.datetime, optional): The end date for the data. Defaults to None.
        check_update (bool, optional): Whether to check if the data is up to date before fetching it. Defaults to False.
        force_update (bool, optional): Whether to force update the data. Defaults to False.

    Returns:
        pd.DataFrame | pd.Series: The combined and sorted data for the given symbols.
    """
    # Validate and prepare parameters
    symbols, start_date, end_date, save_dir = _prep_params(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        save_dir=save_dir,
    )

    # Determine which symbols need to be updated
    file_paths = {s: save_dir / f"{s}.parquet" for s in symbols}

    if force_update:
        to_update = symbols
    elif not check_update:
        to_update = [s for s, fp in file_paths.items() if not fp.exists()]
    else:
        to_update = _get_files_to_update(
            symbols=symbols,
            file_paths=file_paths,
        )

    # Fetch data for symbols that need to be updated
    updated_data = (
        _request_pdr_data(
            pdr_reader_class=pdr_reader_class,
            symbols=to_update,
        )
        if to_update
        else pd.DataFrame()
    )

    # Save updated data
    _save_updated_data(
        updated_data=updated_data,
        file_paths=file_paths,
        to_update=to_update,
    )

    # Load data for symbols that don't need to be updated
    loaded_data = _load_pdr_data(symbols_to_load=tuple(set(symbols) - set(to_update)), file_paths=file_paths)

    # Combine updated and loaded data
    combined_df = pd.concat([updated_data, loaded_data], axis=0)

    # Filter data
    filtered_df = filter_by_date(
        df=combined_df,
        start_date=start_date,
        end_date=end_date,
    )

    # Sort data columns
    sorted_df = filtered_df.sort_index(axis=1)

    # Change index name from "DATE" to "Date"
    sorted_df.index.name = sorted_df.index.name.capitalize()

    return sorted_df
