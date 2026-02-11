"""Tests for DCA optimizer.

Tests _dca_single metric calculations, _convert_to_df, edge cases,
and analyze_results_helper.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.services.optimization.dca_optimizer import (
    DCAParameters,
    _convert_to_df,
    _dca_single,
    _mp_helper,
    analyze_results_helper,
    dca_optimizer,
)


@pytest.fixture
def steady_growth_prices():
    """Prices that grow steadily (1% per period)."""
    n = 1260  # ~5 years of daily data
    return tuple(100.0 * (1.01**i) for i in range(n))


@pytest.fixture
def flat_prices():
    """Prices that stay constant at 100."""
    return tuple(100.0 for _ in range(1260))


class TestDCASingle:
    """Tests for the _dca_single helper."""

    def test_returns_six_metrics(self, steady_growth_prices):
        ratio_linspace = np.array([0.5, 0.3, 0.2])
        ratio_linspace /= ratio_linspace.sum()
        result = _dca_single(
            starting_cash=1000.0,
            ratio_linspace=ratio_linspace,
            trial_duration=252,
            dca_duration=3,
            dca_step=1,
            closes=steady_growth_prices,
        )
        assert len(result) == 6
        final_value, pct_change, cagr, max_drawdown, std, sharpe = result
        assert isinstance(final_value, float)
        assert isinstance(pct_change, float)
        assert isinstance(cagr, float)
        assert isinstance(max_drawdown, float)
        assert isinstance(std, float)
        assert isinstance(sharpe, float)

    def test_steady_growth_positive_return(self, steady_growth_prices):
        ratio_linspace = np.array([1.0])
        result = _dca_single(
            starting_cash=1000.0,
            ratio_linspace=ratio_linspace,
            trial_duration=252,
            dca_duration=1,
            dca_step=1,
            closes=steady_growth_prices,
        )
        final_value = result[0]
        pct_change = result[1]
        assert final_value > 1000.0
        assert pct_change > 0

    def test_final_value_greater_than_zero(self, flat_prices):
        ratio_linspace = np.array([0.5, 0.5])
        ratio_linspace /= ratio_linspace.sum()
        result = _dca_single(
            starting_cash=1000.0,
            ratio_linspace=ratio_linspace,
            trial_duration=252,
            dca_duration=2,
            dca_step=1,
            closes=flat_prices,
        )
        assert result[0] > 0

    def test_flat_prices_near_zero_return(self, flat_prices):
        """With flat prices, pct change should be ~0."""
        ratio_linspace = np.array([1.0])
        result = _dca_single(
            starting_cash=1000.0,
            ratio_linspace=ratio_linspace,
            trial_duration=252,
            dca_duration=1,
            dca_step=1,
            closes=flat_prices,
        )
        assert abs(result[1]) < 1.0  # Less than 1% change


class TestDCAParameters:
    """Tests for the DCAParameters dataclass."""

    def test_creation(self):
        params = DCAParameters(
            start_idx=0,
            ratio=1.5,
            dca_duration=252,
            dca_step=21,
            trial_duration=756,
            closes=(100.0, 101.0, 102.0),
            starting_cash=1000.0,
        )
        assert params.start_idx == 0
        assert params.ratio == 1.5
        assert params.dca_duration == 252
        assert params.dca_step == 21
        assert params.trial_duration == 756
        assert len(params.closes) == 3
        assert params.starting_cash == 1000.0


class TestMPHelper:
    """Tests for the multiprocessing helper."""

    def test_returns_tuple_pair(self, steady_growth_prices):
        params = DCAParameters(
            start_idx=0,
            ratio=1.0,
            dca_duration=1,
            dca_step=1,
            trial_duration=252,
            closes=steady_growth_prices,
            starting_cash=1000.0,
        )
        key, result = _mp_helper(params)
        assert key is not None
        assert result is not None
        assert len(key) == 5
        assert len(result) == 6

    def test_empty_ratio_linspace_returns_none(self):
        """When dca_duration // dca_step == 0, ratio_linspace is empty."""
        params = DCAParameters(
            start_idx=0,
            ratio=1.0,
            dca_duration=0,
            dca_step=1,
            trial_duration=252,
            closes=tuple(100.0 for _ in range(300)),
            starting_cash=1000.0,
        )
        key, result = _mp_helper(params)
        assert key is None
        assert result is None


class TestConvertToDF:
    """Tests for _convert_to_df."""

    def test_creates_dataframe_with_correct_columns(self):
        dates = pd.date_range("2020-01-01", periods=1260, freq="B")
        data = [
            ((0, 1.0, 252, 21, 756), (1500.0, 50.0, 10.0, 5.0, 100.0, 0.08)),
        ]
        result = _convert_to_df(data, dates)
        assert isinstance(result, pd.DataFrame)
        expected_cols = [
            "Trial End",
            "Trial Duration",
            "DCA Duration",
            "DCA Ratio",
            "DCA Step",
            "Final Value",
            "Pct Change",
            "CAGR",
            "Max Drawdown",
            "STDev",
            "Sharpe",
        ]
        assert list(result.columns) == expected_cols
        assert result.index.name == "Trial Start"

    def test_filters_none_results(self):
        dates = pd.date_range("2020-01-01", periods=1260, freq="B")
        data = [
            (None, None),
            ((0, 1.0, 252, 21, 756), (1500.0, 50.0, 10.0, 5.0, 100.0, 0.08)),
        ]
        result = _convert_to_df(data, dates)
        assert len(result) == 1


class TestAnalyzeResultsHelper:
    """Tests for analyze_results_helper."""

    def test_returns_ratio_and_duration_dfs(self):
        # Create minimal results DataFrame
        data = {
            "Trial End": pd.Timestamp("2023-01-01"),
            "Trial Duration": [756, 756, 756, 756],
            "DCA Duration": [252, 252, 504, 504],
            "DCA Ratio": [1.0, 2.0, 1.0, 2.0],
            "DCA Step": [21, 21, 21, 21],
            "Final Value": [1500.0, 1600.0, 1400.0, 1700.0],
            "Pct Change": [50.0, 60.0, 40.0, 70.0],
            "CAGR": [10.0, 12.0, 8.0, 14.0],
            "Max Drawdown": [5.0, 6.0, 4.0, 7.0],
            "STDev": [100.0, 120.0, 80.0, 140.0],
            "Sharpe": [0.08, 0.10, 0.07, 0.10],
        }
        results_df = pd.DataFrame(data)
        results_df.index.name = "Trial Start"

        ratio_df, duration_df = analyze_results_helper(results_df, plot=False)

        assert isinstance(ratio_df, pd.DataFrame)
        assert isinstance(duration_df, pd.DataFrame)
        assert len(ratio_df) == 2  # Two unique ratios
        assert len(duration_df) == 2  # Two unique durations
        assert "Ratio Sharpe Avg" in ratio_df.columns
        assert "Duration CAGR Avg" in duration_df.columns


class TestDCAOptimizerValidation:
    """Tests for dca_optimizer input validation."""

    def test_none_price_history_raises(self):
        with pytest.raises(ValueError, match="cannot be None or empty"):
            dca_optimizer(price_history=None)

    def test_empty_price_history_raises(self):
        with pytest.raises(ValueError, match="cannot be None or empty"):
            dca_optimizer(price_history=pd.Series(dtype=float))
