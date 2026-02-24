"""Fetch daily news sentiment analysis from Alpha Vantage.

Retrieves AI-powered sentiment analysis of financial news for specific tickers.
Includes overall sentiment scores, relevance scores, and topic classifications.

Data source: Alpha Vantage News Sentiment API
Update frequency: Real-time
API function: NEWS_SENTIMENT
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import pandas as pd
from matplotlib import pyplot as plt

from finbot.config import logger
from finbot.utils.data_collection_utils.alpha_vantage.sentiment import get_sentiment


def _plot_daily_sentiment(df: pd.DataFrame, moving_averages: Sequence[int] | None = None) -> None:
    """
    Plots daily sentiment data with optional moving averages.

    Args:
        df (pd.DataFrame): DataFrame containing the sentiment data. Defaults to [5, 20, 10, 100, 200].
        moving_averages (List[int]): List of integers representing the days for moving averages.

    Returns:
        None: The function plots the sentiment data and does not return any value.
    """
    plt_df = df.copy()

    plt.figure(figsize=(13, 3))
    plt.axhline(y=0, color="gray", linestyle="--")
    plt.scatter(
        plt_df.index,
        plt_df["mean_sentiment"],
        label="mean_sentiment",
        color="#aaaaaa",
        s=5,
    )

    moving_averages = moving_averages or [5, 20, 10, 100, 200]
    for mov_av in moving_averages:
        if mov_av <= 0:
            raise ValueError(
                f"Moving average value must be positive: {mov_av}",
            )
        plt_df[f"MA_{mov_av}"] = (
            plt_df["mean_sentiment"]
            .rolling(
                window=mov_av,
            )
            .mean()
        )
        plt.plot(
            plt_df[f"MA_{mov_av}"],
            label=f"{mov_av}-entry MA",
            linewidth=2,
        )

    # Adding labels and title
    plt.xlabel("Date")
    plt.ylabel("Mean Sentiment")
    plt.title("Data Sentiment with Moving Averages")
    plt.legend()
    plt.show()


def get_daily_sentiment(
    start_date: date | None = None,
    end_date: date | None = None,
    check_update: bool = False,
    force_update: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """
    Retrieve and calculate daily mean sentiment scores from market data within a specified date range.
    Optionally, this function can plot the sentiment analysis results.

    Market sentiment data analyzes the mood or tone of market participants towards current market conditions.
    This analysis is crucial for understanding market trends and making informed decisions.

    The sentiment score is categorized as follows:
        - x <= -0.35: Bearish
        - -0.35 < x <= -0.15: Somewhat-Bearish
        - -0.15 < x < 0.15: Neutral
        - 0.15 <= x < 0.35: Somewhat_Bullish
        - x >= 0.35: Bullish

    Args:
        start_date (date | None): The start date for the sentiment analysis. If None, the analysis starts from the earliest available date.
        end_date (date | None): The end date for the sentiment analysis. If None, the analysis ends on the latest available date.
        check_update (bool): If set to True, the function checks for an update to the data. Defaults to False.
        force_update (bool): If set to True, the function forces a fresh retrieval of the data, ignoring any cached results. Defaults to False.
        plot (bool): If set to True, the function plots the sentiment analysis results using a static method _plot_daily_sentiment.

    Returns:
        pd.DataFrame: A DataFrame containing daily sentiment scores and their differences. The DataFrame has the following columns:
                      - 'date': The date of the sentiment analysis.
                      - 'mean_sentiment': The mean sentiment score for the day.
                      - 'sentiment_diff': The day-to-day difference in mean sentiment score.

    Raises:
        ValueError: If the date parameters are invalid (e.g., start_date is after end_date) or if data retrieval fails.

    Example:
        >>> sentiment_df = get_daily_sentiment(start_date=date(2021, 1, 1), end_date=date(2021, 1, 31), plot=True)
        >>> print(sentiment_df.head())
    """
    logger.info("Fetching daily sentiment data")

    daily_sentiment: dict = {"date": [], "mean_sentiment": []}
    full_sentiment_df = get_sentiment(
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )
    date_indexes = pd.DatetimeIndex(full_sentiment_df.index).date
    all_dates = set(date_indexes)

    for _date in all_dates:
        date_data = full_sentiment_df[date_indexes == _date]
        mean_sentiment = date_data["overall_sentiment_score"].mean()
        daily_sentiment["date"].append(_date)
        daily_sentiment["mean_sentiment"].append(mean_sentiment)

    daily_sentiment_df = (
        pd.DataFrame(
            daily_sentiment,
        )
        .set_index("date")
        .sort_index()
    )

    if plot:
        _plot_daily_sentiment(daily_sentiment_df, [5, 20, 50, 100, 200])

    return daily_sentiment_df


if __name__ == "__main__":
    print(get_daily_sentiment(plot=True))
