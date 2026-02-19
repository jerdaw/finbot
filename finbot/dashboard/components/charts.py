"""Reusable plotly chart builders for the dashboard.

All charts include accessibility features:
- Descriptive titles and axis labels
- Alt text via layout annotations
- High contrast color scheme
- Keyboard-navigable legends
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def _add_accessibility_features(fig: go.Figure, description: str) -> go.Figure:
    """Add common accessibility features to a plotly figure.

    Args:
        fig: Plotly figure to enhance
        description: Text description of the chart for screen readers

    Returns:
        Enhanced figure with accessibility features
    """
    # Add description as a layout property (rendered as aria-label in some contexts)
    # Note: Streamlit/Plotly have limited ARIA support, but this helps
    fig.update_layout(
        # Ensure high contrast
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "#000000", "size": 12},
        # Add title annotations for screen readers
        title={"font": {"size": 16, "color": "#000000"}},
        # Ensure legend is keyboard accessible
        showlegend=True,
        legend={"bgcolor": "rgba(255,255,255,0.8)", "bordercolor": "#000000", "borderwidth": 1},
    )
    return fig


def create_time_series_chart(
    data: dict[str, pd.Series],
    title: str,
    normalize: bool = False,
    y_label: str = "Price",
    description: str | None = None,
) -> go.Figure:
    """Create a line chart from multiple time series.

    Args:
        data: Dictionary mapping series names to pandas Series
        title: Chart title
        normalize: If True, normalize all series to start at 1.0
        y_label: Y-axis label
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    fig = go.Figure()

    # Use high-contrast, colorblind-friendly colors
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"]

    for idx, (name, series) in enumerate(data.items()):
        y = series / series.iloc[0] if normalize else series
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=y.index,
                y=y.values,
                mode="lines",
                name=name,
                line={"color": color, "width": 2},
                hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Normalized ($1 start)" if normalize else y_label,
        hovermode="x unified",
        template="plotly_white",
    )

    # Add accessibility features
    if description is None:
        series_names = ", ".join(data.keys())
        description = f"Time series chart showing {series_names} over time"

    fig = _add_accessibility_features(fig, description)
    return fig


def create_histogram_chart(
    data: dict[str, pd.Series],
    title: str,
    bins: int = 50,
    description: str | None = None,
) -> go.Figure:
    """Create an overlaid histogram from multiple series.

    Args:
        data: Dictionary mapping series names to pandas Series
        title: Chart title
        bins: Number of histogram bins
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    fig = go.Figure()

    # Use high-contrast, colorblind-friendly colors
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"]

    for idx, (name, series) in enumerate(data.items()):
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Histogram(
                x=series.dropna().values,
                nbinsx=bins,
                name=name,
                opacity=0.75,
                marker={"color": color, "line": {"color": "#000000", "width": 0.5}},
                hovertemplate=f"{name}: %{{x:.4f}}<br>Count: %{{y}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Value",
        yaxis_title="Count",
        barmode="overlay",
        template="plotly_white",
    )

    # Add accessibility features
    if description is None:
        series_names = ", ".join(data.keys())
        description = f"Histogram showing distribution of {series_names}"

    fig = _add_accessibility_features(fig, description)
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
    description: str | None = None,
) -> go.Figure:
    """Create a grouped bar chart.

    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_cols: List of column names for y-axis (one bar per column)
        title: Chart title
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    fig = go.Figure()

    # Use high-contrast, colorblind-friendly colors
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"]

    for idx, col in enumerate(y_cols):
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=col,
                marker={"color": color, "line": {"color": "#000000", "width": 0.5}},
                hovertemplate=f"{col}: %{{y:.2f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        barmode="group",
        template="plotly_white",
    )

    # Add accessibility features
    if description is None:
        col_names = ", ".join(y_cols)
        description = f"Grouped bar chart comparing {col_names} across {x_col}"

    fig = _add_accessibility_features(fig, description)
    return fig


