"""Walk-forward analysis visualization tools.

All functions return plotly go.Figure objects suitable for Streamlit rendering.
They follow the same accessibility conventions as finbot/dashboard/components/charts.py:
- Wong (2011) colorblind-friendly palette
- White background with high-contrast labels
- No .show() calls (caller handles display)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go

from finbot.core.contracts.walkforward import WalkForwardResult

if TYPE_CHECKING:
    pass

# Wong (2011) colorblind-friendly palette — same as charts.py
_COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"]
_BLUE = "#0072B2"
_ORANGE = "#D55E00"
_GREEN = "#009E73"
_LIGHT_BLUE = "#56B4E9"
_GREY = "#888888"

# Metrics that are "better when lower" — invert colorscale for these
_LOWER_IS_BETTER = {"max_drawdown", "volatility", "risk_of_ruin", "expected_shortfall"}


def _accessibility_layout(fig: go.Figure) -> go.Figure:
    """Apply standard accessibility layout settings."""
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "#000000", "size": 12},
        title={"font": {"size": 16, "color": "#000000"}},
        showlegend=True,
        legend={"bgcolor": "rgba(255,255,255,0.8)", "bordercolor": "#000000", "borderwidth": 1},
    )
    return fig


def _fmt_metric(metric: str, value: float) -> str:
    """Format a metric value for display."""
    pct_metrics = {"cagr", "max_drawdown", "volatility", "roi", "best_day", "worst_day"}
    if metric in pct_metrics:
        return f"{value:.2%}"
    return f"{value:.3f}"


def plot_rolling_metric(
    result: WalkForwardResult,
    metric: str = "cagr",
    *,
    include_train: bool = False,
    title: str | None = None,
) -> go.Figure:
    """Rolling out-of-sample metric across walk-forward windows.

    Shows one data point per window (at the test-period end date), plus a
    horizontal reference line at the mean.  Optionally overlays the
    corresponding in-sample metric for train/test comparison.

    Args:
        result: Walk-forward result object.
        metric: Canonical metric key (e.g. "cagr", "sharpe").
        include_train: If True and train_results is non-empty, add an
            in-sample trace.
        title: Override chart title.

    Returns:
        Plotly figure.

    Raises:
        KeyError: If *metric* is not present in any result's metrics dict.
    """
    # Validate metric exists
    if result.test_results and metric not in result.test_results[0].metrics:
        raise KeyError(f"Metric '{metric}' not found in walk-forward results")

    x_dates = [w.test_end for w in result.windows]
    y_test = [r.metrics[metric] for r in result.test_results]
    mean_val = result.summary_metrics.get(f"{metric}_mean", sum(y_test) / max(len(y_test), 1))

    fig = go.Figure()

    # Test (out-of-sample) trace
    fig.add_trace(
        go.Scatter(
            x=x_dates,
            y=y_test,
            mode="lines+markers",
            name=f"OOS {metric.upper()}",
            line={"color": _BLUE, "width": 2},
            marker={"size": 8, "color": _BLUE},
            hovertemplate=(
                f"Window %{{customdata[0]}}<br>Test end: %{{x|%Y-%m-%d}}<br>{metric}: %{{y:.4f}}<extra></extra>"
            ),
            customdata=[[w.window_id] for w in result.windows],
        )
    )

    # Optional train (in-sample) trace
    if include_train and result.train_results:
        y_train = [r.metrics[metric] for r in result.train_results]
        fig.add_trace(
            go.Scatter(
                x=x_dates,
                y=y_train,
                mode="lines+markers",
                name=f"IS {metric.upper()} (train)",
                line={"color": _ORANGE, "width": 2, "dash": "dash"},
                marker={"size": 8, "symbol": "diamond", "color": _ORANGE},
                hovertemplate=(
                    "Window %{customdata[0]}<br>"
                    "Test end: %{x|%Y-%m-%d}<br>"
                    f"Train {metric}: %{{y:.4f}}<extra></extra>"
                ),
                customdata=[[w.window_id] for w in result.windows],
            )
        )

    # Mean reference line
    fig.add_hline(
        y=mean_val,
        line={"color": _GREY, "dash": "dot", "width": 1.5},
        annotation_text=f"Mean: {_fmt_metric(metric, mean_val)}",
        annotation_position="right",
    )

    chart_title = title or f"Walk-Forward {metric.upper()} — Out-of-Sample"
    fig.update_layout(
        title=chart_title,
        xaxis_title="Test-Period End Date",
        yaxis_title=metric.upper(),
        hovermode="x unified",
        template="plotly_white",
    )
    return _accessibility_layout(fig)


def plot_metric_heatmap(
    result: WalkForwardResult,
    metrics: list[str] | None = None,
    *,
    title: str = "Walk-Forward Metric Heatmap",
) -> go.Figure:
    """Heatmap of metrics (rows) x windows (columns).

    Color encodes relative value across windows for each metric row.
    Metrics in _LOWER_IS_BETTER have their colorscale inverted so that
    green always means "better".

    Args:
        result: Walk-forward result object.
        metrics: Metric keys to include (rows). Defaults to five standard
            metrics.
        title: Chart title.

    Returns:
        Plotly figure.
    """
    if metrics is None:
        metrics = ["cagr", "sharpe", "sortino", "max_drawdown", "volatility"]

    # Filter to metrics that actually exist
    available = [m for m in metrics if result.test_results and m in result.test_results[0].metrics]

    window_ids = [str(w.window_id) for w in result.windows]
    z_rows: list[list[float]] = []
    text_rows: list[list[str]] = []

    for m in available:
        vals = [r.metrics[m] for r in result.test_results]
        # Normalise to [0, 1] for colour — invert for lower-is-better
        lo, hi = min(vals), max(vals)
        rng = hi - lo if hi != lo else 1.0
        normalised = [(v - lo) / rng for v in vals]
        if m in _LOWER_IS_BETTER:
            normalised = [1.0 - n for n in normalised]
        z_rows.append(normalised)
        text_rows.append([_fmt_metric(m, v) for v in vals])

    fig = go.Figure(
        data=go.Heatmap(
            z=z_rows,
            x=window_ids,
            y=available,
            text=text_rows,
            texttemplate="%{text}",
            textfont={"size": 10, "color": "#000000"},
            colorscale="RdYlGn",
            showscale=False,
            hovertemplate="Metric: %{y}<br>Window: %{x}<br>Value: %{text}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Window ID",
        yaxis_title="Metric",
        template="plotly_white",
    )
    return _accessibility_layout(fig)


def plot_train_test_scatter(
    result: WalkForwardResult,
    metric: str = "cagr",
    *,
    title: str | None = None,
) -> go.Figure:
    """Scatter of in-sample vs out-of-sample metric, one point per window.

    Points above the diagonal (y = x) represent windows where the strategy
    performed better out-of-sample than in-sample (unlikely but possible).
    Points below the diagonal indicate in-sample over-fitting.

    Args:
        result: Walk-forward result object. Must have non-empty train_results.
        metric: Canonical metric key.
        title: Override chart title.

    Returns:
        Plotly figure.

    Raises:
        ValueError: If train_results is empty.
        KeyError: If *metric* is not in results.
    """
    if not result.train_results:
        raise ValueError("plot_train_test_scatter requires train_results — re-run with include_train=True")

    if result.test_results and metric not in result.test_results[0].metrics:
        raise KeyError(f"Metric '{metric}' not found in walk-forward results")

    x_train = [r.metrics[metric] for r in result.train_results]
    y_test = [r.metrics[metric] for r in result.test_results]
    window_ids = [w.window_id for w in result.windows]

    # Diagonal range
    all_vals = x_train + y_test
    lo, hi = min(all_vals), max(all_vals)
    pad = (hi - lo) * 0.1 or 0.05
    diag = [lo - pad, hi + pad]

    fig = go.Figure()

    # Diagonal reference line (y = x)
    fig.add_trace(
        go.Scatter(
            x=diag,
            y=diag,
            mode="lines",
            name="IS = OOS (y=x)",
            line={"color": _GREY, "dash": "dash", "width": 1.5},
            hoverinfo="skip",
        )
    )

    # Window scatter points — colour by window_id (temporal order)
    fig.add_trace(
        go.Scatter(
            x=x_train,
            y=y_test,
            mode="markers+text",
            name="Windows",
            marker={
                "size": 12,
                "color": window_ids,
                "colorscale": "Blues",
                "showscale": True,
                "colorbar": {"title": "Window"},
                "line": {"color": "#000000", "width": 1},
            },
            text=[f"W{i}" for i in window_ids],
            textposition="top center",
            hovertemplate=(
                f"Window %{{text}}<br>Train {metric}: %{{x:.4f}}<br>Test {metric}: %{{y:.4f}}<extra></extra>"
            ),
        )
    )

    chart_title = title or f"Train vs Test {metric.upper()} — Walk-Forward Windows"
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"In-Sample (Train) {metric.upper()}",
        yaxis_title=f"Out-of-Sample (Test) {metric.upper()}",
        template="plotly_white",
    )
    return _accessibility_layout(fig)


def plot_window_timeline(
    result: WalkForwardResult,
    *,
    title: str = "Walk-Forward Window Timeline",
) -> go.Figure:
    """Gantt-style chart showing train and test periods for each window.

    Each window occupies one row.  The train period is rendered in a lighter
    shade; the test (out-of-sample) period in the darker project blue.

    Args:
        result: Walk-forward result object.
        title: Chart title.

    Returns:
        Plotly figure.
    """
    fig = go.Figure()

    for w in result.windows:
        row_label = f"Window {w.window_id}"
        train_days = (w.train_end - w.train_start).days
        test_days = (w.test_end - w.test_start).days

        # Train bar
        fig.add_trace(
            go.Bar(
                x=[train_days],
                y=[row_label],
                base=[w.train_start],
                orientation="h",
                name="Train" if w.window_id == 0 else None,
                showlegend=(w.window_id == 0),
                marker={"color": _LIGHT_BLUE, "line": {"color": "#000000", "width": 0.5}},
                hovertemplate=(
                    f"Window {w.window_id} — Train<br>"
                    f"Start: {w.train_start.strftime('%Y-%m-%d')}<br>"
                    f"End: {w.train_end.strftime('%Y-%m-%d')}<br>"
                    f"Days: {train_days}<extra></extra>"
                ),
            )
        )

        # Test bar
        fig.add_trace(
            go.Bar(
                x=[test_days],
                y=[row_label],
                base=[w.test_start],
                orientation="h",
                name="Test (OOS)" if w.window_id == 0 else None,
                showlegend=(w.window_id == 0),
                marker={"color": _BLUE, "line": {"color": "#000000", "width": 0.5}},
                hovertemplate=(
                    f"Window {w.window_id} — Test<br>"
                    f"Start: {w.test_start.strftime('%Y-%m-%d')}<br>"
                    f"End: {w.test_end.strftime('%Y-%m-%d')}<br>"
                    f"Days: {test_days}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=title,
        xaxis={
            "type": "date",
            "title": "Date",
        },
        yaxis={"title": "Window", "autorange": "reversed"},
        barmode="overlay",
        template="plotly_white",
    )
    return _accessibility_layout(fig)


def plot_summary_boxplot(
    result: WalkForwardResult,
    metrics: list[str] | None = None,
    *,
    title: str = "Walk-Forward Metric Distribution",
) -> go.Figure:
    """Box plots showing distribution of per-window metric values.

    Each box represents all test-period values for one metric, with
    individual window results shown as overlay points.

    Args:
        result: Walk-forward result object.
        metrics: Metric keys to include. Defaults to three standard metrics.
        title: Chart title.

    Returns:
        Plotly figure.
    """
    if metrics is None:
        metrics = ["cagr", "sharpe", "max_drawdown"]

    # Filter to metrics that exist
    available = [m for m in metrics if result.test_results and m in result.test_results[0].metrics]

    fig = go.Figure()

    for idx, m in enumerate(available):
        vals = [r.metrics[m] for r in result.test_results]
        color = _COLORS[idx % len(_COLORS)]

        fig.add_trace(
            go.Box(
                y=vals,
                name=m.upper(),
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                marker={
                    "color": color,
                    "size": 8,
                    "line": {"color": "#000000", "width": 1},
                },
                line={"color": color},
                fillcolor=f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.3)",
                hovertemplate=f"{m.upper()}: %{{y:.4f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        yaxis_title="Value",
        template="plotly_white",
        showlegend=False,
    )
    return _accessibility_layout(fig)


def build_summary_dataframe(result: WalkForwardResult) -> pd.DataFrame:
    """Build a tidy summary DataFrame from WalkForwardResult.summary_metrics.

    Args:
        result: Walk-forward result object.

    Returns:
        DataFrame with columns [metric, mean, min, max, std, window_count].
    """
    # Collect base metric names
    base_metrics: set[str] = set()
    for key in result.summary_metrics:
        for suffix in ("_mean", "_min", "_max", "_std"):
            if key.endswith(suffix):
                base_metrics.add(key[: -len(suffix)])

    rows = [
        {
            "metric": m,
            "mean": result.summary_metrics.get(f"{m}_mean", float("nan")),
            "min": result.summary_metrics.get(f"{m}_min", float("nan")),
            "max": result.summary_metrics.get(f"{m}_max", float("nan")),
            "std": result.summary_metrics.get(f"{m}_std", float("nan")),
        }
        for m in sorted(base_metrics)
    ]

    df = pd.DataFrame(rows)
    if not df.empty:
        df["window_count"] = int(result.summary_metrics.get("window_count", len(result.windows)))
    return df
