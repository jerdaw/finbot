"""Parse DataFrame from API response dictionaries.

Extracts and transforms data from API response dictionaries into pandas
DataFrames. Handles common API response patterns like nested data keys,
transposed data, and date indexing.

Particularly useful for parsing JSON responses from financial data APIs.

Features:
    - Extract data from nested response structures
    - Optional transposition for row-major data
    - Automatic date index setting and sorting
    - Logging for debugging response parsing

Typical usage:
    - Parse FRED API responses
    - Process Alpha Vantage data
    - Transform API JSON to DataFrame
    - Handle various API response formats
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from config import logger


def parse_df_from_res(
    data: dict[str, Any],
    data_key: str = "data",
    transpose_data: bool = False,
    set_index: str = "date",
    sort_index: bool = True,
) -> pd.DataFrame:
    """
    Converts an dictionary like object with a key `key` into a pandas DataFrame.

    Args:
        data (Dict[str, Any]): The API response data.
        data_key (str | None): The key in the 'data' dict where the data is stored. Defaults to 'data'.
        transpose_data (bool | None): Whether to transpose the dataframe. Defaults to False.
        set_index (str | None): Column to set as index. Defaults to 'date'.
        sort_index (bool | None): Whether to sort by the index. Defaults to True.

    Returns:
        pd.DataFrame: The resulting DataFrame.

    Raises:
        KeyError: If data_key is not found in data.keys().
        ValueError: If the specified data header is not found in the data.
        Exception: If unknown or other error in convertion process.
    """
    try:
        if data_key:
            if data_key not in data:
                print(data)
                raise KeyError(
                    f"Expected data key header '{data_key}' not found. Available data_keys: {list(data.keys())}",
                )

            df = pd.DataFrame(data[data_key])
        else:
            df = pd.DataFrame(data)

        if transpose_data:
            df = df.transpose()
        if set_index and set_index in df.columns:
            df.set_index(set_index, inplace=True)
        if sort_index:
            df.sort_index(inplace=True)
        return df
    except KeyError as e:
        logger.error(f"KeyError in _convert_key_to_df: {e}")
        raise ValueError(str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error in _convert_key_to_df: {e}")
        raise
