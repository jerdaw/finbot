"""Reusable plotly chart builders for the dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def create_time_series_chart(
    data: dict[str, pd.Series],
    title: str,
    normalize: bool = False,
    y_label: str = "Price",
) -> go.Figure:
    """Create a line chart from multiple time series."""
    fig = go.Figure()
    for name, series in data.items():
        y = series / series.iloc[0] if normalize else series
        fig.add_trace(go.Scatter(x=y.index, y=y.values, mode="lines", name=name))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Normalized ($1 start)" if normalize else y_label,
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def create_histogram_chart(
    data: dict[str, pd.Series],
    title: str,
    bins: int = 50,
) -> go.Figure:
    """Create an overlaid histogram from multiple series."""
    fig = go.Figure()
    for name, series in data.items():
        fig.add_trace(go.Histogram(x=series.dropna().values, nbinsx=bins, name=name, opacity=0.7))
    fig.update_layout(
        title=title,
        xaxis_title="Value",
        yaxis_title="Count",
        barmode="overlay",
        template="plotly_white",
    )
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
) -> go.Figure:
    """Create a grouped bar chart."""
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Bar(x=df[x_col], y=df[col], name=col))
    fig.update_layout(
        title=title,
        barmode="group",
        template="plotly_white",
    )
    return fig


def create_heatmap(
    df: pd.DataFrame,
    title: str,
) -> go.Figure:
    """Create a heatmap from a DataFrame (index=rows, columns=cols)."""
    fig = go.Figure(
        data=go.Heatmap(
            z=df.values,
            x=[str(c) for c in df.columns],
            y=[str(i) for i in df.index],
            colorscale="RdYlGn",
            texttemplate="%{z:.3f}",
        )
    )
    fig.update_layout(title=title, template="plotly_white")
    return fig


def create_fan_chart(
    trials_df: pd.DataFrame,
    title: str,
    max_paths: int = 200,
) -> go.Figure:
    """Create a fan chart from Monte Carlo simulation trials."""
    fig = go.Figure()

    # Plot a sample of individual paths
    n_trials = len(trials_df)
    sample_idx = np.random.default_rng(42).choice(n_trials, min(max_paths, n_trials), replace=False)
    periods = list(range(trials_df.shape[1]))

    for i in sample_idx:
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=trials_df.iloc[i].values,
                mode="lines",
                line={"color": "rgba(100,149,237,0.08)", "width": 0.5},
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Percentile bands
    p5 = trials_df.quantile(0.05)
    p50 = trials_df.quantile(0.50)
    p95 = trials_df.quantile(0.95)

    fig.add_trace(
        go.Scatter(x=periods, y=p95.values, mode="lines", name="95th pctl", line={"color": "green", "dash": "dash"})
    )
    fig.add_trace(go.Scatter(x=periods, y=p50.values, mode="lines", name="Median", line={"color": "blue", "width": 2}))
    fig.add_trace(
        go.Scatter(x=periods, y=p5.values, mode="lines", name="5th pctl", line={"color": "red", "dash": "dash"})
    )

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Price",
        template="plotly_white",
    )
    return fig


def create_drawdown_chart(
    series: pd.Series,
    title: str = "Drawdown",
) -> go.Figure:
    """Create a drawdown chart from a value series."""
    cummax = series.cummax()
    drawdown = (series - cummax) / cummax
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown.values,
            fill="tozeroy",
            mode="lines",
            name="Drawdown",
            line={"color": "red"},
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis_tickformat=".1%",
        template="plotly_white",
    )
    return fig
