"""Shared Hypothesis strategies for property-based testing.

This module provides reusable Hypothesis strategies for generating
test data that represents realistic financial values.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from hypothesis import strategies as st
from hypothesis.extra.pandas import series

# Financial Values
# ================

# Positive prices (stocks, funds, etc.)
prices = st.floats(
    min_value=0.01,
    max_value=10000.0,
    allow_nan=False,
    allow_infinity=False,
)

# Small positive prices (for ratio testing)
small_prices = st.floats(
    min_value=0.01,
    max_value=1000.0,
    allow_nan=False,
    allow_infinity=False,
)

# Percentage changes (daily returns typically -10% to +10%)
daily_returns = st.floats(
    min_value=-0.2,  # -20% (extreme daily loss)
    max_value=0.2,  # +20% (extreme daily gain)
    allow_nan=False,
    allow_infinity=False,
)

# Percentage changes (allow wider range for testing)
pct_changes = st.floats(
    min_value=-0.99,  # -99% (near total loss)
    max_value=10.0,  # +1000% (10x gain)
    allow_nan=False,
    allow_infinity=False,
)

# Expense ratios (annual, in decimal form)
expense_ratios = st.floats(
    min_value=0.0,
    max_value=0.02,  # 0% to 2%
    allow_nan=False,
    allow_infinity=False,
)

# Leverage multipliers (1x to 3x typical)
leverage_mult = st.floats(
    min_value=1.0,
    max_value=3.0,
    allow_nan=False,
    allow_infinity=False,
)


# Time Periods
# ============

# Trading periods (days)
trading_periods = st.integers(min_value=1, max_value=252 * 10)  # Up to 10 years

# Years (for annualization)
years = st.floats(
    min_value=0.01,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
)

# Periods per year (for different frequencies)
periods_per_year = st.sampled_from([1, 12, 52, 252, 365])  # Annual, monthly, weekly, daily

# Business dates
business_dates = st.dates(
    min_value=date(2000, 1, 1),
    max_value=date(2025, 12, 31),
)


# Arrays and Series
# =================


def price_series_strategy(
    min_length: int = 10,
    max_length: int = 252,
    min_price: float = 50.0,
    max_price: float = 500.0,
) -> st.SearchStrategy:
    """Generate pandas Series of realistic prices with datetime index.

    Args:
        min_length: Minimum number of data points
        max_length: Maximum number of data points
        min_price: Minimum price value
        max_price: Maximum price value

    Returns:
        Strategy that generates price Series
    """
    return st.builds(
        lambda length, start_price, returns: pd.Series(
            start_price * (1 + np.array(returns)).cumprod(),
            index=pd.date_range("2020-01-01", periods=length, freq="B"),
        ),
        length=st.integers(min_value=min_length, max_value=max_length),
        start_price=st.floats(min_value=min_price, max_value=max_price, allow_nan=False),
        returns=st.lists(
            st.floats(min_value=-0.1, max_value=0.1, allow_nan=False),
            min_size=min_length,
            max_size=max_length,
        ),
    )


def returns_series_strategy(
    min_length: int = 10,
    max_length: int = 252,
) -> st.SearchStrategy:
    """Generate pandas Series of returns.

    Args:
        min_length: Minimum number of returns
        max_length: Maximum number of returns

    Returns:
        Strategy that generates returns Series
    """
    return series(
        dtype=float,
        elements=daily_returns,
        index=st.builds(
            lambda n: pd.date_range("2020-01-01", periods=n, freq="B"),
            n=st.integers(min_value=min_length, max_value=max_length),
        ),
    )


# Constants
# =========

# Common periods per year values
PERIODS_PER_YEAR_VALUES = [1, 12, 52, 252, 365]

# Reasonable value ranges
MIN_PRICE = 0.01
MAX_PRICE = 1000000.0
MIN_YEARS = 0.01
MAX_YEARS = 100.0
