"""Validation tests against known deterministic reference results."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.services.simulation.fund_simulator import fund_simulator
from finbot.utils.finance_utils.get_cgr import get_cgr
from finbot.utils.finance_utils.get_drawdown import get_drawdown


def test_cgr_matches_known_reference_value() -> None:
    # 100 -> 121 over 2 periods is exactly 10% compound growth.
    assert get_cgr(100.0, 121.0, 2.0) == pytest.approx(0.1)


def test_drawdown_matches_known_reference_series() -> None:
    prices = pd.Series([100.0, 120.0, 90.0, 95.0])
    drawdown = get_drawdown(prices)
    expected = pd.Series([0.0, 0.0, -0.25, -0.2083333333])
    assert np.allclose(drawdown.to_numpy(), expected.to_numpy(), atol=1e-10)


def test_fund_simulator_matches_simple_reference_path() -> None:
    index = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    price_df = pd.DataFrame({"Close": [100.0, 110.0, 121.0]}, index=index)
    libor_df = pd.DataFrame({"Yield": [0.0, 0.0, 0.0]}, index=index)

    result = fund_simulator(
        price_df=price_df,
        leverage_mult=1.0,
        annual_er_pct=0.0,
        percent_daily_spread_cost=0.0,
        fund_swap_pct=0.0,
        periods_per_year=252,
        multiplicative_constant=1.0,
        additive_constant=0.0,
        libor_yield_df=libor_df,
    )

    expected_close = np.array([1.0, 1.1, 1.21])
    expected_change = np.array([0.0, 0.1, 0.1])
    assert np.allclose(result["Close"].to_numpy(), expected_close, atol=1e-10)
    assert np.allclose(result["Change"].to_numpy(), expected_change, atol=1e-10)
