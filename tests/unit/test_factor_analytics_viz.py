"""Smoke tests for factor analytics visualisation functions."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from finbot.core.contracts.factor_analytics import (
    FactorAttributionResult,
    FactorModelType,
    FactorRegressionResult,
    FactorRiskResult,
)
from finbot.services.factor_analytics.viz import (
    plot_factor_attribution,
    plot_factor_correlation,
    plot_factor_loadings,
    plot_factor_risk_decomposition,
    plot_rolling_r_squared,
)


@pytest.fixture()
def reg_result() -> FactorRegressionResult:
    return FactorRegressionResult(
        loadings={"Mkt-RF": 1.1, "SMB": 0.3},
        alpha=0.02,
        r_squared=0.85,
        adj_r_squared=0.84,
        residual_std=0.01,
        t_stats={"alpha": 2.0, "Mkt-RF": 15.0, "SMB": 3.5},
        p_values={"alpha": 0.05, "Mkt-RF": 0.001, "SMB": 0.001},
        factor_names=("Mkt-RF", "SMB"),
        model_type=FactorModelType.CUSTOM,
        n_observations=252,
        annualization_factor=252,
    )


@pytest.fixture()
def attr_result() -> FactorAttributionResult:
    return FactorAttributionResult(
        factor_contributions={"Mkt-RF": 0.05, "SMB": 0.01},
        alpha_contribution=0.005,
        total_return=0.07,
        explained_return=0.065,
        residual_return=0.005,
        factor_names=("Mkt-RF", "SMB"),
        n_observations=252,
    )


@pytest.fixture()
def risk_result() -> FactorRiskResult:
    return FactorRiskResult(
        systematic_variance=0.0004,
        idiosyncratic_variance=0.0001,
        total_variance=0.0005,
        pct_systematic=0.8,
        marginal_contributions={"Mkt-RF": 0.0003, "SMB": 0.0001},
        factor_names=("Mkt-RF", "SMB"),
        n_observations=252,
    )


class TestPlotFactorLoadings:
    def test_returns_figure(self, reg_result: FactorRegressionResult) -> None:
        fig = plot_factor_loadings(reg_result)
        assert isinstance(fig, go.Figure)

    def test_custom_title(self, reg_result: FactorRegressionResult) -> None:
        fig = plot_factor_loadings(reg_result, title="Custom Title")
        assert fig.layout.title.text == "Custom Title"


class TestPlotFactorAttribution:
    def test_returns_figure(self, attr_result: FactorAttributionResult) -> None:
        fig = plot_factor_attribution(attr_result)
        assert isinstance(fig, go.Figure)


class TestPlotFactorRiskDecomposition:
    def test_returns_figure(self, risk_result: FactorRiskResult) -> None:
        fig = plot_factor_risk_decomposition(risk_result)
        assert isinstance(fig, go.Figure)


class TestPlotRollingRSquared:
    def test_returns_figure(self) -> None:
        values = (float("nan"),) * 9 + tuple(0.5 + 0.01 * i for i in range(91))
        dates = tuple(str(i) for i in range(100))
        fig = plot_rolling_r_squared(values, dates)
        assert isinstance(fig, go.Figure)


class TestPlotFactorCorrelation:
    def test_returns_figure(self) -> None:
        rng = np.random.default_rng(42)
        factors = pd.DataFrame(
            {
                "F1": rng.normal(0, 0.01, 100),
                "F2": rng.normal(0, 0.01, 100),
            }
        )
        fig = plot_factor_correlation(factors)
        assert isinstance(fig, go.Figure)

    def test_custom_title(self) -> None:
        rng = np.random.default_rng(42)
        factors = pd.DataFrame(
            {
                "F1": rng.normal(0, 0.01, 100),
                "F2": rng.normal(0, 0.01, 100),
            }
        )
        fig = plot_factor_correlation(factors, title="My Title")
        assert fig.layout.title.text == "My Title"
