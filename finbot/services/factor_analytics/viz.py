"""Factor analytics visualisation functions.

All functions return ``plotly.graph_objects.Figure`` objects.  They are
designed to be used stand-alone or embedded in the Streamlit dashboard.
Never call ``.show()``; the caller handles display.

Colours follow the Wong (2011) colour-blind-safe palette used throughout
the Finbot dashboard.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from finbot.core.contracts.factor_analytics import (
    FactorAttributionResult,
    FactorRegressionResult,
    FactorRiskResult,
)

_BLUE = "#0072B2"
_ORANGE = "#D55E00"
_GREEN = "#009E73"
_PINK = "#CC79A7"
_YELLOW = "#F0E442"
_LIGHT_BLUE = "#56B4E9"

_PALETTE = [_BLUE, _ORANGE, _GREEN, _PINK, _YELLOW, _LIGHT_BLUE]


def plot_factor_loadings(
    result: FactorRegressionResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Horizontal bar chart of factor loadings with confidence intervals.

    Error bars are derived from the t-statistics: ``se = loading / t_stat``,
    displayed as +/- 1.96 * se (95% CI).

    Args:
        result: ``FactorRegressionResult`` from ``compute_factor_regression``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with horizontal bars and error bars.
    """
    names = list(result.factor_names)
    loadings = [result.loadings[n] for n in names]

    # Standard errors from t-stats
    errors = []
    for n in names:
        t = result.t_stats.get(n, 0.0)
        loading = result.loadings[n]
        se = abs(loading / t) if abs(t) > 1e-12 else 0.0
        errors.append(1.96 * se)

    fig = go.Figure(
        go.Bar(
            x=loadings,
            y=names,
            orientation="h",
            marker_color=_BLUE,
            error_x={"type": "data", "array": errors, "visible": True, "color": _ORANGE},
            text=[f"{v:.3f}" for v in loadings],
            textposition="outside",
        )
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title=title or "Factor Loadings (95% CI)",
        xaxis_title="Loading (Beta)",
        yaxis_title="Factor",
        yaxis={"autorange": "reversed"},
    )
    return fig


def plot_factor_attribution(
    result: FactorAttributionResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Grouped bar chart of per-factor, alpha, and residual contributions.

    Args:
        result: ``FactorAttributionResult`` from ``compute_factor_attribution``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with one bar per component.
    """
    labels = [*list(result.factor_names), "Alpha", "Residual"]
    values = [result.factor_contributions[n] for n in result.factor_names]
    values.extend([result.alpha_contribution, result.residual_return])

    colors = []
    for i, _name in enumerate(result.factor_names):
        colors.append(_PALETTE[i % len(_PALETTE)])
    colors.append(_GREEN)
    colors.append(_PINK)

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=[v * 100 for v in values],
            marker_color=colors,
            text=[f"{v * 100:.2f}%" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=title or "Return Attribution by Factor",
        xaxis_title="Component",
        yaxis_title="Contribution (%)",
    )
    return fig


def plot_factor_risk_decomposition(
    result: FactorRiskResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Donut chart of systematic vs idiosyncratic variance.

    Args:
        result: ``FactorRiskResult`` from ``compute_factor_risk``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with a donut chart.
    """
    labels = ["Systematic", "Idiosyncratic"]
    values = [result.systematic_variance, result.idiosyncratic_variance]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker_colors=[_BLUE, _ORANGE],
            textinfo="label+percent",
            textposition="outside",
        )
    )
    pct_text = f"{result.pct_systematic:.1%} systematic"
    fig.update_layout(
        title=title or f"Risk Decomposition ({pct_text})",
        annotations=[
            {
                "text": pct_text,
                "x": 0.5,
                "y": 0.5,
                "font_size": 14,
                "showarrow": False,
            }
        ],
    )
    return fig


def plot_rolling_r_squared(
    values: tuple[float, ...],
    dates: tuple[str, ...],
    *,
    title: str | None = None,
) -> go.Figure:
    """Line chart of rolling R-squared with a 0.5 reference line.

    Args:
        values: R-squared at each bar (NaN for initial positions).
        dates: String labels for the x-axis.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with a line chart and reference line.
    """
    fig = go.Figure(
        go.Scatter(
            x=list(dates),
            y=list(values),
            mode="lines",
            name="R-squared",
            line={"color": _BLUE, "width": 2},
        )
    )
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="R²=0.5")
    fig.update_layout(
        title=title or "Rolling R-squared (Factor Model Fit)",
        xaxis_title="Date",
        yaxis_title="R-squared",
        yaxis={"range": [0, 1]},
    )
    return fig


def plot_factor_correlation(
    factor_returns: pd.DataFrame,
    *,
    title: str | None = None,
) -> go.Figure:
    """Heatmap of pairwise factor correlations.

    Uses a diverging RdBu colour scale centred at zero.

    Args:
        factor_returns: DataFrame with one column per factor.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` heatmap with annotated correlation values.
    """
    arr = factor_returns.to_numpy(dtype=float)
    corr = np.corrcoef(arr, rowvar=False)
    factors = [str(c) for c in factor_returns.columns]

    matrix = [[float(corr[i, j]) for j in range(len(factors))] for i in range(len(factors))]

    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=factors,
            y=factors,
            colorscale="RdBu",
            zmid=0,
            zmin=-1,
            zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in matrix],
            texttemplate="%{text}",
            showscale=True,
        )
    )
    fig.update_layout(
        title=title or "Factor Correlation Matrix",
        xaxis_title="Factor",
        yaxis_title="Factor",
    )
    return fig
