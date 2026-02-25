"""Smoke tests for portfolio analytics visualisation functions."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison
from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics
from finbot.services.portfolio_analytics.drawdown import compute_drawdown_analysis
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics
from finbot.services.portfolio_analytics.viz import (
    plot_benchmark_scatter,
    plot_correlation_heatmap,
    plot_diversification_weights,
    plot_drawdown_periods,
    plot_rolling_metrics,
    plot_underwater_curve,
)

RNG = np.random.default_rng(seed=42)
_RETURNS = RNG.normal(0.0005, 0.01, 300)
_BENCH = RNG.normal(0.0003, 0.009, 300)
_DF = pd.DataFrame(
    {
        "A": RNG.normal(0.0005, 0.01, 300),
        "B": RNG.normal(0.0003, 0.012, 300),
    }
)


@pytest.fixture(scope="module")
def rolling_result():  # type: ignore[no-untyped-def]
    return compute_rolling_metrics(_RETURNS, window=30)


@pytest.fixture(scope="module")
def bench_result():  # type: ignore[no-untyped-def]
    return compute_benchmark_comparison(_RETURNS, _BENCH)


@pytest.fixture(scope="module")
def dd_result():  # type: ignore[no-untyped-def]
    return compute_drawdown_analysis(_RETURNS, top_n=5)


@pytest.fixture(scope="module")
def div_result():  # type: ignore[no-untyped-def]
    return compute_diversification_metrics(_DF)


class TestPortfolioAnalyticsViz:
    """Smoke tests verifying each viz function returns a Plotly Figure."""

    def test_plot_rolling_metrics_returns_figure(self, rolling_result) -> None:  # type: ignore[no-untyped-def]
        """plot_rolling_metrics returns a go.Figure."""
        fig = plot_rolling_metrics(rolling_result)
        assert isinstance(fig, go.Figure)

    def test_plot_benchmark_scatter_returns_figure(self, bench_result) -> None:  # type: ignore[no-untyped-def]
        """plot_benchmark_scatter returns a go.Figure."""
        fig = plot_benchmark_scatter(_RETURNS, _BENCH, bench_result)
        assert isinstance(fig, go.Figure)

    def test_plot_underwater_curve_returns_figure(self, dd_result) -> None:  # type: ignore[no-untyped-def]
        """plot_underwater_curve returns a go.Figure."""
        fig = plot_underwater_curve(dd_result)
        assert isinstance(fig, go.Figure)

    def test_plot_drawdown_periods_returns_figure(self, dd_result) -> None:  # type: ignore[no-untyped-def]
        """plot_drawdown_periods returns a go.Figure."""
        fig = plot_drawdown_periods(dd_result)
        assert isinstance(fig, go.Figure)

    def test_plot_correlation_heatmap_returns_figure(self, div_result) -> None:  # type: ignore[no-untyped-def]
        """plot_correlation_heatmap returns a go.Figure."""
        fig = plot_correlation_heatmap(div_result)
        assert isinstance(fig, go.Figure)

    def test_plot_diversification_weights_returns_figure(self, div_result) -> None:  # type: ignore[no-untyped-def]
        """plot_diversification_weights returns a go.Figure."""
        fig = plot_diversification_weights(div_result)
        assert isinstance(fig, go.Figure)
