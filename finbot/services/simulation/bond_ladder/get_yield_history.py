"""Get yield history from FRED and Shiller data sources."""

from __future__ import annotations

import pandas as pd

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data
from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_data import get_shiller_ch26, get_shiller_data
from finbot.utils.data_collection_utils.yfinance.get_history import get_history


def get_yield_history() -> pd.DataFrame:
    FRED_SERIES = [  # noqa: N806 - Constant scoped to function
        "M1329AUSM193NNBR",
        "M1329BUSM193NNBR",
        "M13009USM156NNBR",
        "M13044USM156NNBR",
        "M13035USM156NNBR",
        "M1333AUSM156NNBR",
        "M13058USM156NNBR",
        "BAA",
        "AAA",
        "CP1M",
        "CP3M",
        "CP6M",
        "GS1M",
        "GS3M",
        "GS6M",
        "GS1",
        "GS2",
        "GS3",
        "GS5",
        "GS7",
        "GS10",
        "GS20",
        "GS30",
        "CD1M",
        "CD3M",
        "CD6M",
        "TB1YR",
        "TB4WK",
        "TB3MS",
        "TB6MS",
        "MSLB20",
        "LTGOVTBD",
        "DBAA",
        "DAAA",
        "DCP30",
        "WCP3M",
        "WCP6M",
        "DGS1MO",
        "DGS3MO",
        "DGS6MO",
        "DGS1",
        "DGS2",
        "DGS3",
        "DGS5",
        "DGS7",
        "DGS10",
        "DGS20",
        "DGS30",
        "DCD1M",
        "DCD90",
        "DCD6M",
        "DTB1YR",
        "DTB4WK",
        "DTB3",
        "DTB6",
        "WSLB20",
    ]

    fred_data = get_fred_data(FRED_SERIES)
    shiller_data = get_shiller_data()[["Real Price", "Real Dividend", "Real Earnings", "Long Interest Rate GS10"]]
    shiller_ch26_data = get_shiller_ch26()["One-Year Interest Rate"]
    gspc_data = get_history("^GSPC")["Close"].to_frame().rename(columns={"Close": "GSPC"})

    # Mix all data sources together
    yield_history = pd.concat([shiller_data, fred_data, shiller_ch26_data], axis=1, join="outer")

    # Add S&P500 market days, then drop the price column
    yield_history = pd.concat([yield_history, gspc_data], axis=1, join="outer")
    yield_history = yield_history.drop(labels="GSPC", axis=1)

    # Fill gaps from non-daily data
    yield_history = yield_history.interpolate()

    # Truncate to start of daily values
    yield_history = yield_history.truncate(before=_get_daily_data_start(yield_history))
    return yield_history


def _get_daily_data_start(yield_history: pd.DataFrame, days_to_qualify: int = 15) -> pd.Timestamp:
    """Find the first date where daily data begins (>= days_to_qualify data points in one month)."""
    cur_idx = 0
    cur_start = yield_history.index[cur_idx]
    cur_end = cur_start + pd.DateOffset(months=1)
    while len(yield_history.loc[cur_start:cur_end]) < days_to_qualify:
        cur_idx += 1
        cur_start = yield_history.index[cur_idx]
        cur_end = cur_start + pd.DateOffset(months=1)
    return cur_start
