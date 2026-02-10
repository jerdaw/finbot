from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config import Config, logger
from constants.api_constants import ALPHA_VANTAGE_API_FUNCTIONS, ALPHA_VANTAGE_RAPI_FUNCTIONS
from constants.path_constants import ALPHA_VANTAGE_DATA_DIR, RESPONSES_DATA_DIR
from finbot.utils.file_utils.is_file_outdated import is_file_outdated
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.parse_df_from_res import parse_df_from_res
from finbot.utils.pandas_utils.save_dataframe import save_dataframe
from finbot.utils.request_utils.request_handler import RequestHandler

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_RAPIDAPI_URL = "https://alpha-vantage.p.rapidapi.com/query"
ALPHA_VANTAGE_RAPIDAPI_HEADERS = {
    "X-RapidAPI-Key": Config.alpha_vantage_api_key,
    "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
}


def _determine_alpha_vantage_api_provider(func_name: str) -> str:
    """
    Determine the appropriate API provider (either RapidAPI or AlphaVantage) for a given function name.

    This function checks whether the specified function name is available in the predefined sets of functions for either RapidAPI or AlphaVantage. It is used to route API requests to the correct provider based on the functionality required.

    Args:
        func_name (str): The name of the function for which the API provider needs to be determined.

    Returns:
        str: A string indicating the API provider. Returns 'rapid' for RapidAPI functions and 'av' for AlphaVantage functions.

    Raises:
        ValueError: If the function name is not recognized as part of either the RapidAPI or AlphaVantage set of functions.

    Example:
        >>> provider = _determine_alpha_vantage_api_provider("TIME_SERIES_DAILY")
        >>> print(provider)
    """
    if func_name.upper() in ALPHA_VANTAGE_RAPI_FUNCTIONS:
        return "rapid"
    if func_name.upper() in ALPHA_VANTAGE_API_FUNCTIONS:
        return "av"
    error_msg = f"Function name {func_name} not found in endpoints."
    logger.error(error_msg)
    raise ValueError(error_msg)


def _make_alpha_vantage_request(
    req_params: dict[str, str],
    save_dir: str | Path | None = RESPONSES_DATA_DIR / "alpha_vantage_api",
    raise_exception: bool = True,
) -> dict[str, Any]:
    """
    Make a request to the AlphaVantage API using specified parameters and retrieve the response data.

    This function determines the appropriate API provider (either AlphaVantage or RapidAPI) based on the function name provided in the request parameters. It supports various configurations like output size, data format, and handles additional query parameters.

    Args:
        req_params (Dict[str, str]): Parameters for the API request including 'function', 'outputsize', 'datatype', and other specific parameters for the AlphaVantage API.
        save_dir (str | Path | None): The directory path where the response data is saved. Defaults to the 'alpha_vantage_api' directory within the RESPONSES_DATA_DIR.
        raise_exception (bool | None): If True, exceptions will be raised in case of request failures. Defaults to True.

    Returns:
        Dict[str, Any]: The response from the API as a dictionary.

    Raises:
        ValueError: If 'function' key is not found in req_params.
        requests.RequestException: For request-related issues.
        RuntimeError: If the function name is invalid or the API provider cannot be determined.

    Example:
        >>> response = _make_alpha_vantage_request({"function": "TIME_SERIES_DAILY", "symbol": "AAPL"})
        >>> print(response)
    """
    if "function" not in req_params:
        raise ValueError(
            "req_params must contain 'function' key and corresponding function name",
        )

    logger.info(
        f"Making request to AlphaVantage API for function: {req_params['function']}",
    )

    # Set default values and process request parameters
    req_params["function"] = req_params["function"].lower()
    req_params["outputsize"] = req_params.get("outputsize", "full").lower()
    req_params["datatype"] = req_params.get("datatype", "full").lower()

    provider = _determine_alpha_vantage_api_provider(req_params["function"])

    # Make the request based on the determined provider
    req_handler = RequestHandler()
    if provider == "rapid":
        return req_handler.make_json_request(
            url=ALPHA_VANTAGE_RAPIDAPI_URL,
            payload_kwargs=dict(params=req_params),
            headers=ALPHA_VANTAGE_RAPIDAPI_HEADERS,
            save_dir=save_dir,
        )
    if provider == "av":
        req_params["apikey"] = str(Config.alpha_vantage_api_key)
        return req_handler.make_json_request(
            url=ALPHA_VANTAGE_API_URL,
            payload_kwargs=dict(params=req_params),
            save_dir=save_dir,
        )
    logger.error(f"Invalid function name provided: {req_params['function']}")
    raise RuntimeError("Unable to determine AlphaVantage API provider.")


