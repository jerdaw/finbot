"""Tests for correlation and diversification metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts.portfolio_analytics import DiversificationResult
from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics

RNG = np.random.default_rng(seed=42)

# 3 assets, 300 observations, low correlation
_RETURNS_A = RNG.normal(0.0005, 0.01, 300)
_RETURNS_B = RNG.normal(0.0003, 0.012, 300)
_RETURNS_C = RNG.normal(0.0002, 0.008, 300)
THREE_ASSET_DF = pd.DataFrame({"A": _RETURNS_A, "B": _RETURNS_B, "C": _RETURNS_C})

# 2 perfectly correlated assets
_COMMON = RNG.normal(0.0, 0.01, 300)
PERFECT_CORR_DF = pd.DataFrame({"X": _COMMON, "Y": _COMMON * 2.0})


class TestComputeDiversificationMetrics:
    """Tests for compute_diversification_metrics function."""

    def test_returns_correct_type(self) -> None:
        """Returns a DiversificationResult instance."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assert isinstance(result, DiversificationResult)

    def test_n_assets_stored(self) -> None:
        """n_assets matches the number of columns."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assert result.n_assets == 3

    def test_equal_weights_hhi(self) -> None:
        """Equal weights produce HHI = 1/n."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        expected_hhi = 1.0 / 3.0
        assert result.herfindahl_index == pytest.approx(expected_hhi, abs=1e-9)

    def test_equal_weights_effective_n(self) -> None:
        """Equal weights produce effective_n = n."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assert result.effective_n == pytest.approx(3.0, abs=1e-9)

    def test_custom_weights_stored(self) -> None:
        """Custom weights are stored in the result."""
        w = {"A": 0.5, "B": 0.3, "C": 0.2}
        result = compute_diversification_metrics(THREE_ASSET_DF, weights=w)
        assert result.weights["A"] == pytest.approx(0.5)
        assert result.weights["B"] == pytest.approx(0.3)
        assert result.weights["C"] == pytest.approx(0.2)

    def test_concentrated_weights_higher_hhi(self) -> None:
        """Concentrated weights produce higher HHI than equal weights."""
        result_equal = compute_diversification_metrics(THREE_ASSET_DF)
        result_conc = compute_diversification_metrics(THREE_ASSET_DF, weights={"A": 0.9, "B": 0.05, "C": 0.05})
        assert result_conc.herfindahl_index > result_equal.herfindahl_index

    def test_avg_pairwise_correlation_in_range(self) -> None:
        """avg_pairwise_correlation is in [-1, 1]."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assert -1.0 <= result.avg_pairwise_correlation <= 1.0

    def test_correlation_matrix_symmetric(self) -> None:
        """Correlation matrix is symmetric."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assets = list(result.correlation_matrix.keys())
        for a in assets:
            for b in assets:
                assert result.correlation_matrix[a][b] == pytest.approx(result.correlation_matrix[b][a], abs=1e-10)

    def test_correlation_diagonal_is_one(self) -> None:
        """Self-correlation (diagonal) is 1.0."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        for a in result.correlation_matrix:
            assert result.correlation_matrix[a][a] == pytest.approx(1.0, abs=1e-10)

    def test_portfolio_vol_non_negative(self) -> None:
        """portfolio_vol is >= 0."""
        result = compute_diversification_metrics(THREE_ASSET_DF)
        assert result.portfolio_vol >= 0.0

    def test_diversification_ratio_near_one_perfect_corr(self) -> None:
        """Perfectly correlated assets have diversification_ratio ~= 1."""
        result = compute_diversification_metrics(PERFECT_CORR_DF)
        assert result.diversification_ratio == pytest.approx(1.0, abs=0.01)

    def test_n_assets_less_than_two_raises(self) -> None:
        """DataFrame with fewer than 2 columns raises ValueError."""
        single = pd.DataFrame({"A": _RETURNS_A})
        with pytest.raises(ValueError, match="at least 2"):
            compute_diversification_metrics(single)

    def test_insufficient_rows_raises(self) -> None:
        """Fewer than 30 rows raises ValueError."""
        tiny = THREE_ASSET_DF.head(10)
        with pytest.raises(ValueError, match="at least"):
            compute_diversification_metrics(tiny)

    def test_weights_not_summing_raises(self) -> None:
        """Weights not summing to 1.0 raises ValueError."""
        bad_weights = {"A": 0.5, "B": 0.5, "C": 0.5}  # sum = 1.5
        with pytest.raises(ValueError, match="sum to 1"):
            compute_diversification_metrics(THREE_ASSET_DF, weights=bad_weights)
