"""Fetch BLS economic data by series ID.

Main entry point for retrieving Bureau of Labor Statistics time series data
by series ID. Supports batch fetching (up to 50 series at once), automatic
caching, and incremental updates.

Series IDs can be found at: https://www.bls.gov/help/hlpforma.htm

Common series IDs:
    - CUUR0000SA0: CPI for All Urban Consumers (CPI-U)
    - LNS14000000: Unemployment Rate
    - PRS85006092: Business Sector Labor Productivity

Data source: U.S. Bureau of Labor Statistics API
Update frequency: Varies by series (monthly, quarterly, annual)
API endpoint: /timeseries/data/
"""

import datetime

import pandas as pd

from constants.path_constants import BLS_DATA_DIR
from finbot.utils.data_collection_utils.bls._bls_utils import (
    _get_ids_to_update,
    _load_bls_data,
    _prep_params,
    _request_bls_data,
    _save_updated_data,
)
from finbot.utils.pandas_utils.filter_by_date import filter_by_date


def get_bls_data(
    series_ids: str | list[str],
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
):
    """
    Fetches time series data from the BLS API for given series IDs.

    :param series_ids: Single series ID or list of series IDs.
    :param start_date: Start date of the data range.
    :param end_date: End date of the data range.
    :param check_update: Whether to check if the data is up to date before fetching it.
    :param force_update: Whether to force update the data even if it's already up to date.
    :return: Pandas DataFrame with time series data.
    :raises ValueError: If more than 50 series IDs are provided or API request fails.
    """

    series_ids = _prep_params(series_ids=series_ids, start_date=start_date, end_date=end_date)
    save_dir = BLS_DATA_DIR
    ids_paths_dict = {s: save_dir / f"{s}.parquet" for s in series_ids}

    if force_update:
        ids_to_update = series_ids
    elif not check_update:
        ids_to_update = [s for s in series_ids if not ids_paths_dict[s].exists()]
    else:
        ids_to_update = _get_ids_to_update(ids_paths_dict=ids_paths_dict, force_update=force_update)

    updated_data = _request_bls_data(series_ids=ids_to_update) if ids_to_update else {}

    _save_updated_data(updated_data=updated_data, ids_paths_dict=ids_paths_dict, save_dir=save_dir)

    loaded_data_df = _load_bls_data(symbols_to_load=series_ids, symbol_paths_dict=ids_paths_dict)

    updated_data_df = pd.concat([updated_data[s] for s in updated_data], axis=1) if updated_data else pd.DataFrame()

    combined_df = pd.concat([updated_data_df, loaded_data_df], axis=0)

    # Filter data
    filtered_df = filter_by_date(df=combined_df, start_date=start_date, end_date=end_date)

    # set data column to the same order as series_ids and other final things
    sorted_df = filtered_df[series_ids].drop_duplicates().dropna(axis=0, how="all").sort_index()

    return sorted_df


if __name__ == "__main__":
    print(get_bls_data(series_ids=["CUUR0000SA0", "ISU00000000031004"], force_update=True))
