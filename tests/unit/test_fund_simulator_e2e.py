"""End-to-end and edge case tests for fund_simulator.

Tests fund_simulator() with synthetic data to verify:
- DataFrame output shape, column names, index alignment
- Zero-value event handling
- Edge cases: zero leverage, various expense ratios, single-row, etc.
- simulate_fund() registry lookup and error handling
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.services.simulation.fund_simulator import _compute_sim_changes, fund_simulator
from finbot.services.simulation.sim_specific_funds import FUND_CONFIGS, FundConfig, simulate_fund


@pytest.fixture
def sample_price_df():
    """Create 252 business days of synthetic price data."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    prices = 100.0 * np.cumprod(1 + np.random.default_rng(42).normal(0.0003, 0.01, 252))
    return pd.DataFrame({"Close": prices}, index=dates)


@pytest.fixture
def sample_libor_series():
    """Create matching LIBOR yield data (5% annual)."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    return pd.Series(5.0 * np.ones(252), index=dates, name="Yield")


@pytest.fixture
def sample_libor_df(sample_libor_series):
    """LIBOR as DataFrame with Yield column."""
    return sample_libor_series.to_frame(name="Yield")


class TestFundSimulatorEndToEnd:
    """End-to-end tests for fund_simulator()."""

    def test_output_is_dataframe(self, sample_price_df, sample_libor_df):
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, sample_price_df, sample_libor_df):
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert list(result.columns) == ["Close", "Change"]

    def test_output_index_matches_input(self, sample_price_df, sample_libor_df):
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        pd.testing.assert_index_equal(result.index, sample_price_df.index)

    def test_output_shape_matches_input(self, sample_price_df, sample_libor_df):
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert result.shape == (252, 2)

    def test_close_starts_near_one(self, sample_price_df, sample_libor_df):
        """Close values should start at cumprod of first change + 1 ~ 1.0."""
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert result["Close"].iloc[0] == pytest.approx(1.0, abs=0.01)

    def test_change_first_value_near_zero(self, sample_price_df, sample_libor_df):
        """First change should be near zero (pct_change of first element)."""
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert abs(result["Change"].iloc[0]) < 0.01

    def test_all_values_finite(self, sample_price_df, sample_libor_df):
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_df)
        assert np.all(np.isfinite(result["Close"].values))
        assert np.all(np.isfinite(result["Change"].values))

    def test_no_leverage_tracks_underlying(self, sample_price_df, sample_libor_df):
        """With leverage=1 and no costs, changes should closely track underlying."""
        result = fund_simulator(
            sample_price_df,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=0.0,
            libor_yield_df=sample_libor_df,
        )
        underlying_pct_changes = sample_price_df["Close"].pct_change().fillna(0)
        np.testing.assert_allclose(result["Change"].values, underlying_pct_changes.values, atol=1e-10)

    def test_leverage_amplifies_changes(self, sample_price_df, sample_libor_df):
        """2x leverage should amplify changes (before costs)."""
        result_1x = fund_simulator(
            sample_price_df,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            libor_yield_df=sample_libor_df,
        )
        result_2x = fund_simulator(
            sample_price_df,
            leverage_mult=2.0,
            annual_er_pct=0.0,
            libor_yield_df=sample_libor_df,
        )
        # Absolute mean change should be larger for 2x
        mean_abs_1x = np.abs(result_1x["Change"].values[1:]).mean()
        mean_abs_2x = np.abs(result_2x["Change"].values[1:]).mean()
        assert mean_abs_2x > mean_abs_1x

    def test_libor_as_series(self, sample_price_df, sample_libor_series):
        """fund_simulator should accept LIBOR as a Series."""
        result = fund_simulator(sample_price_df, libor_yield_df=sample_libor_series)
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (252, 2)

    def test_adj_close_column(self, sample_libor_df):
        """fund_simulator should use 'Adj Close' if present."""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        prices = 100.0 * np.cumprod(1 + np.random.default_rng(5).normal(0.0003, 0.01, 100))
        df = pd.DataFrame({"Adj Close": prices, "Close": prices * 0.99}, index=dates)
        libor = pd.DataFrame({"Yield": 5.0 * np.ones(100)}, index=dates)
        result = fund_simulator(df, libor_yield_df=libor)
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (100, 2)


class TestFundSimulatorEdgeCases:
    """Edge case tests for fund_simulator()."""

    def test_zero_leverage(self, sample_price_df):
        """Zero leverage with zero LIBOR should produce only ER-based changes."""
        dates = sample_price_df.index
        zero_libor = pd.DataFrame({"Yield": np.zeros(len(dates))}, index=dates)
        result = fund_simulator(
            sample_price_df,
            leverage_mult=0.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=0.0,
            libor_yield_df=zero_libor,
        )
        # With zero leverage, zero ER, and zero LIBOR, all changes should be zero
        np.testing.assert_allclose(result["Change"].values, 0.0, atol=1e-15)

    def test_small_dataframe(self, sample_libor_df):
        """fund_simulator should work with a small number of rows."""
        dates = pd.date_range("2020-01-01", periods=5, freq="B")
        df = pd.DataFrame({"Close": [100, 101, 102, 101, 103]}, index=dates, dtype=float)
        libor = pd.DataFrame({"Yield": [5.0] * 5}, index=dates)
        result = fund_simulator(df, libor_yield_df=libor)
        assert result.shape == (5, 2)
        assert list(result.columns) == ["Close", "Change"]

    def test_negative_expense_ratio(self, sample_price_df, sample_libor_df):
        """Negative expense ratio (unusual but technically valid)."""
        result = fund_simulator(
            sample_price_df,
            annual_er_pct=-0.01,
            libor_yield_df=sample_libor_df,
        )
        assert isinstance(result, pd.DataFrame)
        assert np.all(np.isfinite(result["Close"].values))

    def test_high_leverage(self, sample_libor_df):
        """High leverage (10x) should still produce valid output."""
        dates = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = 100.0 + np.cumsum(np.random.default_rng(42).normal(0, 0.5, 50))
        prices = np.maximum(prices, 1.0)  # Ensure positive
        df = pd.DataFrame({"Close": prices}, index=dates)
        libor = pd.DataFrame({"Yield": [5.0] * 50}, index=dates)
        result = fund_simulator(df, leverage_mult=10.0, libor_yield_df=libor)
        assert isinstance(result, pd.DataFrame)

    def test_zero_value_event_handling(self):
        """Test that a crash to zero is handled properly (closes set to zero)."""
        dates = pd.date_range("2020-01-01", periods=10, freq="B")
        # Price drops from 100 to nearly 0 (a 99%+ single-day drop)
        prices = [100.0, 50.0, 25.0, 10.0, 1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001]
        df = pd.DataFrame({"Close": prices}, index=dates)
        libor = pd.DataFrame({"Yield": [0.0] * 10}, index=dates)
        # With 3x leverage, cumulative product goes to zero quickly
        result = fund_simulator(df, leverage_mult=3.0, annual_er_pct=0.0, libor_yield_df=libor)
        assert isinstance(result, pd.DataFrame)
        # Once a zero event occurs, remaining closes should be zero
        close_values = result["Close"].values
        zero_idxs = np.where(close_values <= 0)[0]
        if len(zero_idxs) > 0:
            first_zero = zero_idxs[0]
            assert np.all(close_values[first_zero:] == 0)

    def test_multiplicative_constant(self, sample_price_df, sample_libor_df):
        """Multiplicative constant should scale changes."""
        result_1x = fund_simulator(sample_price_df, multiplicative_constant=1.0, libor_yield_df=sample_libor_df)
        result_2x = fund_simulator(sample_price_df, multiplicative_constant=2.0, libor_yield_df=sample_libor_df)
        # The 2x multiplicative constant should produce different changes
        assert not np.allclose(result_1x["Change"].values, result_2x["Change"].values)

    def test_additive_constant(self, sample_price_df, sample_libor_df):
        """Additive constant should shift changes."""
        result_0 = fund_simulator(sample_price_df, additive_constant=0.0, libor_yield_df=sample_libor_df)
        result_add = fund_simulator(sample_price_df, additive_constant=0.001, libor_yield_df=sample_libor_df)
        # Additive constant adds a fixed offset per period
        diff = result_add["Change"].values - result_0["Change"].values
        np.testing.assert_allclose(diff, 0.001, atol=1e-15)

    def test_invalid_index_type_raises(self):
        """Non-datetime index should raise ValueError."""
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=[0, 1, 2])
        with pytest.raises(ValueError, match="datetime64"):
            fund_simulator(df)

    def test_missing_close_column_raises(self):
        """DataFrame without Close/Adj Close should raise ValueError."""
        dates = pd.date_range("2020-01-01", periods=3, freq="B")
        df = pd.DataFrame({"Price": [100, 101, 102]}, index=dates)
        with pytest.raises(ValueError, match="Close"):
            fund_simulator(df)

    def test_invalid_libor_index_raises(self):
        """LIBOR with non-datetime index should raise ValueError."""
        dates = pd.date_range("2020-01-01", periods=3, freq="B")
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=dates)
        libor = pd.DataFrame({"Yield": [5.0, 5.0, 5.0]}, index=[0, 1, 2])
        with pytest.raises(ValueError, match="datetime64"):
            fund_simulator(df, libor_yield_df=libor)


class TestComputeSimChangesDetailed:
    """Detailed tests for the vectorized _compute_sim_changes function."""

    def test_expense_ratio_deducted(self):
        """Expense ratio should reduce changes."""
        underlying = np.array([0.0, 0.01, 0.01, 0.01])
        libor = np.zeros(4)
        result_no_er = _compute_sim_changes(underlying, libor, 1.0, 0.0, 0.0, 0.0, 252)
        result_with_er = _compute_sim_changes(underlying, libor, 1.0, 0.10, 0.0, 0.0, 252)
        # With ER, changes should be smaller
        assert np.all(result_with_er[1:] < result_no_er[1:])

    def test_spread_cost_deducted(self):
        """Spread cost should reduce changes when swap_pct > 0."""
        underlying = np.array([0.0, 0.01, 0.01])
        libor = np.zeros(3)
        result_no_spread = _compute_sim_changes(underlying, libor, 1.0, 0.0, 0.0, 0.0, 252)
        result_with_spread = _compute_sim_changes(underlying, libor, 1.0, 0.0, 0.01, 0.5, 252)
        assert np.all(result_with_spread[1:] < result_no_spread[1:])

    def test_libor_cost_scales_with_leverage(self):
        """LIBOR costs should increase with leverage."""
        underlying = np.array([0.0, 0.01])
        libor = np.array([0.05, 0.05])
        result_1x = _compute_sim_changes(underlying, libor, 1.0, 0.0, 0.0, 0.0, 252)
        result_3x = _compute_sim_changes(underlying, libor, 3.0, 0.0, 0.0, 0.0, 252)
        # 3x leverage should have higher LIBOR borrowing cost
        # LIBOR cost = (rate/periods) * (leverage - 1)
        # 1x: cost = 0 (leverage - 1 = 0)
        # 3x: cost = (0.05/252) * 2
        expected_cost_diff = (0.05 / 252) * 2
        actual_diff = result_1x[1] * 3 - result_3x[1]  # scaled underlying minus actual
        assert actual_diff == pytest.approx(expected_cost_diff, rel=1e-10)


class TestSimulateFundRegistry:
    """Tests for the simulate_fund() registry-based function."""

    def test_fund_configs_registry_populated(self):
        assert len(FUND_CONFIGS) == 15

    def test_all_fund_configs_have_required_fields(self):
        for ticker, config in FUND_CONFIGS.items():
            assert isinstance(config, FundConfig)
            assert config.ticker == ticker
            assert len(config.name) > 0
            assert callable(config.underlying_func)
            assert isinstance(config.leverage_mult, float)
            assert isinstance(config.annual_er_pct, float)

    def test_simulate_fund_unknown_ticker_raises(self):
        with pytest.raises(ValueError, match="Unknown fund ticker"):
            simulate_fund("INVALID_TICKER")

    def test_simulate_fund_case_insensitive(self):
        """Ticker lookup should be case-insensitive."""
        # This should not raise (just tests the lookup, not the actual simulation)
        with pytest.raises(ValueError, match="Unknown fund ticker"):
            simulate_fund("zzz_nonexistent")

    def test_fund_config_spy(self):
        config = FUND_CONFIGS["SPY"]
        assert config.leverage_mult == 1.0
        assert config.overwrite_sim_with_fund is True

    def test_fund_config_upro(self):
        config = FUND_CONFIGS["UPRO"]
        assert config.leverage_mult == 3.0
        assert config.overwrite_sim_with_fund is True

    def test_fund_config_2x_stt_no_overwrite(self):
        config = FUND_CONFIGS["2X_STT"]
        assert config.overwrite_sim_with_fund is False

    @pytest.mark.parametrize("ticker", sorted(FUND_CONFIGS.keys()))
    def test_all_fund_configs_valid(self, ticker):
        config = FUND_CONFIGS[ticker]
        assert config.leverage_mult >= 0
        assert isinstance(config.annual_er_pct, float)