def _prep_params(req_params: dict[str, str], save_dir: Path | None = None) -> tuple[dict[str, str], Path]:
    """
    Validates the request parameters and sets default values for file_name.

    Args:
        req_params (dict[str, str]): The request parameters.
        save_dir (Path | None, optional): The directory to save the file. Defaults to None.

    Returns:
        Tuple[dict[str, str], Path]: A tuple containing the validated request parameters and the save directory.

    Raises:
        ValueError: If 'function' key is missing in req_params or if file_name does not end with '.parquet'.

    Example:
        >>> req_params = {
        ...     "function": "TIME_SERIES_DAILY",
        ...     "symbol": "AAPL",
        ...     "interval": "1min",
        ...     "file_name": "aapl_daily.parquet",
        ... }
        >>> save_dir = Path("/data")
        >>> _prep_params(req_params, save_dir)
        ({'function': 'time_series_daily', 'symbol': 'AAPL', 'interval': '1min', 'file_name': 'aapl_daily.parquet'}, Path('/data/time_series_daily'))

    """
    if "function" not in req_params:
        raise ValueError(
            "req_params must contain 'function' key and corresponding function name",
        )
    req_params["function"] = req_params["function"].lower()
    func_name = req_params["function"]  # Earier to reference
    req_params["file_name"] = req_params.get("file_name", "").lower()
    if not req_params["file_name"]:
        symbol = req_params.get("symbol", "").upper()
        interval = req_params.get("interval", "")
        maturity = req_params.get("maturity", "")
        req_params[
            "file_name"
        ] = f"{symbol + '_' if symbol else ''}{maturity + '_' if maturity else ''}{func_name}{f'_{interval}' if interval else ''}.parquet".lower()
    elif not req_params["file_name"].endswith(".parquet"):
        raise ValueError("file_name must end with '.parquet'")
    if save_dir is None:
        save_dir = Path(ALPHA_VANTAGE_DATA_DIR / func_name)
    return req_params, save_dir


def _request_and_parse(
    req_params: dict[str, str],
    parse_res_params: dict[str, str | bool] | None = None,
) -> pd.DataFrame:
    # Make request and parse response
    response = _make_alpha_vantage_request(req_params=req_params)
    parse_res_params = parse_res_params or {}
    data_df = parse_df_from_res(
        data=response,
        data_key=str(parse_res_params.get("data_key", "data")),
        transpose_data=bool(parse_res_params.get("transpose_data", False)),
        set_index=str(parse_res_params.get("set_index", "date")),
        sort_index=bool(parse_res_params.get("sort_index", True)),
    )
    return data_df


def get_avapi_base(
    req_params: dict,
    parse_res_params: dict[str, str | bool] | None = None,
    check_update: bool = False,
    force_update: bool = False,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Retrieve data from the AlphaVantage API, convert it to a pandas DataFrame, and optionally save it. This function is designed to simplify the process of obtaining and handling financial data from AlphaVantage.

    Args:
        req_params (Dict): Required parameters for the _make_alpha_vantage_request API request. Must include the 'function' key with the name of the AlphaVantage API function.
        parse_res_params (Dict[str, str | bool] | None): Parameters to parse_df_from_res for parsing the API response. Defaults to None.
        check_update (bool): If True, the function checks if the data is outdated before fetching new data. Defaults to False.
        force_update (bool): If True, the function fetches new data irrespective of the data's age. Defaults to False.
        save_dir (Path | None): The directory path where the retrieved data should be saved. If None, the data is not saved. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the data retrieved from the AlphaVantage API.

    Raises:
        ValueError: If 'function' key is not found in req_params.
        Exception: For any other exceptions that occur during the data retrieval or processing.

    Note:
        - The function constructs the file name for saving data based on provided parameters like symbol, interval, maturity, and function name.
        - Data freshness is evaluated based on the update_time_period and the latest available data file.

    Example:
        >>> api_data = _get_avapi_simple(
        ...     req_params={"function": "TIME_SERIES_DAILY", "symbol": "AAPL"},
        ...     update_time_period="daily",
        ... )
        >>> print(api_data.head())
    """

    # Validate input arguments and prepare parameters
    req_params, save_dir = _prep_params(req_params, save_dir)

    # Check if update is required
    file_path = save_dir / req_params["file_name"]
    do_update = (
        force_update
        or not Path(file_path).exists()
        or (check_update and is_file_outdated(file_path=file_path, analyze_pandas=True))
    )

    # Fetch data and save if required
    if do_update:
        data_df = _request_and_parse(
            req_params=req_params,
            parse_res_params=parse_res_params,
        )
        save_dataframe(
            df=data_df,
            save_dir=save_dir,
            file_name=req_params["file_name"],
        )
        return data_df

    # Load data from file if update wasn't performed
    return load_dataframe(file_path)
