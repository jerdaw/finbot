"""Portfolio analytics visualisation functions.

All functions return ``plotly.graph_objects.Figure`` objects.  They are
designed to be used stand-alone or embedded in the Streamlit dashboard.
Never call ``.show()``; the caller handles display.

Colours follow the Wong (2011) colour-blind-safe palette used throughout
the Finbot dashboard.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from finbot.core.contracts.portfolio_analytics import (
    BenchmarkComparisonResult,
    DiversificationResult,
    DrawdownAnalysisResult,
    RollingMetricsResult,
)

_BLUE = "#0072B2"
_ORANGE = "#D55E00"
_GREEN = "#009E73"
_PINK = "#CC79A7"
_YELLOW = "#F0E442"
_LIGHT_BLUE = "#56B4E9"
_RED = "#D55E00"


def plot_rolling_metrics(
    result: RollingMetricsResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Subplot of rolling Sharpe ratio, annualized volatility, and beta.

    Produces 2 rows (Sharpe + Vol) when no beta series is present, or
    3 rows (Sharpe + Vol + Beta) when a benchmark was supplied.

    Args:
        result: ``RollingMetricsResult`` from ``compute_rolling_metrics``.
        title: Optional figure title.  Defaults to an auto-generated label.

    Returns:
        Plotly ``Figure`` with shared x-axis subplots.
    """
    has_beta = result.beta is not None
    n_rows = 3 if has_beta else 2
    subplot_titles = ["Rolling Sharpe Ratio", f"Rolling Volatility (Ann., window={result.window})"]
    if has_beta:
        subplot_titles.append("Rolling Beta vs Benchmark")

    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        subplot_titles=subplot_titles,
        vertical_spacing=0.08,
    )

    x = list(result.dates)

    fig.add_trace(
        go.Scatter(x=x, y=list(result.sharpe), mode="lines", name="Sharpe", line={"color": _BLUE}),
        row=1,
        col=1,
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)

    fig.add_trace(
        go.Scatter(
            x=x,
            y=list(result.volatility),
            mode="lines",
            name="Volatility",
            line={"color": _ORANGE},
        ),
        row=2,
        col=1,
    )

    if has_beta and result.beta is not None:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=list(result.beta),
                mode="lines",
                name="Beta",
                line={"color": _GREEN},
            ),
            row=3,
            col=1,
        )
        fig.add_hline(y=1, line_dash="dash", line_color="gray", row=3, col=1)

    fig.update_layout(
        title=title or f"Rolling Metrics (window = {result.window} bars)",
        height=400 if not has_beta else 550,
        showlegend=True,
    )
    fig.update_yaxes(title_text="Sharpe", row=1, col=1)
    fig.update_yaxes(title_text="Vol (ann.)", row=2, col=1)
    if has_beta:
        fig.update_yaxes(title_text="Beta", row=3, col=1)

    return fig


def plot_benchmark_scatter(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    result: BenchmarkComparisonResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Scatter plot of portfolio vs benchmark returns with OLS regression line.

    Each point is one bar.  The regression line visualises alpha and beta.
    Key statistics (alpha, beta, R², TE, IR) are annotated in the layout.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        benchmark_returns: 1-D array of benchmark period returns.
        result: ``BenchmarkComparisonResult`` from
            ``compute_benchmark_comparison``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with scatter points and a fitted line.
    """
    portfolio_returns = np.asarray(portfolio_returns, dtype=float)
    benchmark_returns = np.asarray(benchmark_returns, dtype=float)

    x_line = np.linspace(float(benchmark_returns.min()), float(benchmark_returns.max()), 200)
    y_line = result.alpha / result.annualization_factor + result.beta * x_line

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=benchmark_returns,
            y=portfolio_returns,
            mode="markers",
            name="Returns",
            marker={"color": _BLUE, "opacity": 0.5, "size": 4},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name=f"OLS (β={result.beta:.2f})",
            line={"color": _ORANGE, "width": 2},
        )
    )

    ann_text = (
        f"a={result.alpha:.2%}/yr  b={result.beta:.2f}  "
        f"R2={result.r_squared:.2f}  TE={result.tracking_error:.2%}  "
        f"IR={result.information_ratio:.2f}"
    )
    fig.update_layout(
        title=title or f"Portfolio vs {result.benchmark_name}",
        xaxis_title=f"{result.benchmark_name} Return",
        yaxis_title="Portfolio Return",
        annotations=[
            {
                "text": ann_text,
                "xref": "paper",
                "yref": "paper",
                "x": 0.01,
                "y": 0.99,
                "showarrow": False,
                "font": {"size": 11},
                "bgcolor": "rgba(255,255,255,0.8)",
            }
        ],
    )
    return fig


def plot_underwater_curve(
    result: DrawdownAnalysisResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Area chart of the portfolio underwater curve.

    The y-axis shows the fractional distance below the prior peak
    (always <= 0).  The filled area is shaded red for emphasis.

    Args:
        result: ``DrawdownAnalysisResult`` from ``compute_drawdown_analysis``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with the full underwater time-series.
    """
    x = list(range(result.n_observations))
    y = list(result.underwater_curve)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="tozeroy",
            name="Drawdown",
            line={"color": _RED, "width": 1},
            fillcolor="rgba(213,94,0,0.25)",
        )
    )
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    fig.update_layout(
        title=title or "Underwater Curve",
        xaxis_title="Bar",
        yaxis_title="Drawdown",
        yaxis_tickformat=".1%",
    )
    return fig


