"""Correlate FRED economic indicators to stock prices.

Analyzes correlations between FRED economic data series and the S&P 500 index
across different time periods (full history, recessions, non-recessions) using
multiple correlation methods (Pearson, Spearman, Kendall).

Identifies which economic indicators are most predictive of stock market
movements, helping to build economic-based trading signals.

Typical usage:
    - Screen FRED indicators for market correlation
    - Build macroeconomic market timing models
    - Identify leading/lagging economic indicators
    - Develop recession-aware trading strategies

Note: This module is work-in-progress and needs refactoring.
"""

# TODO: This module is still very much a WIP. It needs to be refactored and cleaned up.

from typing import Any

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import DataFrame, Series

from finbot.config import logger
from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data
from finbot.utils.data_collection_utils.fred.get_popular_fred_symbols import get_popular_fred_symbols
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from finbot.utils.data_science_utils.data_analysis.get_correlation import get_correlation
from finbot.utils.finance_utils.get_us_gdp_cycle_dates import get_us_gdp_cycle_dates
from finbot.utils.finance_utils.get_us_gdp_recessions_bools import get_us_gdp_recessions_bools
from finbot.utils.pandas_utils.get_timeseries_frequency import get_timeseries_frequency
from finbot.utils.pandas_utils.merge_data_on_closest_date import merge_data_on_closest_date


def _load_popular_databases(max_pages: int | None) -> DataFrame:
    """
    Scrape and fetch popular database symbols and their corresponding data.
    Includes error handling for network-related issues.

    Args:
        max_pages (int): The maximum number of pages to scrape.

    Returns:
        DataFrame: A pandas DataFrame containing data for popular databases.
    """
    try:
        popular_symbols = get_popular_fred_symbols(max_pages_to_scrape=max_pages)
        popular_dbs = (
            get_fred_data(symbols=popular_symbols, check_update=False).dropna(axis=1, how="all").sort_index(axis=1)
        )
        return popular_dbs
    except Exception as e:
        logger.error(f"Failed to load popular databases: {e}")
        raise


def _get_recession_and_cycle_data() -> tuple[list[tuple[Any, Any]], list[tuple[Any, Any]]]:
    """
    Gather data about US recessions and economic cycles.

    Returns:
        tuple[list[tuple[Any, Any]], list[tuple[Any, Any]]]: A tuple containing lists of start and end dates for
        recessionary and non-recessionary periods.
    """
    us_recessions = get_us_gdp_recessions_bools()
    cycles = get_us_gdp_cycle_dates(us_recessions)
    recessionary_periods = cycles["recessions"]
    non_recessionary_periods = cycles["non_recessions"]
    return recessionary_periods, non_recessionary_periods


def _compute_correlation(trunc_gspc: DataFrame, trunc_serie: Series, corr_methods: list[str]) -> dict[str, float]:
    """
    Compute correlations between two time series using specified methods.
    Optimized using vectorized operations.

    Args:
        trunc_gspc (DataFrame): The truncated time series data of the S&P 500 index.
        trunc_serie (Series): The truncated time series data of a database.
        corr_methods (list[str]): list of correlation methods to use.

    Returns:
        dict[str, float]: A dictionary containing correlation values for each method.
    """
    correlations = {}
    for method in corr_methods:
        try:
            correlation = get_correlation([trunc_gspc, trunc_serie], method=method).iloc[0, 1]
            correlations[method] = float(correlation) if not np.isnan(correlation) else np.nan
        except Exception as e:
            logger.warning(f"Error in computing correlation using {method}: {e}")
            correlations[method] = np.nan
    correlations["avg"] = np.nanmean(list(correlations.values()))
    return correlations


def _compute_period_correlation(
    serie: Series,
    gspc_close: Series,
    periods: list[tuple[Any, Any]],
    corr_methods: list[str],
) -> dict[str, float]:
    """
    Compute correlations for specified periods using various methods.

    Args:
        serie (Series): The time series data of a database.
        gspc_close (Series): The time series data of the S&P 500 index.
        periods (list[tuple[Any, Any]]): list of start and end dates for specified periods.
        corr_methods (list[str]): list of correlation methods to use.

    Returns:
        dict[str, float]: A dictionary containing average correlation values for each method across specified periods.
    """
    period_corrs = {method: [] for method in corr_methods}
    for start_dt, end_dt in periods:
        trunc_serie = serie.truncate(before=start_dt, after=end_dt)
        trunc_gspc = merge_data_on_closest_date(
            index_df=pd.DataFrame(trunc_serie),
            value_df=pd.DataFrame(gspc_close.truncate(before=start_dt, after=end_dt)),
        )
        for method in corr_methods:
            corr = get_correlation([trunc_gspc, trunc_serie], method=method).iloc[0, 1]
            if isinstance(corr, float | int) and not np.isnan(corr):
                period_corrs[method].append(corr)

    averaged_corrs = {method: np.nanmean(period_corrs[method]) for method in corr_methods}
    averaged_corrs["avg"] = np.nanmean(list(averaged_corrs.values()))
    return averaged_corrs


