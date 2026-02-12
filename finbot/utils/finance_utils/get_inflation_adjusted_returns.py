"""Inflation-adjusted (real) return calculations using FRED CPI data.

Deflates nominal price series by the Consumer Price Index (CPIAUCSL)
to produce real-dollar price histories.  Essential for comparing
long-horizon returns across different inflation regimes.

The CPI data is fetched from FRED (already collected in the data
pipeline) and resampled to match the price series frequency via
forward-fill interpolation.

Typical usage:
    real_prices = get_inflation_adjusted_returns(nominal_prices)
    real_return = (real_prices.iloc[-1] / real_prices.iloc[0]) - 1
"""

from __future__ import annotations

import datetime

import pandas as pd

from finbot.config import logger


def get_inflation_adjusted_returns(
    prices: pd.Series | pd.DataFrame,
    cpi_data: pd.DataFrame | None = None,
    base_date: datetime.date | None = None,
) -> pd.Series | pd.DataFrame:
    """Deflate a nominal price series by CPI to get real prices.

    Parameters
    ----------
    prices : pd.Series | pd.DataFrame
        Nominal price series with a DatetimeIndex.  If DataFrame, each
        column is deflated independently.
    cpi_data : pd.DataFrame | None
        DataFrame with a "CPIAUCSL" column indexed by date.  If None,
        fetched from FRED automatically.
    base_date : datetime.date | None
        Date to rebase CPI to 1.0.  Defaults to the first date in
        ``prices``.  Real prices are expressed in ``base_date`` dollars.

    Returns
    -------
    pd.Series | pd.DataFrame
        Inflation-adjusted price series of the same shape as input.
    """
    if cpi_data is None:
        cpi_data = _load_cpi()

    cpi_series = cpi_data["CPIAUCSL"].copy()

    # Reindex CPI to daily frequency (forward-fill monthly values)
    cpi_daily = cpi_series.reindex(prices.index, method="ffill")

    # Fill any leading NaNs (prices start before CPI) with the earliest CPI value
    if cpi_daily.isna().any():
        cpi_daily = cpi_daily.bfill()

    if cpi_daily.isna().all():
        logger.warning("No CPI data overlaps with price series; returning nominal prices.")
        return prices

    # Rebase CPI so base_date = 1.0
    if base_date is None:
        base_cpi = cpi_daily.iloc[0]
    else:
        base_ts = pd.Timestamp(base_date)
        # Find closest available CPI value
        idx = cpi_daily.index.get_indexer(pd.Index([base_ts]), method="ffill")[0]
        base_cpi = cpi_daily.iloc[max(idx, 0)]

    cpi_factor = cpi_daily / base_cpi

    if isinstance(prices, pd.DataFrame):
        return prices.div(cpi_factor, axis=0)
    return prices / cpi_factor


def _load_cpi() -> pd.DataFrame:
    """Fetch CPIAUCSL from FRED."""
    from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

    result = get_fred_data(symbols=["CPIAUCSL"], start_date=datetime.date(1947, 1, 1))
    if not isinstance(result, pd.DataFrame):
        raise TypeError("Expected DataFrame from get_fred_data")
    return result
