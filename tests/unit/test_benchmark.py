"""Tests for benchmark comparison analytics."""

from __future__ import annotations

import math

import numpy as np
import pytest

from finbot.core.contracts.portfolio_analytics import BenchmarkComparisonResult
from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison

RNG = np.random.default_rng(seed=42)
BENCHMARK = RNG.normal(0.0005, 0.01, 500)
PORTFOLIO = BENCHMARK * 1.1 + RNG.normal(0.0002, 0.003, 500)  # correlated, slightly higher return
UNCORRELATED = RNG.normal(0.0004, 0.01, 500)


class TestComputeBenchmarkComparison:
    """Tests for compute_benchmark_comparison function."""

    def test_returns_correct_type(self) -> None:
        """Returns a BenchmarkComparisonResult instance."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert isinstance(result, BenchmarkComparisonResult)

    def test_benchmark_name_stored(self) -> None:
        """benchmark_name is stored in the result."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK, benchmark_name="ACME_IDX")
        assert result.benchmark_name == "ACME_IDX"

    def test_n_observations_stored(self) -> None:
        """n_observations equals the length of the input arrays."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert result.n_observations == len(PORTFOLIO)

    def test_r_squared_in_valid_range(self) -> None:
        """r_squared is in [0, 1]."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert 0.0 <= result.r_squared <= 1.0

    def test_tracking_error_non_negative(self) -> None:
        """tracking_error is >= 0."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert result.tracking_error >= 0.0

    def test_perfect_replication_beta_near_one(self) -> None:
        """Portfolio identical to benchmark gives beta ~= 1."""
        result = compute_benchmark_comparison(BENCHMARK, BENCHMARK)
        assert result.beta == pytest.approx(1.0, abs=1e-6)

    def test_perfect_replication_alpha_near_zero(self) -> None:
        """Portfolio identical to benchmark gives alpha ~= 0."""
        result = compute_benchmark_comparison(BENCHMARK, BENCHMARK)
        assert result.alpha == pytest.approx(0.0, abs=1e-6)

    def test_perfect_replication_tracking_error_near_zero(self) -> None:
        """Portfolio identical to benchmark has tracking error ~= 0."""
        result = compute_benchmark_comparison(BENCHMARK, BENCHMARK)
        assert result.tracking_error == pytest.approx(0.0, abs=1e-10)

    def test_uncorrelated_returns_low_r_squared(self) -> None:
        """Uncorrelated portfolio has low R²."""
        result = compute_benchmark_comparison(UNCORRELATED, BENCHMARK)
        assert result.r_squared < 0.1

    def test_high_correlation_high_r_squared(self) -> None:
        """Highly correlated portfolio has high R²."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert result.r_squared > 0.8

    def test_information_ratio_finite_when_te_positive(self) -> None:
        """Information ratio is finite when tracking error is positive."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        if result.tracking_error > 0:
            assert math.isfinite(result.information_ratio)

    def test_up_down_capture_computed(self) -> None:
        """up_capture and down_capture are finite numbers."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK)
        assert math.isfinite(result.up_capture)
        assert math.isfinite(result.down_capture)

    def test_length_mismatch_raises(self) -> None:
        """Arrays of different length raise ValueError."""
        with pytest.raises(ValueError, match="length"):
            compute_benchmark_comparison(PORTFOLIO[:100], BENCHMARK)

    def test_insufficient_data_raises(self) -> None:
        """Fewer than 30 observations raises ValueError."""
        with pytest.raises(ValueError, match="observations"):
            compute_benchmark_comparison(np.zeros(10), np.zeros(10))

    def test_annualization_factor_stored(self) -> None:
        """annualization_factor is stored in the result."""
        result = compute_benchmark_comparison(PORTFOLIO, BENCHMARK, annualization_factor=52)
        assert result.annualization_factor == 52
