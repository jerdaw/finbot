"""Smoke tests for risk analytics visualisation functions."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from finbot.services.risk_analytics.kelly import compute_kelly_from_returns, compute_multi_asset_kelly
from finbot.services.risk_analytics.stress import run_all_scenarios
from finbot.services.risk_analytics.var import compute_cvar, compute_var
from finbot.services.risk_analytics.viz import (
    plot_kelly_correlation_heatmap,
    plot_kelly_fractions,
    plot_stress_comparison,
    plot_stress_path,
    plot_var_comparison,
    plot_var_distribution,
)

RNG = np.random.default_rng(seed=42)
RETURNS = RNG.normal(0.001, 0.01, 500)


@pytest.fixture
def var_results() -> list:
    """VaR results for all three methods."""
    return [
        compute_var(RETURNS, confidence=0.95, method="historical"),
        compute_var(RETURNS, confidence=0.95, method="parametric"),
        compute_var(RETURNS, confidence=0.95, method="montecarlo"),
    ]


@pytest.fixture
def cvar_results() -> list:
    """CVaR results."""
    return [compute_cvar(RETURNS, confidence=0.95, method="historical")]


@pytest.fixture
def stress_results() -> dict:
    """All four stress scenario results."""
    return run_all_scenarios(RETURNS)


@pytest.fixture
def kelly_result():
    """Single-asset Kelly result."""
    return compute_kelly_from_returns(RETURNS)


@pytest.fixture
def multi_kelly():
    """Multi-asset Kelly result."""
    returns2 = RNG.normal(0.002, 0.015, 500)
    df = pd.DataFrame({"SPY": RETURNS, "TLT": returns2})
    return compute_multi_asset_kelly(df)


def test_plot_var_distribution_returns_figure(var_results, cvar_results) -> None:
    """plot_var_distribution returns a go.Figure."""
    fig = plot_var_distribution(RETURNS, var_results, cvar_results)
    assert isinstance(fig, go.Figure)


def test_plot_var_comparison_returns_figure(var_results) -> None:
    """plot_var_comparison returns a go.Figure."""
    fig = plot_var_comparison(var_results)
    assert isinstance(fig, go.Figure)


def test_plot_stress_path_returns_figure(stress_results) -> None:
    """plot_stress_path returns a go.Figure."""
    result = stress_results["2008_financial_crisis"]
    fig = plot_stress_path(result)
    assert isinstance(fig, go.Figure)


def test_plot_stress_comparison_returns_figure(stress_results) -> None:
    """plot_stress_comparison returns a go.Figure."""
    fig = plot_stress_comparison(stress_results)
    assert isinstance(fig, go.Figure)


def test_plot_kelly_fractions_single_returns_figure(kelly_result) -> None:
    """plot_kelly_fractions with single KellyResult returns a go.Figure."""
    fig = plot_kelly_fractions(kelly_result)
    assert isinstance(fig, go.Figure)


def test_plot_kelly_fractions_dict_returns_figure(multi_kelly) -> None:
    """plot_kelly_fractions with dict input returns a go.Figure."""
    fig = plot_kelly_fractions(multi_kelly.asset_kelly_results)
    assert isinstance(fig, go.Figure)


def test_plot_kelly_correlation_heatmap_returns_figure(multi_kelly) -> None:
    """plot_kelly_correlation_heatmap returns a go.Figure."""
    fig = plot_kelly_correlation_heatmap(multi_kelly)
    assert isinstance(fig, go.Figure)
