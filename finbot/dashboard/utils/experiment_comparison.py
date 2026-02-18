"""Utilities for comparing backtest experiments."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from finbot.core.contracts import BacktestRunResult


def build_assumptions_comparison(
    experiments: list[BacktestRunResult],
) -> pd.DataFrame:
    """Build assumptions comparison table showing differences.

    Args:
        experiments: List of backtest results to compare

    Returns:
        DataFrame with assumptions as rows, experiments as columns.
        Only includes assumptions that differ across experiments.
    """
    if not experiments:
        return pd.DataFrame()

    # Extract all assumptions
    all_assumptions: dict[str, dict[str, Any]] = {}

    for exp in experiments:
        exp_id = f"{exp.metadata.run_id[:12]}..."
        all_assumptions[exp_id] = exp.assumptions.copy()

    # Convert to DataFrame (convert unhashable types to strings for comparison)
    df = pd.DataFrame(all_assumptions)

    # Convert lists and dicts to strings for comparison
    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list | dict) else x)

    # Keep only rows where values differ
    rows_to_keep = []
    for idx in df.index:
        unique_vals = df.loc[idx].nunique()
        if unique_vals > 1:
            rows_to_keep.append(idx)

    if rows_to_keep:
        df = df.loc[rows_to_keep]

    return df


def build_metrics_comparison(
    experiments: list[BacktestRunResult],
) -> pd.DataFrame:
    """Build metrics comparison table.

    Args:
        experiments: List of backtest results to compare

    Returns:
        DataFrame with metrics as rows, experiments as columns
    """
    if not experiments:
        return pd.DataFrame()

    # Extract all metrics
    all_metrics: dict[str, dict[str, float]] = {}

    for exp in experiments:
        exp_id = f"{exp.metadata.run_id[:12]}..."
        all_metrics[exp_id] = exp.metrics.copy()

    # Convert to DataFrame
    df = pd.DataFrame(all_metrics)

    return df


def format_metric_value(value: Any) -> str:
    """Format metric value for display.

    Args:
        value: Metric value

    Returns:
        Formatted string
    """
    if isinstance(value, float):
        # Format as percentage if value is between -0.99 and 0.99 (likely a ratio/rate)
        # Exclude values close to 1 or -1 as they might be other metrics
        if -0.99 < value < 0.99 and value != 0:
            return f"{value:.2%}"
        return f"{value:.4f}"
    return str(value)


def highlight_best_worst(
    df: pd.DataFrame,
    higher_is_better: dict[str, bool] | None = None,
) -> pd.io.formats.style.Styler:
    """Apply styling to highlight best and worst values.

    Args:
        df: Metrics DataFrame with metrics as rows, experiments as columns
        higher_is_better: Dict mapping metric name to bool indicating if higher is better.
                         If None, uses defaults for common metrics.

    Returns:
        Styled DataFrame
    """
    if higher_is_better is None:
        # Default assumptions for common metrics
        higher_is_better = {
            "cagr": True,
            "sharpe": True,
            "sortino": True,
            "calmar": True,
            "win_rate": True,
            "profit_factor": True,
            "max_drawdown": False,  # Lower is better (less negative)
            "volatility": False,  # Lower is better
            "var_95": False,  # Lower is better (less negative)
        }

    def highlight_row(row):
        """Highlight best (green) and worst (red) in a row."""
        if row.name not in df.index:
            return [""] * len(row)

        metric_name = str(row.name).lower()
        better_is_higher = higher_is_better.get(metric_name, True)

        # Find best and worst
        if better_is_higher:
            best_val = row.max()
            worst_val = row.min()
        else:
            best_val = row.min()
            worst_val = row.max()

        # Apply colors
        colors = []
        for val in row:
            if pd.isna(val):
                colors.append("")
            elif val == best_val:
                colors.append("background-color: lightgreen")
            elif val == worst_val:
                colors.append("background-color: lightcoral")
            else:
                colors.append("")

        return colors

    return df.style.apply(highlight_row, axis=1)


def plot_metrics_comparison(
    df: pd.DataFrame,
    selected_metrics: list[str] | None = None,
) -> list[go.Figure]:
    """Create bar charts comparing metrics across experiments.

    Args:
        df: Metrics DataFrame with metrics as rows, experiments as columns
        selected_metrics: List of metrics to plot. If None, plots all.

    Returns:
        List of plotly figures
    """
    if df.empty:
        return []

    metrics_to_plot = selected_metrics if selected_metrics else df.index.tolist()
    figures = []

    for metric in metrics_to_plot:
        if metric not in df.index:
            continue

        # Get values for this metric
        values = df.loc[metric]

        # Create bar chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=values.index,
                y=values.values,
                text=[format_metric_value(v) for v in values.values],
                textposition="auto",
                marker_color="steelblue",
            )
        )

        fig.update_layout(
            title=f"{metric.replace('_', ' ').title()} Comparison",
            xaxis_title="Experiment",
            yaxis_title=metric.replace("_", " ").title(),
            height=400,
            showlegend=False,
        )

        figures.append(fig)

    return figures


def export_comparison_csv(
    assumptions_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
) -> str:
    """Export comparison data to CSV format.

    Args:
        assumptions_df: Assumptions comparison DataFrame
        metrics_df: Metrics comparison DataFrame

    Returns:
        CSV string containing both tables
    """
    import io

    output = io.StringIO()

    # Write assumptions
    output.write("# Assumptions Comparison\n")
    if not assumptions_df.empty:
        assumptions_df.to_csv(output)
    output.write("\n")

    # Write metrics
    output.write("# Metrics Comparison\n")
    if not metrics_df.empty:
        metrics_df.to_csv(output)

    return output.getvalue()