def _aggregate_average_correlation(
    full_data_corrs: dict[str, float],
    rec_corrs: dict[str, float],
    non_rec_corrs: dict[str, float],
) -> float:
    """
    Aggregate and compute the overall average correlation from various correlation measures.

    Args:
        full_data_corrs (dict[str, float]): Correlations for the full dataset.
        rec_corrs (dict[str, float]): Correlations for recessionary periods.
        non_rec_corrs (dict[str, float]): Correlations for non-recessionary periods.

    Returns:
        float: The overall average correlation.
    """
    all_avg_corrs = [
        abs(corr["avg"]) for corr in [full_data_corrs, rec_corrs, non_rec_corrs] if not np.isnan(corr["avg"])
    ]
    overall_avg = np.nanmean(all_avg_corrs) if all_avg_corrs else np.nan
    return overall_avg


def _calculate_correlations(
    gspc_close: Series,
    popular_dbs: DataFrame,
    recessionary_periods: list[tuple[Any, Any]],
    non_recessionary_periods: list[tuple[Any, Any]],
    corr_methods: list[str],
    min_days: int,
) -> dict[str, dict[str, float | dict[str, float]]]:
    """
    Calculate correlations between the S&P 500 index and other datasets for given periods.

    Args:
        gspc_close (Series): The adjusted close prices of the S&P 500 index.
        popular_dbs (DataFrame): A dataframe of popular databases.
        recessionary_periods (list[tuple[Any, Any]]): list of start and end dates for recessionary periods.
        non_recessionary_periods (list[tuple[Any, Any]]): list of start and end dates for non-recessionary periods.
        corr_methods (list[str]): list of correlation methods to use.
        min_days (int): Minimum number of days for the time series frequency.

    Returns:
        dict[str, dict[str, Union[float, dict[str, float]]]]: A dictionary of correlations.
    """
    correlations = {}
    for db_name in popular_dbs.columns:
        serie = popular_dbs[db_name].ffill().dropna().sort_index()
        freq = get_timeseries_frequency(time_series=serie)

        if not isinstance(freq, pd.Timedelta | relativedelta) or freq.days > min_days or len(serie) < 10:
            continue

        serie_start_dt = serie.index.min()
        serie_end_dt = serie.index.max()
        max_start_dt = max(gspc_close.index.min(), serie_start_dt)
        min_end_dt = min(gspc_close.index.max(), serie_end_dt)

        trunc_serie = serie.truncate(before=max_start_dt, after=min_end_dt)
        trunc_gspc = merge_data_on_closest_date(
            index_df=pd.DataFrame(trunc_serie),
            value_df=pd.DataFrame(gspc_close.truncate(before=max_start_dt, after=min_end_dt)),
        )

        # Compute overall, recession, and non-recession correlations
        full_data_corrs = _compute_correlation(trunc_gspc, trunc_serie, corr_methods)
        rec_corrs = _compute_period_correlation(trunc_serie, gspc_close, recessionary_periods, corr_methods)
        non_rec_corrs = _compute_period_correlation(trunc_serie, gspc_close, non_recessionary_periods, corr_methods)

        # Aggregate and average correlations
        overall_avg = _aggregate_average_correlation(full_data_corrs, rec_corrs, non_rec_corrs)

        correlations[db_name] = {
            "full": full_data_corrs,
            "rec": rec_corrs,
            "non_rec": non_rec_corrs,
            "abs_avg": overall_avg,
        }

    return correlations


def correlate_fred_to_price(
    popular_dbs: DataFrame | None = None,
    min_days: int = 60,
    max_pages: None | int = None,
) -> dict[str, dict[str, float | dict[str, float]]]:
    """
    Calculate correlations between the S&P 500 index (^GSPC) and other datasets.

    This function retrieves the price history of the S&P 500 index, as well as a set of popular databases.
    It then calculates the correlations between the S&P 500 index and each database, using three different methods:
    Pearson, Spearman, and Kendall. The function also considers the correlations during US recessions and calculates
    an average correlation for each method. Databases with an average correlation above 0.75 are considered significant.

    Args:
        popular_dbs (Optional[DataFrame]): A dataframe of popular databases. If None, it scrapes and fetches data.
        min_days (int): Minimum number of days for the time series frequency.

    Returns:
        dict[str, dict[str, Union[float, dict[str, float]]]]: A dictionary of sorted correlations.
    """

    # Extracting the adjusted close prices for the S&P 500 index
    gspc_close = get_history("^GSPC")["Adj Close"]

    # Loading popular databases if not provided
    if popular_dbs is None:
        popular_dbs = _load_popular_databases(max_pages=max_pages)

    # Gathering recession and cycle data
    recessionary_periods, non_recessionary_periods = _get_recession_and_cycle_data()

    # Defining correlation methods
    corr_methods = ["pearson", "spearman", "kendall"]

    # Calculating correlations
    correlations = _calculate_correlations(
        gspc_close,
        popular_dbs,
        recessionary_periods,
        non_recessionary_periods,
        corr_methods,
        min_days,
    )

    # Sorting correlations
    sorted_correlations = dict(sorted(correlations.items(), key=lambda x: x[1]["abs_avg"], reverse=True))

    return sorted_correlations


if __name__ == "__main__":
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    sorted_correlations = correlate_fred_to_price()
    for k, v in sorted_correlations.items():
        print(f"{k}\t{v.get('abs_avg')}")

    plotter = InteractivePlotter()
    plotter.plot_bar_chart(
        pd.DataFrame(sorted_correlations).transpose().reset_index(),
        x_col="index",
        y_col="abs_avg",
        title="Correlations",
    )
