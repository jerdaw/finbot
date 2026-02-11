"""Registry of data sources with expected freshness thresholds.

Defines all data sources tracked by finbot along with their storage
locations, file patterns, and staleness thresholds. Used by the
freshness checker and CLI status command.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from finbot.constants.path_constants import (
    ALPHA_VANTAGE_DATA_DIR,
    BLS_DATA_DIR,
    FRED_DATA_DIR,
    GOOGLE_FINANCE_DATA_DIR,
    SHILLER_DATA_DIR,
    SIMULATIONS_DATA_DIR,
    YFINANCE_DATA_DIR,
)


@dataclass(frozen=True)
class DataSource:
    """A tracked data source with freshness metadata."""

    name: str
    directory: Path
    pattern: str
    max_age_days: int
    description: str


# Ordered by update priority (most frequently updated first)
DATA_SOURCES: tuple[DataSource, ...] = (
    DataSource(
        name="Yahoo Finance",
        directory=YFINANCE_DATA_DIR / "history",
        pattern="*_history_1d.parquet",
        max_age_days=3,
        description="Daily price histories (OHLCV)",
    ),
    DataSource(
        name="Google Finance",
        directory=GOOGLE_FINANCE_DATA_DIR,
        pattern="*.parquet",
        max_age_days=3,
        description="Index data from Google Sheets",
    ),
    DataSource(
        name="FRED",
        directory=FRED_DATA_DIR,
        pattern="*.parquet",
        max_age_days=7,
        description="Federal Reserve economic data",
    ),
    DataSource(
        name="Shiller",
        directory=SHILLER_DATA_DIR,
        pattern="*.parquet",
        max_age_days=35,
        description="CAPE ratios, PE ratios, long-term S&P data",
    ),
    DataSource(
        name="Alpha Vantage",
        directory=ALPHA_VANTAGE_DATA_DIR,
        pattern="*.parquet",
        max_age_days=7,
        description="Intraday data, sentiment scores",
    ),
    DataSource(
        name="BLS",
        directory=BLS_DATA_DIR,
        pattern="*.parquet",
        max_age_days=35,
        description="CPI, unemployment, labor statistics",
    ),
    DataSource(
        name="Simulations",
        directory=SIMULATIONS_DATA_DIR,
        pattern="*.parquet",
        max_age_days=3,
        description="Fund and index simulation results",
    ),
)
