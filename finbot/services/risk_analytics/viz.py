"""Risk analytics visualisation functions.

All functions return ``plotly.graph_objects.Figure`` objects.  They are
designed to be used stand-alone or embedded in the Streamlit dashboard.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from finbot.core.contracts.risk_analytics import (
    CVaRResult,
    KellyResult,
    MultiAssetKellyResult,
    StressTestResult,
    VaRResult,
)


def plot_var_distribution(
    returns: np.ndarray,
    var_results: list[VaRResult],
    cvar_results: list[CVaRResult] | None = None,
) -> go.Figure:
    """Plot the return distribution with VaR/CVaR threshold lines.

    Args:
        returns: Raw daily returns series.
        var_results: One or more ``VaRResult`` objects to overlay.
        cvar_results: Optional ``CVaRResult`` objects to overlay.

    Returns:
        Plotly ``Figure`` with a histogram and vertical threshold lines.
    """
    returns = np.asarray(returns, dtype=float)
    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=returns,
            nbinsx=60,
            name="Returns",
            marker_color="steelblue",
            opacity=0.7,
        )
    )

    for vr in var_results:
        fig.add_vline(
            x=-vr.var,
            line_dash="dash",
            line_color="red",
            annotation_text=f"VaR {vr.method} {vr.confidence:.0%}",
        )

    if cvar_results:
        for cr in cvar_results:
            fig.add_vline(
                x=-cr.cvar,
                line_dash="dot",
                line_color="darkred",
                annotation_text=f"CVaR {cr.method} {cr.confidence:.0%}",
            )

    fig.update_layout(
        title="Return Distribution with VaR / CVaR Thresholds",
        xaxis_title="Daily Return",
        yaxis_title="Count",
        legend_title="Metric",
    )
    return fig


def plot_var_comparison(
    var_results: list[VaRResult],
) -> go.Figure:
    """Bar chart comparing VaR values across methods.

    Args:
        var_results: List of ``VaRResult`` objects to compare.

    Returns:
        Plotly ``Figure`` with one bar per result.
    """
    labels = [f"{r.method} {r.confidence:.0%} {r.horizon_days}d" for r in var_results]
    values = [r.var * 100 for r in var_results]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color="indianred",
            text=[f"{v:.2f}%" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="VaR Comparison by Method",
        yaxis_title="VaR (%)",
        xaxis_title="Method / Confidence / Horizon",
    )
    return fig


def plot_stress_path(
    result: StressTestResult,
) -> go.Figure:
    """Line chart of a single stress scenario price path.

    Args:
        result: ``StressTestResult`` from ``run_stress_test``.

    Returns:
        Plotly ``Figure`` with the full portfolio path over time.
    """
    days = list(range(len(result.price_path)))
    values = list(result.price_path)

    fig = go.Figure(
        go.Scatter(
            x=days,
            y=values,
            mode="lines",
            name=result.scenario_name,
            line={"color": "firebrick", "width": 2},
        )
    )
    fig.add_hline(
        y=result.initial_value,
        line_dash="dash",
        line_color="gray",
        annotation_text="Initial value",
    )
    fig.update_layout(
        title=f"Stress Scenario: {result.scenario_name}",
        xaxis_title="Trading Day",
        yaxis_title="Portfolio Value",
    )
    return fig


def plot_stress_comparison(
    results: dict[str, StressTestResult],
) -> go.Figure:
    """Bar chart comparing max drawdown across multiple stress scenarios.

    Args:
        results: Mapping of scenario key to ``StressTestResult``.

    Returns:
        Plotly ``Figure`` with one bar per scenario.
    """
    labels = [r.scenario_name for r in results.values()]
    drawdowns = [r.max_drawdown_pct for r in results.values()]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=drawdowns,
            marker_color="darkorange",
            text=[f"{d:.1f}%" for d in drawdowns],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Stress Scenario Max Drawdown Comparison",
        yaxis_title="Max Drawdown (%)",
        xaxis_title="Scenario",
    )
    return fig


def plot_kelly_fractions(
    kelly_input: KellyResult | dict[str, KellyResult],
) -> go.Figure:
    """Bar chart of full, half, and quarter Kelly fractions.

    Accepts either a single ``KellyResult`` or a dict mapping asset names
    to ``KellyResult`` objects (as returned by ``MultiAssetKellyResult
    .asset_kelly_results``).

    Args:
        kelly_input: Single or multi-asset Kelly results.

    Returns:
        Plotly ``Figure`` comparing Kelly fraction sizes.
    """
    items = {"Portfolio": kelly_input} if isinstance(kelly_input, KellyResult) else kelly_input

    assets = list(items.keys())
    full = [items[a].full_kelly * 100 for a in assets]
    half = [items[a].half_kelly * 100 for a in assets]
    quarter = [items[a].quarter_kelly * 100 for a in assets]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Full Kelly", x=assets, y=full, marker_color="steelblue"))
    fig.add_trace(go.Bar(name="Half Kelly", x=assets, y=half, marker_color="cornflowerblue"))
    fig.add_trace(go.Bar(name="Quarter Kelly", x=assets, y=quarter, marker_color="lightblue"))
    fig.update_layout(
        barmode="group",
        title="Kelly Fraction Comparison",
        yaxis_title="Kelly Fraction (%)",
        xaxis_title="Asset",
    )
    return fig


def plot_kelly_correlation_heatmap(
    result: MultiAssetKellyResult,
) -> go.Figure:
    """Heatmap of the multi-asset correlation matrix.

    Args:
        result: ``MultiAssetKellyResult`` from ``compute_multi_asset_kelly``.

    Returns:
        Plotly ``Figure`` heatmap with annotated correlation values.
    """
    assets = list(result.correlation_matrix.keys())
    matrix = [[result.correlation_matrix[a][b] for b in assets] for a in assets]

    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=assets,
            y=assets,
            colorscale="RdBu",
            zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in matrix],
            texttemplate="%{text}",
            showscale=True,
        )
    )
    fig.update_layout(
        title="Asset Correlation Matrix",
        xaxis_title="Asset",
        yaxis_title="Asset",
    )
    return fig
