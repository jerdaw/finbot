"""Tests for portfolio analytics frozen dataclass contracts."""

from __future__ import annotations

import pytest

from finbot.core.contracts.portfolio_analytics import (
    BenchmarkComparisonResult,
    DiversificationResult,
    DrawdownAnalysisResult,
    DrawdownPeriod,
    RollingMetricsResult,
)

# ── RollingMetricsResult ───────────────────────────────────────────────────────


class TestRollingMetricsResult:
    """Tests for RollingMetricsResult construction and validation."""

    def test_valid_construction(self) -> None:
        """Constructs without error for a valid input."""
        result = RollingMetricsResult(
            window=10,
            n_obs=100,
            sharpe=tuple([float("nan")] * 9 + [1.0] * 91),
            volatility=tuple([float("nan")] * 9 + [0.15] * 91),
            beta=None,
            dates=tuple(str(i) for i in range(100)),
            annualization_factor=252,
        )
        assert result.window == 10
        assert result.n_obs == 100

    def test_window_too_small_raises(self) -> None:
        """window < 2 raises ValueError."""
        with pytest.raises(ValueError, match="window must be >= 2"):
            RollingMetricsResult(
                window=1,
                n_obs=50,
                sharpe=tuple([1.0] * 50),
                volatility=tuple([0.1] * 50),
                beta=None,
                dates=tuple(str(i) for i in range(50)),
                annualization_factor=252,
            )

    def test_n_obs_less_than_window_raises(self) -> None:
        """n_obs < window raises ValueError."""
        with pytest.raises(ValueError, match="n_obs"):
            RollingMetricsResult(
                window=20,
                n_obs=10,
                sharpe=tuple([1.0] * 10),
                volatility=tuple([0.1] * 10),
                beta=None,
                dates=tuple(str(i) for i in range(10)),
                annualization_factor=252,
            )

    def test_tuple_length_mismatch_raises(self) -> None:
        """sharpe and volatility of different lengths raises ValueError."""
        with pytest.raises(ValueError, match="sharpe length"):
            RollingMetricsResult(
                window=5,
                n_obs=10,
                sharpe=tuple([1.0] * 10),
                volatility=tuple([0.1] * 8),  # wrong length
                beta=None,
                dates=tuple(str(i) for i in range(10)),
                annualization_factor=252,
            )

    def test_beta_length_mismatch_raises(self) -> None:
        """beta length different from sharpe length raises ValueError."""
        with pytest.raises(ValueError, match="beta length"):
            RollingMetricsResult(
                window=5,
                n_obs=10,
                sharpe=tuple([1.0] * 10),
                volatility=tuple([0.1] * 10),
                beta=tuple([0.9] * 7),  # wrong length
                dates=tuple(str(i) for i in range(10)),
                annualization_factor=252,
            )

    def test_invalid_annualization_raises(self) -> None:
        """annualization_factor < 1 raises ValueError."""
        with pytest.raises(ValueError, match="annualization_factor"):
            RollingMetricsResult(
                window=5,
                n_obs=10,
                sharpe=tuple([1.0] * 10),
                volatility=tuple([0.1] * 10),
                beta=None,
                dates=tuple(str(i) for i in range(10)),
                annualization_factor=0,
            )


# ── BenchmarkComparisonResult ──────────────────────────────────────────────────


class TestBenchmarkComparisonResult:
    """Tests for BenchmarkComparisonResult construction and validation."""

    def test_valid_construction(self) -> None:
        """Constructs without error for valid inputs."""
        result = BenchmarkComparisonResult(
            alpha=0.02,
            beta=1.1,
            r_squared=0.85,
            tracking_error=0.03,
            information_ratio=0.67,
            up_capture=1.05,
            down_capture=0.95,
            benchmark_name="SPY",
            n_observations=252,
            annualization_factor=252,
        )
        assert result.alpha == pytest.approx(0.02)

    def test_r_squared_above_one_raises(self) -> None:
        """r_squared > 1 raises ValueError."""
        with pytest.raises(ValueError, match="r_squared"):
            BenchmarkComparisonResult(
                alpha=0.01,
                beta=1.0,
                r_squared=1.5,
                tracking_error=0.02,
                information_ratio=0.5,
                up_capture=1.0,
                down_capture=1.0,
                benchmark_name="SPY",
                n_observations=100,
                annualization_factor=252,
            )

    def test_tracking_error_negative_raises(self) -> None:
        """tracking_error < 0 raises ValueError."""
        with pytest.raises(ValueError, match="tracking_error"):
            BenchmarkComparisonResult(
                alpha=0.01,
                beta=1.0,
                r_squared=0.9,
                tracking_error=-0.01,
                information_ratio=0.5,
                up_capture=1.0,
                down_capture=1.0,
                benchmark_name="SPY",
                n_observations=100,
                annualization_factor=252,
            )

    def test_n_observations_too_small_raises(self) -> None:
        """n_observations < 2 raises ValueError."""
        with pytest.raises(ValueError, match="n_observations"):
            BenchmarkComparisonResult(
                alpha=0.01,
                beta=1.0,
                r_squared=0.9,
                tracking_error=0.02,
                information_ratio=0.5,
                up_capture=1.0,
                down_capture=1.0,
                benchmark_name="SPY",
                n_observations=1,
                annualization_factor=252,
            )


# ── DrawdownPeriod ─────────────────────────────────────────────────────────────