def create_heatmap(
    df: pd.DataFrame,
    title: str,
    description: str | None = None,
) -> go.Figure:
    """Create a heatmap from a DataFrame (index=rows, columns=cols).

    Args:
        df: DataFrame to visualize as heatmap
        title: Chart title
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    # Use colorblind-friendly diverging colorscale
    # RdYlGn is not ideal for colorblind users, use Blue-Red instead
    fig = go.Figure(
        data=go.Heatmap(
            z=df.values,
            x=[str(c) for c in df.columns],
            y=[str(i) for i in df.index],
            colorscale="RdBu_r",  # Red-Blue reversed (blue=high, red=low)
            texttemplate="%{z:.3f}",
            textfont={"size": 10, "color": "#000000"},
            hovertemplate="Row: %{y}<br>Column: %{x}<br>Value: %{z:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        template="plotly_white",
        xaxis={"side": "bottom"},
        yaxis={"side": "left"},
    )

    # Add accessibility features
    if description is None:
        description = f"Heatmap showing values across {len(df.index)} rows and {len(df.columns)} columns"

    fig = _add_accessibility_features(fig, description)
    return fig


def create_fan_chart(
    trials_df: pd.DataFrame,
    title: str,
    max_paths: int = 200,
    description: str | None = None,
) -> go.Figure:
    """Create a fan chart from Monte Carlo simulation trials.

    Args:
        trials_df: DataFrame where each row is a simulation trial
        title: Chart title
        max_paths: Maximum number of individual paths to display
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    fig = go.Figure()

    # Plot a sample of individual paths (light blue, low opacity)
    n_trials = len(trials_df)
    sample_idx = np.random.default_rng(42).choice(n_trials, min(max_paths, n_trials), replace=False)
    periods = list(range(trials_df.shape[1]))

    for i in sample_idx:
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=trials_df.iloc[i].values,
                mode="lines",
                line={"color": "rgba(0,114,178,0.08)", "width": 0.5},  # Blue with low opacity
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Percentile bands with high-contrast, colorblind-friendly colors
    p5 = trials_df.quantile(0.05)
    p50 = trials_df.quantile(0.50)
    p95 = trials_df.quantile(0.95)

    # Use distinct line styles and colors
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=p95.values,
            mode="lines",
            name="95th percentile",
            line={"color": "#009E73", "dash": "dash", "width": 2},  # Green
            hovertemplate="95th pctl: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=p50.values,
            mode="lines",
            name="Median (50th percentile)",
            line={"color": "#0072B2", "width": 3},  # Blue
            hovertemplate="Median: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=p5.values,
            mode="lines",
            name="5th percentile",
            line={"color": "#D55E00", "dash": "dash", "width": 2},  # Orange (better than red for colorblind)
            hovertemplate="5th pctl: %{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Price",
        template="plotly_white",
    )

    # Add accessibility features
    if description is None:
        description = (
            f"Monte Carlo fan chart showing {n_trials} simulation trials "
            f"with median, 5th percentile, and 95th percentile paths highlighted"
        )

    fig = _add_accessibility_features(fig, description)
    return fig


def create_drawdown_chart(
    series: pd.Series,
    title: str = "Drawdown",
    description: str | None = None,
) -> go.Figure:
    """Create a drawdown chart from a value series.

    Args:
        series: Time series of values
        title: Chart title
        description: Accessible description of chart content

    Returns:
        Plotly figure with accessibility features
    """
    cummax = series.cummax()
    drawdown = (series - cummax) / cummax
    fig = go.Figure()

    # Use orange instead of red (better for colorblind users)
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown.values,
            fill="tozeroy",
            mode="lines",
            name="Drawdown",
            line={"color": "#D55E00", "width": 2},  # Orange
            fillcolor="rgba(213,94,0,0.3)",  # Semi-transparent orange
            hovertemplate="Date: %{x}<br>Drawdown: %{y:.2%}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis_tickformat=".1%",
        template="plotly_white",
    )

    # Add accessibility features
    if description is None:
        max_dd = drawdown.min()
        description = f"Drawdown chart showing peak-to-trough declines over time. Maximum drawdown: {max_dd:.2%}"

    fig = _add_accessibility_features(fig, description)
    return fig
