"""Unit tests for dashboard chart components."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from finbot.dashboard.components.charts import (
    create_bar_chart,
    create_drawdown_chart,
    create_fan_chart,
    create_heatmap,
    create_histogram_chart,
    create_time_series_chart,
)


def _make_price_series(name: str = "TEST", length: int = 252) -> pd.Series:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2020-01-01", periods=length)
    prices = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, length))
    return pd.Series(prices, index=dates, name=name)


def test_time_series_chart_returns_figure():
    s = _make_price_series()
    fig = create_time_series_chart({"TEST": s}, "Test Chart")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].name == "TEST"


def test_time_series_chart_normalized():
    s = _make_price_series()
    fig = create_time_series_chart({"TEST": s}, "Normalized", normalize=True)
    assert isinstance(fig, go.Figure)
    # First y value should be 1.0 when normalized
    assert abs(fig.data[0].y[0] - 1.0) < 1e-10


def test_time_series_chart_multiple_series():
    s1 = _make_price_series("A")
    s2 = _make_price_series("B", length=200)
    fig = create_time_series_chart({"A": s1, "B": s2}, "Multi")
    assert len(fig.data) == 2


def test_histogram_chart():
    s = _make_price_series().pct_change().dropna()
    fig = create_histogram_chart({"Returns": s}, "Returns Dist", bins=30)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_bar_chart():
    df = pd.DataFrame({"Category": ["A", "B", "C"], "Val1": [1, 2, 3], "Val2": [4, 5, 6]})
    fig = create_bar_chart(df, "Category", ["Val1", "Val2"], "Test Bars")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2


def test_heatmap():
    df = pd.DataFrame(
        [[1.0, 2.0], [3.0, 4.0]],
        index=["Row1", "Row2"],
        columns=["Col1", "Col2"],
    )
    fig = create_heatmap(df, "Test Heatmap")
    assert isinstance(fig, go.Figure)


def test_fan_chart():
    rng = np.random.default_rng(42)
    trials = pd.DataFrame(rng.normal(100, 10, (50, 30)))
    fig = create_fan_chart(trials, "Test Fan Chart", max_paths=20)
    assert isinstance(fig, go.Figure)
    # Should have individual paths + 3 percentile lines
    assert len(fig.data) >= 3


def test_drawdown_chart():
    s = _make_price_series()
    fig = create_drawdown_chart(s, "Test Drawdown")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
