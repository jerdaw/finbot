"""Integration-style CLI execution path tests with mocked data/providers.

These tests exercise command handlers through the real Click CLI while replacing
network/data-heavy dependencies with deterministic fixtures.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from click.testing import CliRunner

from finbot.cli.main import cli


@dataclass
class _FakeSource:
    name: str
    max_age_days: int


@dataclass
class _FakeFreshness:
    source: _FakeSource
    file_count: int
    size_str: str
    newest_file: datetime | None
    age_str: str
    is_stale: bool
    total_size_bytes: int


def _price_df() -> pd.DataFrame:
    index = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    return pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=index)


def test_simulate_command_executes_with_mocked_fund(monkeypatch):
    runner = CliRunner()

    from finbot.services.simulation import sim_specific_funds

    monkeypatch.setattr(sim_specific_funds, "sim_spy", _price_df)

    result = runner.invoke(cli, ["--trace-id", "it-sim-001", "simulate", "--fund", "SPY"])

    assert result.exit_code == 0
    assert "Simulation Results for SPY" in result.output
    assert "Data points: 3" in result.output


def test_backtest_command_executes_with_mocked_runner(monkeypatch):
    runner = CliRunner()

    def _fake_get_history(*_args, **_kwargs):
        return _price_df()

    class _FakeRunner:
        def __init__(self, **_kwargs):
            pass

        def run_backtest(self):
            return pd.DataFrame(
                {
                    "Starting Value": [100000.0],
                    "Ending Value": [110000.0],
                    "ROI": [0.1],
                    "CAGR": [0.05],
                    "Sharpe": [1.2],
                    "Calmar": [0.7],
                    "Max Drawdown": [-0.1],
                    "Annualized Volatility": [0.15],
                    "Win Days %": [0.55],
                }
            )

    get_history_module = importlib.import_module("finbot.utils.data_collection_utils.yfinance.get_history")
    monkeypatch.setattr(get_history_module, "get_history", _fake_get_history)
    monkeypatch.setattr(
        "finbot.services.backtesting.backtest_runner.BacktestRunner",
        _FakeRunner,
    )

    result = runner.invoke(
        cli,
        [
            "--trace-id",
            "it-backtest-001",
            "backtest",
            "--strategy",
            "NoRebalance",
            "--asset",
            "SPY",
        ],
    )

    assert result.exit_code == 0
    assert "Backtest Results" in result.output
    assert "Total return: +10.00%" in result.output


def test_optimize_command_executes_with_mocked_optimizer(monkeypatch):
    runner = CliRunner()

    def _fake_get_history(*_args, **_kwargs):
        return _price_df()

    def _fake_dca_optimizer(*_args, **_kwargs):
        return pd.DataFrame(
            {
                "ratio": [1.0, 2.0],
                "sharpe": [0.5, 0.6],
            }
        )

    def _fake_analyze_results_helper(*_args, **_kwargs):
        ratio_df = pd.DataFrame([[0.7, 8.0, 0.0, -12.0]], index=[2.0])
        duration_df = pd.DataFrame([[0.6, 7.5, 0.0, -13.5]], index=[63])
        return ratio_df, duration_df

    get_history_module = importlib.import_module("finbot.utils.data_collection_utils.yfinance.get_history")
    monkeypatch.setattr(get_history_module, "get_history", _fake_get_history)
    monkeypatch.setattr(
        "finbot.services.optimization.dca_optimizer.dca_optimizer",
        _fake_dca_optimizer,
    )
    monkeypatch.setattr(
        "finbot.services.optimization.dca_optimizer.analyze_results_helper",
        _fake_analyze_results_helper,
    )

    result = runner.invoke(
        cli,
        [
            "--trace-id",
            "it-opt-001",
            "optimize",
            "--method",
            "dca",
            "--asset",
            "SPY",
            "--cash",
            "1000",
        ],
    )

    assert result.exit_code == 0
    assert "Optimization Results by DCA Ratio" in result.output
    assert "Optimization Results by DCA Duration" in result.output


def test_status_command_executes_with_mocked_freshness(monkeypatch):
    runner = CliRunner()

    fake_statuses = [
        _FakeFreshness(
            source=_FakeSource(name="yfinance", max_age_days=1),
            file_count=12,
            size_str="1.2 MB",
            newest_file=datetime(2026, 2, 19, 10, 30),
            age_str="0 days",
            is_stale=False,
            total_size_bytes=1_200_000,
        )
    ]

    monkeypatch.setattr(
        "finbot.services.data_quality.check_data_freshness.check_all_freshness",
        lambda: fake_statuses,
    )

    result = runner.invoke(cli, ["--trace-id", "it-status-001", "status"])

    assert result.exit_code == 0
    assert "Data Source Status" in result.output
    assert "All data sources are fresh." in result.output
