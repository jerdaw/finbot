"""Tests for Kelly criterion computation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts.risk_analytics import KellyResult, MultiAssetKellyResult
from finbot.services.risk_analytics.kelly import (
    compute_kelly_criterion,
    compute_kelly_from_returns,
    compute_multi_asset_kelly,
)

RNG = np.random.default_rng(seed=2)
POSITIVE_RETURNS = RNG.normal(0.005, 0.01, 300)  # positive EV series
NEGATIVE_RETURNS = RNG.normal(-0.005, 0.01, 300)  # negative EV series


class TestKellyFormula:
    """Tests for compute_kelly_criterion (win_rate + ratio inputs)."""

    def test_known_kelly_value(self) -> None:
        """50% win rate, 2:1 ratio -> f* = 0.25."""
        result = compute_kelly_criterion(win_rate=0.5, win_loss_ratio=2.0)
        assert abs(result.full_kelly - 0.25) < 1e-10

    def test_negative_ev_gives_negative_kelly(self) -> None:
        """Kelly is <= 0 for negative expected value."""
        result = compute_kelly_criterion(win_rate=0.3, win_loss_ratio=0.5)
        assert result.full_kelly <= 0
        assert not result.is_positive_ev

    def test_half_kelly_is_half_of_full(self) -> None:
        """half_kelly == full_kelly * 0.5."""
        result = compute_kelly_criterion(win_rate=0.6, win_loss_ratio=1.5)
        assert abs(result.half_kelly - result.full_kelly * 0.5) < 1e-10

    def test_quarter_kelly_is_quarter_of_full(self) -> None:
        """quarter_kelly == full_kelly * 0.25."""
        result = compute_kelly_criterion(win_rate=0.6, win_loss_ratio=1.5)
        assert abs(result.quarter_kelly - result.full_kelly * 0.25) < 1e-10

    def test_invalid_win_rate_raises(self) -> None:
        """win_rate > 1 raises ValueError."""
        with pytest.raises(ValueError, match="win_rate"):
            compute_kelly_criterion(win_rate=1.5, win_loss_ratio=2.0)

    def test_invalid_win_loss_ratio_raises(self) -> None:
        """win_loss_ratio <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="win_loss_ratio"):
            compute_kelly_criterion(win_rate=0.5, win_loss_ratio=0.0)


class TestKellyFromReturns:
    """Tests for compute_kelly_from_returns."""

    def test_returns_kelly_result(self) -> None:
        """Returns a KellyResult instance."""
        result = compute_kelly_from_returns(POSITIVE_RETURNS)
        assert isinstance(result, KellyResult)

    def test_positive_ev_series(self) -> None:
        """Positive-drift series yields is_positive_ev=True."""
        result = compute_kelly_from_returns(POSITIVE_RETURNS)
        assert result.is_positive_ev

    def test_n_observations_stored(self) -> None:
        """n_observations matches input length."""
        result = compute_kelly_from_returns(POSITIVE_RETURNS)
        assert result.n_observations == len(POSITIVE_RETURNS)

    def test_insufficient_data_raises(self) -> None:
        """Fewer than 10 observations raises ValueError."""
        with pytest.raises(ValueError, match="observations"):
            compute_kelly_from_returns(np.array([0.01] * 5))

    def test_kelly_fractions_consistency(self) -> None:
        """half and quarter kelly are fractions of full kelly."""
        result = compute_kelly_from_returns(POSITIVE_RETURNS)
        assert abs(result.half_kelly - result.full_kelly * 0.5) < 1e-10
        assert abs(result.quarter_kelly - result.full_kelly * 0.25) < 1e-10


class TestMultiAssetKelly:
    """Tests for compute_multi_asset_kelly."""

    def _make_two_asset_df(self) -> pd.DataFrame:
        returns1 = RNG.normal(0.001, 0.01, 300)
        returns2 = RNG.normal(0.002, 0.015, 300)
        return pd.DataFrame({"SPY": returns1, "TLT": returns2})

    def test_returns_multi_asset_kelly_result(self) -> None:
        """Returns a MultiAssetKellyResult instance."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        assert isinstance(result, MultiAssetKellyResult)

    def test_weights_sum_to_one(self) -> None:
        """Practical weights sum to approximately 1."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        total = sum(result.weights.values())
        assert abs(total - 1.0) < 1e-9

    def test_n_assets_correct(self) -> None:
        """n_assets matches DataFrame column count."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        assert result.n_assets == 2

    def test_correlation_matrix_shape(self) -> None:
        """Correlation matrix has correct shape (2x2 for 2 assets)."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        assert len(result.correlation_matrix) == 2
        for row in result.correlation_matrix.values():
            assert len(row) == 2

    def test_correlation_diagonal_is_one(self) -> None:
        """Self-correlations on the diagonal are 1.0."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        for asset in result.correlation_matrix:
            assert abs(result.correlation_matrix[asset][asset] - 1.0) < 1e-9

    def test_fewer_than_two_assets_raises(self) -> None:
        """Single-column DataFrame raises ValueError."""
        df = pd.DataFrame({"SPY": RNG.normal(0.001, 0.01, 100)})
        with pytest.raises(ValueError, match="2 assets"):
            compute_multi_asset_kelly(df)

    def test_per_asset_kelly_results_present(self) -> None:
        """asset_kelly_results contains an entry for each asset."""
        df = self._make_two_asset_df()
        result = compute_multi_asset_kelly(df)
        assert set(result.asset_kelly_results.keys()) == set(df.columns)
