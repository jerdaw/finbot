"""Serialization helpers for converting pandas/numpy objects to JSON-safe dicts."""

from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd


def _sanitize_float(v: float) -> float | None:
    """Sanitize a float, returning None for NaN/Inf."""
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def sanitize_value(v: Any) -> Any:
    """Convert a single value to a JSON-safe type."""
    if v is None:
        return None
    if isinstance(v, float):
        return _sanitize_float(v)
    if isinstance(v, np.floating):
        return _sanitize_float(float(v))
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, pd.Timestamp | datetime | date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, np.ndarray):
        return [sanitize_value(x) for x in v.tolist()]
    return v


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame to a list of JSON-safe dicts, one per row."""
    if df is None or df.empty:
        return []

    records = []
    for idx, row in df.iterrows():
        record: dict[str, Any] = {}
        if isinstance(idx, pd.Timestamp | datetime):
            record["date"] = idx.isoformat()
        elif isinstance(idx, str):
            record["index"] = idx
        else:
            record["index"] = sanitize_value(idx)

        for col in df.columns:
            record[str(col)] = sanitize_value(row[col])
        records.append(record)
    return records


def series_to_timeseries(series: pd.Series, name: str | None = None) -> dict[str, Any]:
    """Convert a pandas Series to a TimeSeries dict with dates and values."""
    if series is None or series.empty:
        return {"name": name or "", "dates": [], "values": []}

    dates = []
    values = []
    for idx, val in series.items():
        if isinstance(idx, pd.Timestamp | datetime):
            dates.append(idx.isoformat())
        else:
            dates.append(str(idx))
        values.append(sanitize_value(val))

    return {"name": name or str(series.name) or "", "dates": dates, "values": values}


def stats_df_to_dict(stats_df: pd.DataFrame) -> dict[str, Any]:
    """Convert a single-row statistics DataFrame to a flat dict."""
    if stats_df is None or stats_df.empty:
        return {}
    row = stats_df.iloc[0]
    return {str(col): sanitize_value(row[col]) for col in stats_df.columns}
