"""Inflation adjustment for time series data using CPI.

Adjusts entire price time series for inflation using Consumer Price Index (CPI)
data from FRED. Handles common data alignment challenges like missing values,
different frequencies, and overlapping date ranges.

More sophisticated than get_inflation_adjusted_value.py which handles single
point adjustments. This module processes full time series with interpolation
and date range alignment.

Typical usage:
    - Convert nominal price series to real (constant-dollar) terms
    - Compare asset performance across different inflation regimes
    - Calculate real returns for backtesting
"""

import pandas as pd

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data


def _interpolate_cpi_data(cpi_data: pd.Series, price_index_data: pd.Series) -> pd.Series:
    """
    Interpolates CPI data to fill in missing values based on the index of the price index data.

    Args:
        cpi_data (pd.Series): Series containing CPI data.
        price_index_data (pd.Series): Series containing price index data.

    Returns:
        pd.Series: Interpolated CPI data.
    """
    orig_cpi_start, orig_cpi_end = cpi_data.index.min(), cpi_data.index.max()
    cpi_data = cpi_data.reindex(cpi_data.index.union(price_index_data.index))
    cpi_data = cpi_data.interpolate(method="time")
    cpi_data = cpi_data[(cpi_data.index >= orig_cpi_start) & (cpi_data.index <= orig_cpi_end)]
    return cpi_data


def _find_common_date_range(price_data: pd.Series, cpi_data: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Identifies the common date range between two data series.

    Args:
        price_data (pd.Series): Series containing price index data.
        cpi_data (pd.Series): Series containing CPI data.

    Returns:
        tuple[pd.Timestamp, pd.Timestamp]: Start and end dates of the common range.
    """
    common_start = price_data[price_data.index >= cpi_data.index.min()].index.min()
    common_end = price_data[price_data.index <= cpi_data.index.max()].index.max()
    return common_start, common_end


def _filter_data_by_common_range(
    price_data: pd.Series,
    cpi_data: pd.Series,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> tuple[pd.Series, pd.Series]:
    """
    Filters two data series to a common date range.

    Args:
        price_data (pd.Series): Series containing price index data.
        cpi_data (pd.Series): Series containing CPI data.
        start_date (pd.Timestamp): Start date of the common range.
        end_date (pd.Timestamp): End date of the common range.

    Returns:
        tuple[pd.Series, pd.Series]: Filtered price data and CPI data.
    """
    price_data = price_data[(price_data.index >= start_date) & (price_data.index <= end_date)]
    cpi_data = cpi_data[(cpi_data.index >= start_date) & (cpi_data.index <= end_date)]
    return price_data, cpi_data


def get_series_adjusted_for_inflation(
    price_index_data: pd.Series,
    cpi_data: pd.Series | None = None,
    interpolate_cpi: bool = True,
) -> pd.Series:
    """
    Adjusts a price index for inflation using CPI data, handling edge cases.

    Args:
        price_index_data (pd.Series): Series containing price index data.
        cpi_data (Optional[pd.Series]): Series containing CPI data.
        interpolate_cpi (bool): Whether to interpolate CPI data to fill in missing values.

    Returns:
        pd.Series: Series containing the inflation-adjusted price index.
    """
    # Validate input types
    if not isinstance(price_index_data, pd.Series):
        raise TypeError(f"price_index_data must be a pd.Series, not {type(price_index_data)}")

    if cpi_data is None:
        cpi_data = get_fred_data(symbols=["CPIAUCSL"])["CPIAUCSL"]

    if not isinstance(cpi_data, pd.Series):
        raise TypeError(f"cpi_data must be a pd.Series, not {type(cpi_data)}")

    # Process CPI data
    cpi_data = cpi_data.dropna()  # Remove NaN values
    if interpolate_cpi:
        cpi_data = _interpolate_cpi_data(cpi_data, price_index_data)

    # Filter for common date range
    common_start, common_end = _find_common_date_range(price_index_data, cpi_data)
    price_index_data, cpi_data = _filter_data_by_common_range(price_index_data, cpi_data, common_start, common_end)

    # Adjust price index based on CPI
    base_cpi = cpi_data.iloc[0]  # type: ignore
    adjusted_price_index = price_index_data * (base_cpi / cpi_data)

    return adjusted_price_index


if __name__ == "__main__":
    # Example usage
    from constants.data_constants import DEMO_DATA

    adjusted_index = get_series_adjusted_for_inflation(DEMO_DATA["Close"])
    print(f"Inflation-adjusted price index:\n{adjusted_index}")
