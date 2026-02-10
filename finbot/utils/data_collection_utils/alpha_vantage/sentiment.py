from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
from time import sleep

import pandas as pd
from tqdm.auto import tqdm

from config import Config, logger
from constants.path_constants import ALPHA_VANTAGE_DATA_DIR
from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import _make_alpha_vantage_request
from finbot.utils.datetime_utils.get_latest_us_business_date import get_latest_us_business_date
from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates
from finbot.utils.pandas_utils.filter_by_date import filter_by_date
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe


def _process_sentiment_date_range(
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[datetime, datetime]:
    """
    Processes and validates the start and end dates for sentiment data retrieval, providing default values if necessary.

    This method is used internally to ensure that the start and end dates for sentiment analysis are correctly set up. If the start_date or end_date is not provided, it defaults to a predetermined start date or the current day, respectively. It also ensures that the start_date is not later than the end_date.

    Args:
        start_date (date | None): The starting date for the sentiment data retrieval. If None, defaults to a predetermined earliest available data date.
        end_date (date | None): The ending date for the sentiment data retrieval. If None, defaults to the current day.

    Returns:
        Tuple[datetime, datetime]: A tuple containing the processed start and end datetime objects.

    Raises:
        ValueError: If the start_date is later than the end_date.

    Example:
        >>> start_dt, end_dt = _process_sentiment_date_range(date(2023, 1, 1), date(2023, 1, 31))
        >>> print(start_dt, end_dt)

    Note:
        The start and end dates are converted to datetime objects with the time component set to the start and end of the respective days.
    """
    if not start_date:
        start_date = date(2022, 3, 2)  # Earliest date data available
    if not end_date:
        end_date = date.today()

    if start_date > end_date:
        raise ValueError("start_date cannot be later than end_date.")

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    return start_datetime, end_datetime


def get_sentiment(
    start_date: date | None = None,
    end_date: date | None = None,
    check_update: bool = False,
    force_update: bool = False,
    incremental_save: bool = True,
    rate_lim_per_min: int = 5,
) -> pd.DataFrame:
    """
    Fetches, processes, and saves sentiment data within a specified date range from an API source.

    This function gathers market sentiment data, which provides insights into the mood or tone of market participants towards current market conditions. The sentiment data includes various metrics like relevance score and sentiment score, with definitions provided for interpreting these scores.

    The relevance score is categorized as follows:
        - 0 < x <= 1, with a higher score indicating higher relevance.
    The sentiment score is categorized as follows:
        - x <= -0.35: Bearish
        - -0.35 < x <= -0.15: Somewhat-Bearish
        - -0.15 < x < 0.15: Neutral
        - 0.15 <= x < 0.35: Somewhat_Bullish
        - x >= 0.35: Bullish

    Args:
        start_date (date | None): The start date for the sentiment data retrieval. Defaults to a predetermined start date if None.
        end_date (date | None): The end date for the sentiment data retrieval. Defaults to the current day if None.
        check_update (bool): If True, checks for an update to the data. Defaults to False.
        force_update (bool): If True, forces a fresh retrieval of the data, ignoring any cached results. Defaults to False.
        incremental_save (bool): If True, saves data incrementally during the data retrieval process.
        rate_lim_per_min (int): The rate limit per minute for API requests to avoid hitting API rate limits.

    Returns:
        pd.DataFrame: A DataFrame containing the fetched sentiment data within the specified date range. The DataFrame includes information like published time, title, URL, sentiment scores, etc.

    Raises:
        Exception: If there are issues in fetching the data from the API or in processing the data.

    Example:
        >>> sentiment_df = get_sentiment(start_date=date(2023, 1, 1), end_date=date(2023, 1, 31))
        >>> print(sentiment_df.head())

    Note:
        The sentiment data is fetched in chunks to comply with the rate limit of the API. If an incremental save is enabled, the data is saved after each successful fetch.
    """
    logger.info("Fetching sentiment data")

    # Set date ranges
    process_dates = _process_sentiment_date_range
    start_datetime, end_datetime = process_dates(start_date, end_date)
    start_date = start_datetime.date()
    end_date = get_latest_us_business_date(min_time=time(hour=9, minute=30))

    # Setup paths
    save_dir = Path(ALPHA_VANTAGE_DATA_DIR / "sentiment")
    file_name = "sentiment.parquet"

    # Load any saved existing data
    existing_data = load_dataframe(save_dir / file_name, raise_exception=False)

    if not any([check_update, existing_data.empty, force_update]):
        return pd.DataFrame(filter_by_date(df=existing_data, start_date=start_date, end_date=end_date))

    req_params: dict[str, str] = {
        "function": "NEWS_SENTIMENT",
        "topics": "economy_macro",
        "ticker": "FOREX:USD",
        "time_from": "",
        "time_to": "",
        "sort": "EARLIEST",
        "limit": "1000",
        "apikey": Config.alpha_vantage_api_key,  # type: ignore[dict-item]
    }
    requested_bdates = set(get_us_business_dates(start_date, end_date))
    n_requests = 0
    # Convert to DateTimeIndex if not already
    existing_data.index = pd.to_datetime(existing_data.index)
    existing_dates_set = set() if force_update else set(existing_data.index.date)
    for bdate in tqdm(sorted(requested_bdates - existing_dates_set)):
        if bdate in set(existing_data.index.date):
            continue

        # Wait to stay under api rate limit
        if n_requests >= 2:
            sleep_duration = 60 / rate_lim_per_min
            sleep(sleep_duration)

        cur_start_dt, cur_end_dt = process_dates(bdate, end_date)
        req_params["time_from"] = cur_start_dt.strftime("%Y%m%dT%H%M")
        req_params["time_to"] = cur_end_dt.strftime("%Y%m%dT%H%M")

        logger.info(
            f"Fetching sentiment data starting at {req_params['time_from']}.",
        )
        try:
            data = _make_alpha_vantage_request(req_params=req_params)
            n_requests += 1
        except Exception as e:
            logger.error(f"Error during AVApi sentiment request: {e}")
            raise

        logger.info("Merging fetched data to existing DataFrame")
        try:
            if "feed" not in data:
                logger.warning("No 'feed' key in response, skipping this data")
                continue
            new_data = pd.DataFrame(data["feed"])
            if "time_published" not in new_data.columns:
                logger.warning("No 'time_published' column in response, skipping this data")
                continue
            new_data["datetime_published"] = new_data["time_published"].apply(
                lambda tp: datetime.strptime(tp, "%Y%m%dT%H%M%S"),
            )
            new_data.set_index("datetime_published", inplace=True)
            existing_data = pd.concat([existing_data, new_data])
            if incremental_save:
                existing_data.drop_duplicates(
                    subset=["title", "url", "time_published"],
                    inplace=True,
                )
                existing_data.sort_index(inplace=True)
                save_dataframe(df=new_data, file_path=save_dir / file_name)
        except Exception as e:
            logger.error(
                f"Error merging fetched data to existing dataframe: {e}",
            )
            raise

    logger.info("Finished fetching sentiment data.")

    # Optimize and save full dataframe
    existing_data.drop_duplicates(
        subset=["title", "url", "time_published"],
        inplace=True,
    )
    existing_data.sort_index(inplace=True)
    save_dataframe(df=existing_data, file_path=save_dir / file_name)

    # Return data within the requested time bounds
    return existing_data[(existing_data.index >= start_datetime) & (existing_data.index <= end_datetime)].sort_index()


if __name__ == "__main__":
    print(get_sentiment())
