"""Core utilities for Google Sheets-based financial data retrieval.

Provides base functionality for fetching index data from Google Sheets using
the Google Sheets API (v4). Used primarily for ICE U.S. Treasury indexes and
Nasdaq 100 Total Return data that are maintained in shared spreadsheets.

Features:
    - OAuth2 service account authentication
    - Automatic caching to parquet files
    - Update checking based on data freshness
    - Date filtering and validation

Requires:
    - Google Sheets API enabled
    - Service account credentials JSON file
    - GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH environment variable

Google Sheets API documentation: https://developers.google.com/sheets/api
"""

import datetime as dt

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings_accessors
from constants.path_constants import GOOGLE_FINANCE_DATA_DIR
from finbot.utils.datetime_utils.validate_start_end_dates import validate_start_end_dates
from finbot.utils.file_utils.is_file_outdated import is_file_outdated
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def _get_google_sheets_credentials():
    SERVICE_ACCOUNT_FILE = settings_accessors.get_google_finance_service_account_credentials_path()  # noqa: N806 - Constant scoped to function
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]  # noqa: N806 - Constant scoped to function
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials


def _get_google_sheets_service(credentials):
    return build("sheets", "v4", credentials=credentials)


def _process_sheet_response(response) -> pd.DataFrame:
    values = response.get("values", [])

    # Process sheet into dataframe
    df = pd.DataFrame(values)
    df.columns = df.iloc[0].to_numpy().tolist()
    df.drop(axis=0, index=0, inplace=True)
    df.set_index("Date", inplace=True)
    df.index = pd.to_datetime(df.index)
    df.dropna(inplace=True)
    for col_h in df.columns:
        df[col_h] = pd.to_numeric(df[col_h])

    return df


def _get_sheet_df(range_to_get: str) -> pd.DataFrame:
    credentials = _get_google_sheets_credentials()
    service = _get_google_sheets_service(credentials=credentials)
    spreadsheets = service.spreadsheets()

    value_render_option = "FORMATTED_VALUE"
    date_time_render_option = "SERIAL_NUMBER"
    spreadsheet_id = "1QnCXxQakq1bQMFkclx8FC-roTzng2jGTwXf7Q2gSpLI"

    res = spreadsheets.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_to_get,
        valueRenderOption=value_render_option,
        dateTimeRenderOption=date_time_render_option,
    )
    response = res.execute()

    df = _process_sheet_response(response=response)

    return df


def _prep_params(range_to_get, start_date, end_date):
    if not isinstance(range_to_get, str):
        raise TypeError("range_to_get must be a string")

    validate_start_end_dates(start_date=start_date, end_date=end_date, permit_none=True)


def get_sheet_base(
    range_to_get: str,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
) -> pd.DataFrame | pd.Series:
    # Prep params
    _prep_params(range_to_get=range_to_get, start_date=start_date, end_date=end_date)
    file_name_stem = range_to_get.split("!")[0].replace("^", "").replace("$", "").upper()
    file_path = GOOGLE_FINANCE_DATA_DIR / f"{file_name_stem}.parquet"

    # determine outdated data
    if force_update:
        is_outdated = True
    elif not check_update:
        is_outdated = file_path.exists()
    else:
        is_outdated = is_file_outdated(file_path=file_path, analyze_pandas=True, file_not_found_error=False)

    # fetch data if outdated
    if is_outdated:
        df = _get_sheet_df(range_to_get=range_to_get)

        # save newly updated data
        save_dataframe(df=df, file_path=file_path)
    else:
        # load up-to-date data
        load_dataframe(file_path=file_path)

    # filter and sort data
    filtered_df = filter_by_date(df=df, start_date=start_date, end_date=end_date)

    return filtered_df.drop_duplicates().dropna().sort_index()