def plot_drawdown_periods(
    result: DrawdownAnalysisResult,
    top_n: int = 5,
    *,
    title: str | None = None,
) -> go.Figure:
    """Horizontal bar chart of the top-N drawdown periods by depth.

    Args:
        result: ``DrawdownAnalysisResult`` from ``compute_drawdown_analysis``.
        top_n: Maximum number of periods to display.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with bars sorted by depth (deepest at top).
    """
    periods = result.periods[:top_n]
    if not periods:
        fig = go.Figure()
        fig.update_layout(title=title or "No Drawdown Periods Detected")
        return fig

    labels = [f"Period {i + 1} (bar {p.start_idx}→{p.trough_idx})" for i, p in enumerate(periods)]
    depths = [p.depth * 100 for p in periods]
    text = [f"{d:.1f}%" for d in depths]

    fig = go.Figure(
        go.Bar(
            x=depths,
            y=labels,
            orientation="h",
            marker_color=_RED,
            text=text,
            textposition="outside",
        )
    )
    fig.update_layout(
        title=title or f"Top {len(periods)} Drawdown Periods by Depth",
        xaxis_title="Drawdown Depth (%)",
        yaxis={"autorange": "reversed"},
    )
    return fig


def plot_correlation_heatmap(
    result: DiversificationResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Annotated correlation heatmap for a multi-asset portfolio.

    Uses a diverging RdBu colour scale centred at zero so that
    positive (negative) correlations appear blue (red).

    Args:
        result: ``DiversificationResult`` from
            ``compute_diversification_metrics``.
        title: Optional figure title.

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
            zmin=-1,
            zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in matrix],
            texttemplate="%{text}",
            showscale=True,
        )
    )
    fig.update_layout(
        title=title or "Asset Correlation Matrix",
        xaxis_title="Asset",
        yaxis_title="Asset",
    )
    return fig


def plot_diversification_weights(
    result: DiversificationResult,
    *,
    title: str | None = None,
) -> go.Figure:
    """Bar chart of portfolio weights with diversification summary.

    Annotates the chart with the effective number of assets (Effective N)
    and the HHI concentration index.

    Args:
        result: ``DiversificationResult`` from
            ``compute_diversification_metrics``.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` bar chart of weights with annotations.
    """
    assets = list(result.weights.keys())
    weights_pct = [result.weights[a] * 100 for a in assets]
    text = [f"{w:.1f}%" for w in weights_pct]

    fig = go.Figure(
        go.Bar(
            x=assets,
            y=weights_pct,
            marker_color=_BLUE,
            text=text,
            textposition="outside",
        )
    )

    ann_text = (
        f"HHI={result.herfindahl_index:.3f}  "
        f"Effective N={result.effective_n:.1f}  "
        f"Div. Ratio={result.diversification_ratio:.2f}"
    )
    fig.update_layout(
        title=title or "Portfolio Weights",
        xaxis_title="Asset",
        yaxis_title="Weight (%)",
        annotations=[
            {
                "text": ann_text,
                "xref": "paper",
                "yref": "paper",
                "x": 0.99,
                "y": 0.99,
                "xanchor": "right",
                "showarrow": False,
                "font": {"size": 11},
                "bgcolor": "rgba(255,255,255,0.8)",
            }
        ],
    )
    return fig
