"""Core utilities for Bureau of Labor Statistics (BLS) API integration.

Provides base functionality for BLS API calls including:
    - Request parameter preparation and validation
    - Data conversion from BLS JSON format to pandas Series
    - File update detection to avoid unnecessary API calls
    - Incremental data fetching for long time ranges (20-year chunks)
    - Caching and parquet persistence

BLS API provides:
    - Consumer Price Index (CPI) data
    - Employment and unemployment statistics
    - Producer Price Index (PPI) data
    - Other economic indicators

API Documentation: https://www.bls.gov/developers/
"""

import datetime
from pathlib import Path

import pandas as pd

from finbot.config import settings_accessors
from finbot.utils.file_utils.are_files_outdated import are_files_outdated
from finbot.utils.pandas_utils.load_dataframes import load_dataframes
from finbot.utils.pandas_utils.save_dataframes import save_dataframes
from finbot.utils.request_utils.request_handler import RequestHandler
from finbot.utils.validation_utils.validation_helpers import validate_types


def _convert_bls_data_to_series(data: list[dict[str, str]]) -> pd.Series:
    """
    Convert a list of dictionaries to a pandas Series with timestamp index.

    :param data: List of dictionaries with 'year', 'period', 'periodName', 'value', and 'footnotes'.
    :return: pandas Series with the value and timestamp index.
    """

    records = [(f"{d['year']}-{d['period'][1:]}", d["value"]) for d in data]
    df = pd.DataFrame(records, columns=["date", "value"])

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m")
    df.set_index("date", inplace=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    squeezed = df.squeeze()
    if isinstance(squeezed, pd.Series):
        return squeezed
    return pd.Series(squeezed, index=df.index)


def _prep_params(
    series_ids: str | list[str],
    start_date: datetime.date | None,
    end_date: datetime.date | None,
) -> list[str]:
    if isinstance(series_ids, str):
        series_ids = [series_ids]

    # If this proves limiting, we can break up the series IDs into chunks of 50 and make multiple requests.
    if len(series_ids) > 50:
        raise ValueError("Maximum 50 series IDs allowed per request.")

    if isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date) and end_date < start_date:
        raise ValueError("End date cannot be before start date.")

    return series_ids


def _get_ids_to_update(ids_paths_dict: dict[str, Path], force_update: bool) -> list[str]:
    immutable_ids = tuple(ids_paths_dict.keys())

    if force_update:
        return list(immutable_ids)

    immutable_paths = tuple([ids_paths_dict[i] for i in immutable_ids])

    outdated_mask = are_files_outdated(
        file_paths=immutable_paths,
        analyze_pandas=True,
        align_to_period_start=False,
        raise_error=False,
    )

    if len(outdated_mask) != len(ids_paths_dict):
        raise ValueError("Length of outdated_mask does not match length of file_paths.")

    return [immutable_ids[i] for i, outdated in enumerate(outdated_mask) if outdated]


def _request_bls_data(series_ids: list[str]) -> dict[str, pd.DataFrame]:
    headers = {"Content-type": "application/json"}
    series_partial_dfs = []
    current_year = datetime.datetime.now().year
    start_year = current_year

    # TODO: Right now this pulls all the data even if only the last month is needed.
    while True:
        end_year = start_year - 19
        params = {
            "seriesid": series_ids,
            "startyear": str(end_year),
            "endyear": str(start_year),
            "registrationkey": settings_accessors.get_us_bureau_of_labor_statistics_api_key(),
        }

        res_data = RequestHandler().make_json_request(
            url="https://api.bls.gov/publicAPI/v2/timeseries/data/",
            payload_kwargs={"json": params},
            headers=headers,
            request_type="POST",
            timeout=(10, 45),
        )

        # The seriesID is expected to be the header by other logic in this module.
        cur_series_df = pd.DataFrame(
            {d["seriesID"]: _convert_bls_data_to_series(d["data"]) for d in res_data["Results"]["series"]},
        )

        if cur_series_df.empty or str(end_year) not in pd.DatetimeIndex(cur_series_df.index).strftime("%Y").tolist():
            break

        series_partial_dfs.append(cur_series_df)
        start_year = end_year - 1

    combined_df = pd.concat(series_partial_dfs, axis=0).drop_duplicates().dropna(axis=0, how="all").sort_index()
    data_dict = {s_id: pd.DataFrame(combined_df[s_id]).drop_duplicates().dropna().sort_index() for s_id in series_ids}
    return data_dict


def _save_updated_data(updated_data: dict[str, pd.DataFrame], ids_paths_dict: dict[str, Path], save_dir: Path) -> None:
    validate_types(updated_data, "updated_data", [dict])
    if not updated_data:
        return

    immutable_ids = tuple(updated_data.keys())
    id_paths = tuple([ids_paths_dict[i] for i in immutable_ids])
    id_dfs = [updated_data[i].dropna() for i in immutable_ids]

    save_dataframes(dataframes=id_dfs, file_paths=id_paths, save_dir=save_dir)


def _load_bls_data(symbols_to_load: list[str], symbol_paths_dict: dict[str, Path]) -> pd.DataFrame:
    if not symbols_to_load:
        return pd.DataFrame()

    try:
        immutable_symbols = tuple(symbols_to_load)
        immutable_paths = tuple(symbol_paths_dict[i] for i in immutable_symbols)
        loaded_dfs = load_dataframes(file_paths=immutable_paths)

        # Check to make sure the order of the loaded_dfs matches the order of the immutable_ids
        # This isn't actually needed since we merge all the dataframes into one, but it's a good check.
        if any(loaded_dfs[i].columns[0] != immutable_symbols[i] for i in range(len(immutable_symbols))):
            raise ValueError("Loaded DataFrames do not match the order of the requested IDs.")

        merged_df = (
            pd.concat(
                loaded_dfs,
                axis=1,
            )
            if loaded_dfs
            else pd.DataFrame()
        )

        return merged_df
    except KeyError as e:
        raise KeyError(f"Missing symbol data or path for: {e}") from e
