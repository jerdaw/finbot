"""Tests for rolling performance metrics computation."""

from __future__ import annotations

import math

import numpy as np
import pytest

from finbot.core.contracts.portfolio_analytics import RollingMetricsResult
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics

RNG = np.random.default_rng(seed=42)
RETURNS = RNG.normal(0.0005, 0.01, 300)
BENCHMARK = RNG.normal(0.0003, 0.009, 300)
HIGH_VOL = RNG.normal(0.0, 0.05, 300)


class TestComputeRollingMetrics:
    """Tests for compute_rolling_metrics function."""

    def test_returns_correct_type(self) -> None:
        """Returns a RollingMetricsResult instance."""
        result = compute_rolling_metrics(RETURNS)
        assert isinstance(result, RollingMetricsResult)

    def test_sharpe_length_equals_n_obs(self) -> None:
        """sharpe tuple length equals number of observations."""
        result = compute_rolling_metrics(RETURNS, window=63)
        assert len(result.sharpe) == len(RETURNS)

    def test_volatility_length_equals_n_obs(self) -> None:
        """volatility tuple length equals number of observations."""
        result = compute_rolling_metrics(RETURNS, window=63)
        assert len(result.volatility) == len(RETURNS)

    def test_dates_length_equals_n_obs(self) -> None:
        """dates tuple length equals number of observations."""
        result = compute_rolling_metrics(RETURNS, window=63)
        assert len(result.dates) == len(RETURNS)

    def test_first_positions_are_nan(self) -> None:
        """First (window - 1) positions in sharpe and volatility are NaN."""
        window = 30
        result = compute_rolling_metrics(RETURNS, window=window)
        for i in range(window - 1):
            assert math.isnan(result.sharpe[i]), f"sharpe[{i}] should be NaN"
            assert math.isnan(result.volatility[i]), f"volatility[{i}] should be NaN"

    def test_valid_positions_are_finite(self) -> None:
        """Positions from window - 1 onward are finite numbers."""
        window = 30
        result = compute_rolling_metrics(RETURNS, window=window)
        for i in range(window - 1, len(RETURNS)):
            assert math.isfinite(result.sharpe[i]), f"sharpe[{i}] should be finite"

    def test_higher_vol_series_higher_rolling_vol(self) -> None:
        """Series with larger swings produces higher mean rolling vol."""
        result_norm = compute_rolling_metrics(RETURNS, window=30)
        result_high = compute_rolling_metrics(HIGH_VOL, window=30)

        valid_norm = [x for x in result_norm.volatility if not math.isnan(x)]
        valid_high = [x for x in result_high.volatility if not math.isnan(x)]
        assert sum(valid_high) / len(valid_high) > sum(valid_norm) / len(valid_norm)

    def test_with_benchmark_beta_not_none(self) -> None:
        """Providing benchmark_returns produces a non-None beta series."""
        result = compute_rolling_metrics(RETURNS, window=30, benchmark_returns=BENCHMARK)
        assert result.beta is not None
        assert len(result.beta) == len(RETURNS)

    def test_without_benchmark_beta_is_none(self) -> None:
        """Omitting benchmark_returns produces beta=None."""
        result = compute_rolling_metrics(RETURNS, window=30)
        assert result.beta is None

    def test_perfect_tracking_beta_near_one(self) -> None:
        """Portfolio equal to benchmark gives rolling beta near 1."""
        bench = RNG.normal(0.0005, 0.012, 300)
        result = compute_rolling_metrics(bench, window=63, benchmark_returns=bench)
        valid_beta = [x for x in result.beta if not math.isnan(x)]  # type: ignore[union-attr]
        assert abs(sum(valid_beta) / len(valid_beta) - 1.0) < 0.01

    def test_window_stored_in_result(self) -> None:
        """Result stores the requested window."""
        result = compute_rolling_metrics(RETURNS, window=42)
        assert result.window == 42

    def test_annualization_factor_stored(self) -> None:
        """Result stores the annualization factor."""
        result = compute_rolling_metrics(RETURNS, annualization_factor=52)
        assert result.annualization_factor == 52

    def test_insufficient_data_raises(self) -> None:
        """Fewer than 30 observations raises ValueError."""
        with pytest.raises(ValueError, match="observations"):
            compute_rolling_metrics(np.zeros(10))

    def test_window_less_than_two_raises(self) -> None:
        """window < 2 raises ValueError."""
        with pytest.raises(ValueError, match="window must be >= 2"):
            compute_rolling_metrics(RETURNS, window=1)

    def test_benchmark_length_mismatch_raises(self) -> None:
        """benchmark_returns with different length raises ValueError."""
        with pytest.raises(ValueError, match="length"):
            compute_rolling_metrics(RETURNS, benchmark_returns=BENCHMARK[:100])

    def test_zero_return_series_sharpe_zero(self) -> None:
        """Constant-return series produces Sharpe of 0 (zero std)."""
        const = np.zeros(100)
        result = compute_rolling_metrics(const, window=30, risk_free_rate=0.0)
        valid = [x for x in result.sharpe if not math.isnan(x)]
        assert all(x == pytest.approx(0.0) for x in valid)