class TestDrawdownPeriod:
    """Tests for DrawdownPeriod construction and validation."""

    def test_valid_recovered_period(self) -> None:
        """Constructs without error for a fully-recovered drawdown."""
        period = DrawdownPeriod(
            start_idx=10,
            trough_idx=25,
            end_idx=40,
            depth=0.15,
            duration_bars=15,
            recovery_bars=15,
        )
        assert period.depth == pytest.approx(0.15)

    def test_valid_unrecovered_period(self) -> None:
        """Constructs without error when end_idx is None."""
        period = DrawdownPeriod(
            start_idx=5,
            trough_idx=20,
            end_idx=None,
            depth=0.30,
            duration_bars=15,
            recovery_bars=None,
        )
        assert period.end_idx is None

    def test_trough_before_start_raises(self) -> None:
        """trough_idx < start_idx raises ValueError."""
        with pytest.raises(ValueError, match="trough_idx"):
            DrawdownPeriod(
                start_idx=20,
                trough_idx=10,
                end_idx=30,
                depth=0.10,
                duration_bars=10,
                recovery_bars=20,
            )

    def test_end_before_trough_raises(self) -> None:
        """end_idx < trough_idx raises ValueError."""
        with pytest.raises(ValueError, match="end_idx"):
            DrawdownPeriod(
                start_idx=10,
                trough_idx=25,
                end_idx=20,
                depth=0.10,
                duration_bars=15,
                recovery_bars=5,
            )

    def test_negative_depth_raises(self) -> None:
        """Negative depth raises ValueError."""
        with pytest.raises(ValueError, match="depth"):
            DrawdownPeriod(
                start_idx=10,
                trough_idx=20,
                end_idx=30,
                depth=-0.10,
                duration_bars=10,
                recovery_bars=10,
            )


# ── DrawdownAnalysisResult ─────────────────────────────────────────────────────


class TestDrawdownAnalysisResult:
    """Tests for DrawdownAnalysisResult construction and validation."""

    def _make_period(self) -> DrawdownPeriod:
        return DrawdownPeriod(
            start_idx=0,
            trough_idx=5,
            end_idx=10,
            depth=0.10,
            duration_bars=5,
            recovery_bars=5,
        )

    def test_valid_construction(self) -> None:
        """Constructs without error for valid inputs."""
        p = self._make_period()
        result = DrawdownAnalysisResult(
            periods=(p,),
            underwater_curve=tuple([-0.05] * 10),
            n_periods=1,
            max_depth=0.10,
            avg_depth=0.10,
            avg_duration_bars=5.0,
            avg_recovery_bars=5.0,
            current_drawdown=0.0,
            n_observations=10,
        )
        assert result.n_periods == 1

    def test_n_periods_mismatch_raises(self) -> None:
        """n_periods != len(periods) raises ValueError."""
        p = self._make_period()
        with pytest.raises(ValueError, match="n_periods"):
            DrawdownAnalysisResult(
                periods=(p,),
                underwater_curve=tuple([-0.05] * 10),
                n_periods=99,  # wrong
                max_depth=0.10,
                avg_depth=0.10,
                avg_duration_bars=5.0,
                avg_recovery_bars=None,
                current_drawdown=0.0,
                n_observations=10,
            )

    def test_underwater_curve_length_mismatch_raises(self) -> None:
        """underwater_curve length != n_observations raises ValueError."""
        p = self._make_period()
        with pytest.raises(ValueError, match="underwater_curve length"):
            DrawdownAnalysisResult(
                periods=(p,),
                underwater_curve=tuple([-0.05] * 5),  # wrong length
                n_periods=1,
                max_depth=0.10,
                avg_depth=0.10,
                avg_duration_bars=5.0,
                avg_recovery_bars=None,
                current_drawdown=0.0,
                n_observations=10,
            )


# ── DiversificationResult ──────────────────────────────────────────────────────


class TestDiversificationResult:
    """Tests for DiversificationResult construction and validation."""

    def _valid_kwargs(self) -> dict:  # type: ignore[type-arg]
        corr = {"A": {"A": 1.0, "B": 0.3}, "B": {"A": 0.3, "B": 1.0}}
        return {
            "n_assets": 2,
            "weights": {"A": 0.6, "B": 0.4},
            "herfindahl_index": 0.52,
            "effective_n": 1.923,
            "diversification_ratio": 1.1,
            "avg_pairwise_correlation": 0.3,
            "correlation_matrix": corr,
            "individual_vols": {"A": 0.15, "B": 0.12},
            "portfolio_vol": 0.13,
            "n_observations": 252,
            "annualization_factor": 252,
        }

    def test_valid_construction(self) -> None:
        """Constructs without error for valid inputs."""
        result = DiversificationResult(**self._valid_kwargs())
        assert result.n_assets == 2

    def test_n_assets_less_than_two_raises(self) -> None:
        """n_assets < 2 raises ValueError."""
        kw = self._valid_kwargs()
        kw["n_assets"] = 1
        with pytest.raises(ValueError, match="n_assets"):
            DiversificationResult(**kw)

    def test_hhi_out_of_range_raises(self) -> None:
        """herfindahl_index > 1 raises ValueError."""
        kw = self._valid_kwargs()
        kw["herfindahl_index"] = 1.5
        with pytest.raises(ValueError, match="herfindahl_index"):
            DiversificationResult(**kw)

    def test_weights_not_summing_raises(self) -> None:
        """Weights summing to != 1 raises ValueError."""
        kw = self._valid_kwargs()
        kw["weights"] = {"A": 0.5, "B": 0.5 + 1e-6}  # sum != 1
        with pytest.raises(ValueError, match="weights must sum"):
            DiversificationResult(**kw)
