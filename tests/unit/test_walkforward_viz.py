"""Tests for walk-forward visualization module."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import pytest

from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
from finbot.core.contracts.walkforward import WalkForwardConfig, WalkForwardResult, WalkForwardWindow
from finbot.services.backtesting.walkforward_viz import (
    build_summary_dataframe,
    plot_metric_heatmap,
    plot_rolling_metric,
    plot_summary_boxplot,
    plot_train_test_scatter,
    plot_window_timeline,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_metadata(idx: int = 0) -> BacktestRunMetadata:
    from datetime import UTC, datetime
    from uuid import uuid4

    return BacktestRunMetadata(
        run_id=str(uuid4()),
        engine_name="test",
        engine_version="0",
        strategy_name="NoRebalance",
        created_at=datetime.now(UTC),
        config_hash="abc",
        data_snapshot_id=None,
        random_seed=None,
    )


def _make_result(cagr: float = 0.10, sharpe: float = 0.8, idx: int = 0) -> BacktestRunResult:
    from finbot.core.contracts.costs import CostSummary
    from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION

    return BacktestRunResult(
        metadata=_make_metadata(idx),
        metrics={
            "cagr": cagr,
            "sharpe": sharpe,
            "sortino": sharpe * 1.2,
            "max_drawdown": -0.15,
            "volatility": 0.12,
            "roi": cagr * 3,
        },
        schema_version=BACKTEST_RESULT_SCHEMA_VERSION,
        assumptions={},
        artifacts={},
        costs=CostSummary(
            total_commission=0.0,
            total_slippage=0.0,
            total_spread=0.0,
            total_borrow=0.0,
            total_market_impact=0.0,
        ),
    )


def _make_window(i: int, base: pd.Timestamp) -> WalkForwardWindow:
    train_start = base + timedelta(days=i * 100)
    train_end = train_start + timedelta(days=63)
    test_start = train_end + timedelta(days=1)
    test_end = test_start + timedelta(days=20)
    return WalkForwardWindow(
        window_id=i,
        train_start=train_start,
        train_end=train_end,
        test_start=test_start,
        test_end=test_end,
    )


def _make_wf_result(n_windows: int = 4, with_train: bool = False) -> WalkForwardResult:
    base = pd.Timestamp("2018-01-02")
    windows = tuple(_make_window(i, base) for i in range(n_windows))
    test_results = tuple(_make_result(cagr=0.05 + i * 0.02, sharpe=0.5 + i * 0.1, idx=i) for i in range(n_windows))
    train_results = (
        tuple(_make_result(cagr=0.08 + i * 0.02, sharpe=0.7 + i * 0.1, idx=i) for i in range(n_windows))
        if with_train
        else ()
    )

    # Build summary metrics
    cagr_vals = [r.metrics["cagr"] for r in test_results]
    sharpe_vals = [r.metrics["sharpe"] for r in test_results]
    summary: dict[str, float] = {
        "cagr_mean": sum(cagr_vals) / n_windows,
        "cagr_min": min(cagr_vals),
        "cagr_max": max(cagr_vals),
        "cagr_std": 0.02,
        "sharpe_mean": sum(sharpe_vals) / n_windows,
        "sharpe_min": min(sharpe_vals),
        "sharpe_max": max(sharpe_vals),
        "sharpe_std": 0.1,
        "window_count": float(n_windows),
    }

    return WalkForwardResult(
        config=WalkForwardConfig(train_window=63, test_window=21, step_size=21),
        windows=windows,
        test_results=test_results,
        train_results=train_results,
        summary_metrics=summary,
    )


# ── plot_rolling_metric ───────────────────────────────────────────────────────


def test_plot_rolling_metric_returns_figure():
    result = _make_wf_result()
    fig = plot_rolling_metric(result)
    assert isinstance(fig, go.Figure)


def test_plot_rolling_metric_has_correct_trace_count_without_train():
    result = _make_wf_result()
    fig = plot_rolling_metric(result, include_train=False)
    # Test trace + horizontal mean line (added via add_hline — stored in layout.shapes)
    assert len(fig.data) == 1


def test_plot_rolling_metric_with_train_adds_trace():
    result = _make_wf_result(with_train=True)
    fig = plot_rolling_metric(result, include_train=True)
    assert len(fig.data) == 2


def test_plot_rolling_metric_missing_metric_raises():
    result = _make_wf_result()
    with pytest.raises(KeyError, match="nonexistent_metric"):
        plot_rolling_metric(result, metric="nonexistent_metric")


def test_plot_rolling_metric_custom_title():
    result = _make_wf_result()
    fig = plot_rolling_metric(result, title="My Custom Title")
    assert "My Custom Title" in fig.layout.title.text


def test_plot_rolling_metric_sharpe():
    result = _make_wf_result()
    fig = plot_rolling_metric(result, metric="sharpe")
    assert isinstance(fig, go.Figure)


# ── plot_metric_heatmap ───────────────────────────────────────────────────────


def test_plot_metric_heatmap_returns_figure():
    result = _make_wf_result()
    fig = plot_metric_heatmap(result)
    assert isinstance(fig, go.Figure)


def test_plot_metric_heatmap_default_has_five_metrics():
    result = _make_wf_result()
    fig = plot_metric_heatmap(result)
    heatmap = fig.data[0]
    assert isinstance(heatmap, go.Heatmap)
    # Default: ["cagr", "sharpe", "sortino", "max_drawdown", "volatility"]
    assert len(heatmap.y) == 5


def test_plot_metric_heatmap_custom_metrics():
    result = _make_wf_result()
    fig = plot_metric_heatmap(result, metrics=["cagr", "sharpe"])
    heatmap = fig.data[0]
    assert len(heatmap.y) == 2


def test_plot_metric_heatmap_correct_window_count():
    result = _make_wf_result(n_windows=6)
    fig = plot_metric_heatmap(result)
    heatmap = fig.data[0]
    # x-axis = window IDs
    assert len(heatmap.x) == 6


# ── plot_train_test_scatter ────────────────────────────────────────────────────


def test_plot_train_test_scatter_returns_figure():
    result = _make_wf_result(with_train=True)
    fig = plot_train_test_scatter(result)
    assert isinstance(fig, go.Figure)


def test_plot_train_test_scatter_no_train_raises():
    result = _make_wf_result(with_train=False)
    with pytest.raises(ValueError, match="train_results"):
        plot_train_test_scatter(result)


def test_plot_train_test_scatter_has_diagonal_and_points():
    result = _make_wf_result(with_train=True)
    fig = plot_train_test_scatter(result)
    # Two traces: diagonal reference line + scatter points
    assert len(fig.data) == 2


def test_plot_train_test_scatter_missing_metric_raises():
    result = _make_wf_result(with_train=True)
    with pytest.raises(KeyError):
        plot_train_test_scatter(result, metric="nonexistent")


# ── plot_window_timeline ──────────────────────────────────────────────────────


def test_plot_window_timeline_returns_figure():
    result = _make_wf_result()
    fig = plot_window_timeline(result)
    assert isinstance(fig, go.Figure)


def test_plot_window_timeline_bar_count():
    n = 4
    result = _make_wf_result(n_windows=n)
    fig = plot_window_timeline(result)
    # 2 bars per window (train + test)
    assert len(fig.data) == 2 * n


def test_plot_window_timeline_single_window():
    result = _make_wf_result(n_windows=1)
    fig = plot_window_timeline(result)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2


# ── plot_summary_boxplot ─────────────────────────────────────────────────────


def test_plot_summary_boxplot_returns_figure():
    result = _make_wf_result()
    fig = plot_summary_boxplot(result)
    assert isinstance(fig, go.Figure)


def test_plot_summary_boxplot_default_three_metrics():
    result = _make_wf_result()
    fig = plot_summary_boxplot(result)
    assert len(fig.data) == 3  # cagr, sharpe, max_drawdown


def test_plot_summary_boxplot_custom_metrics():
    result = _make_wf_result()
    fig = plot_summary_boxplot(result, metrics=["cagr"])
    assert len(fig.data) == 1


# ── build_summary_dataframe ───────────────────────────────────────────────────


def test_build_summary_dataframe_returns_dataframe():
    result = _make_wf_result()
    df = build_summary_dataframe(result)
    assert isinstance(df, pd.DataFrame)


def test_build_summary_dataframe_has_expected_columns():
    result = _make_wf_result()
    df = build_summary_dataframe(result)
    assert "metric" in df.columns
    for col in ("mean", "min", "max", "std"):
        assert col in df.columns


def test_build_summary_dataframe_window_count():
    n = 5
    result = _make_wf_result(n_windows=n)
    df = build_summary_dataframe(result)
    assert df["window_count"].iloc[0] == n
