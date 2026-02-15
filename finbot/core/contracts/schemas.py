"""Schema helpers for canonical contract data structures."""

from __future__ import annotations

from typing import Any

import pandas as pd

BAR_DATAFRAME_COLUMNS = ("Open", "High", "Low", "Close", "Volume")

BACKTEST_STATS_COLUMN_TO_METRIC = {
    "Starting Value": "starting_value",
    "Ending Value": "ending_value",
    "ROI": "roi",
    "CAGR": "cagr",
    "Sharpe": "sharpe",
    "Max Drawdown": "max_drawdown",
    "Mean Cash Utilization": "mean_cash_utilization",
}

CANONICAL_METRIC_KEYS = tuple(BACKTEST_STATS_COLUMN_TO_METRIC.values())


def validate_bar_dataframe(df: pd.DataFrame) -> None:
    """Raise ValueError if a bar DataFrame is missing canonical columns."""

    missing = [column for column in BAR_DATAFRAME_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Bar DataFrame is missing required columns: {missing}")


def extract_canonical_metrics(stats_df: pd.DataFrame) -> dict[str, float]:
    """Extract canonical metric keys from a BacktestRunner stats DataFrame."""

    if stats_df.empty:
        raise ValueError("stats_df must contain at least one row")

    row = stats_df.iloc[0]
    metrics: dict[str, float] = {}

    missing_columns = [column for column in BACKTEST_STATS_COLUMN_TO_METRIC if column not in row.index]
    if missing_columns:
        raise ValueError(f"Stats DataFrame missing canonical metric columns: {missing_columns}")

    for source_column, metric_key in BACKTEST_STATS_COLUMN_TO_METRIC.items():
        value: Any = row[source_column]
        metrics[metric_key] = float(value)
    return metrics
