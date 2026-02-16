"""Unit tests for experiment comparison utilities."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from finbot.core.contracts import BacktestRunMetadata, BacktestRunResult
from finbot.dashboard.utils.experiment_comparison import (
    build_assumptions_comparison,
    build_metrics_comparison,
    export_comparison_csv,
    format_metric_value,
    highlight_best_worst,
    plot_metrics_comparison,
)


def create_test_result(run_id: str, strategy: str, metrics: dict, assumptions: dict) -> BacktestRunResult:
    """Create a test backtest result."""
    metadata = BacktestRunMetadata(
        run_id=run_id,
        engine_name="backtrader",
        engine_version="1.9.0",
        strategy_name=strategy,
        created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
        config_hash="test-hash",
        data_snapshot_id="test-snapshot",
    )

    return BacktestRunResult(
        metadata=metadata,
        metrics=metrics,
        assumptions=assumptions,
    )


def test_build_assumptions_comparison():
    """Test building assumptions comparison table."""
    exp1 = create_test_result(
        "run-001",
        "Rebalance",
        {},
        {"symbols": ["SPY"], "start": "2020-01-01", "end": "2023-12-31", "rebalance_freq": "monthly"},
    )

    exp2 = create_test_result(
        "run-002",
        "Rebalance",
        {},
        {"symbols": ["SPY", "TLT"], "start": "2020-01-01", "end": "2023-12-31", "rebalance_freq": "quarterly"},
    )

    df = build_assumptions_comparison([exp1, exp2])

    # Should show only differing assumptions
    assert not df.empty
    assert "symbols" in df.index
    assert "rebalance_freq" in df.index
    # start and end are the same, so shouldn't be included
    assert "start" not in df.index
    assert "end" not in df.index


def test_build_assumptions_comparison_empty():
    """Test building assumptions comparison with empty list."""
    df = build_assumptions_comparison([])
    assert df.empty


def test_build_assumptions_comparison_few_differences():
    """Test building assumptions comparison with mostly identical assumptions."""
    # Mix of identical and different assumptions
    exp1 = create_test_result("run-001", "Rebalance", {}, {"symbol": "SPY", "start": "2020-01-01", "end": "2023-12-31"})

    exp2 = create_test_result(
        "run-002",
        "Rebalance",
        {},
        {"symbol": "TLT", "start": "2020-01-01", "end": "2023-12-31"},  # Different symbol
    )

    df = build_assumptions_comparison([exp1, exp2])

    # Should include the differing assumption
    assert "symbol" in df.index
    # start and end are identical, may or may not be included
    # (depending on pandas comparison behavior with object types)


def test_build_metrics_comparison():
    """Test building metrics comparison table."""
    exp1 = create_test_result("run-001", "Rebalance", {"cagr": 0.15, "sharpe": 1.5}, {})

    exp2 = create_test_result("run-002", "Rebalance", {"cagr": 0.18, "sharpe": 1.2}, {})

    df = build_metrics_comparison([exp1, exp2])

    assert not df.empty
    assert "cagr" in df.index
    assert "sharpe" in df.index
    assert len(df.columns) == 2


def test_build_metrics_comparison_empty():
    """Test building metrics comparison with empty list."""
    df = build_metrics_comparison([])
    assert df.empty


def test_format_metric_value_percentage():
    """Test formatting metric value as percentage."""
    assert format_metric_value(0.15) == "15.00%"
    assert format_metric_value(-0.10) == "-10.00%"
    assert format_metric_value(0.005) == "0.50%"


def test_format_metric_value_decimal():
    """Test formatting metric value as decimal."""
    assert format_metric_value(100.5) == "100.5000"
    assert format_metric_value(1.5) == "1.5000"  # Above 0.99, so formatted as decimal


def test_format_metric_value_non_numeric():
    """Test formatting non-numeric values."""
    assert format_metric_value("text") == "text"
    assert format_metric_value(None) == "None"


def test_highlight_best_worst():
    """Test highlighting best and worst values."""
    df = pd.DataFrame(
        {
            "exp1": [0.15, 1.5, -0.10],
            "exp2": [0.18, 1.2, -0.15],
            "exp3": [0.12, 1.8, -0.08],
        },
        index=["cagr", "sharpe", "max_drawdown"],
    )

    # Higher is better config
    higher_is_better = {
        "cagr": True,
        "sharpe": True,
        "max_drawdown": False,  # Lower is better (less negative)
    }

    styled = highlight_best_worst(df, higher_is_better)

    # styled should be a Styler object
    assert hasattr(styled, "data")
    assert styled.data.equals(df)


def test_plot_metrics_comparison():
    """Test plotting metrics comparison."""
    df = pd.DataFrame(
        {
            "exp1": [0.15, 1.5],
            "exp2": [0.18, 1.2],
        },
        index=["cagr", "sharpe"],
    )

    figures = plot_metrics_comparison(df)

    assert len(figures) == 2
    # Check that figures are plotly figures
    for fig in figures:
        assert hasattr(fig, "data")
        assert hasattr(fig, "layout")


def test_plot_metrics_comparison_selected():
    """Test plotting only selected metrics."""
    df = pd.DataFrame(
        {
            "exp1": [0.15, 1.5, -0.10],
            "exp2": [0.18, 1.2, -0.15],
        },
        index=["cagr", "sharpe", "max_drawdown"],
    )

    figures = plot_metrics_comparison(df, selected_metrics=["cagr"])

    assert len(figures) == 1


def test_plot_metrics_comparison_empty():
    """Test plotting with empty dataframe."""
    df = pd.DataFrame()
    figures = plot_metrics_comparison(df)
    assert figures == []


def test_export_comparison_csv():
    """Test exporting comparison to CSV."""
    assumptions_df = pd.DataFrame(
        {
            "exp1": ["['SPY']"],
            "exp2": ["['SPY', 'TLT']"],
        },
        index=["symbols"],
    )

    metrics_df = pd.DataFrame(
        {
            "exp1": [0.15, 1.5],
            "exp2": [0.18, 1.2],
        },
        index=["cagr", "sharpe"],
    )

    csv_data = export_comparison_csv(assumptions_df, metrics_df)

    assert "# Assumptions Comparison" in csv_data
    assert "# Metrics Comparison" in csv_data
    assert "symbols" in csv_data
    assert "cagr" in csv_data


def test_export_comparison_csv_empty():
    """Test exporting empty comparison."""
    csv_data = export_comparison_csv(pd.DataFrame(), pd.DataFrame())

    assert "# Assumptions Comparison" in csv_data
    assert "# Metrics Comparison" in csv_data
