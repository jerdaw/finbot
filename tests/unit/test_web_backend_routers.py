"""Tests for web backend API routers.

Uses FastAPI TestClient to validate endpoint registration, request validation,
and error handling without requiring external data or API keys.
"""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from finbot.services.backtesting.experiment_registry import ExperimentRegistry
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry
from web.backend.main import app
from web.backend.routers import backtesting as backtesting_router
from web.backend.routers import experiments as experiments_router

client = TestClient(app)


class TestAppSetup:
    """Test that the FastAPI app is correctly configured."""

    def test_app_has_routes(self):
        routes = [r.path for r in app.routes]
        assert len(routes) > 0

    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "prefix",
        [
            "/api/backtesting",
            "/api/risk-analytics",
            "/api/portfolio-analytics",
            "/api/realtime-quotes",
            "/api/factor-analytics",
        ],
    )
    def test_new_routers_registered(self, prefix):
        """Verify new router prefixes appear in registered routes."""
        routes = [r.path for r in app.routes]
        matching = [r for r in routes if r.startswith(prefix)]
        assert len(matching) > 0, f"No routes found with prefix {prefix}"


class TestRiskAnalyticsRouter:
    """Test risk analytics endpoint validation."""

    def test_var_missing_ticker(self):
        response = client.post("/api/risk-analytics/var", json={})
        assert response.status_code == 422

    def test_var_request_shape(self):
        payload = {
            "ticker": "SPY",
            "confidence_level": 0.95,
            "horizon_days": 1,
            "start_date": "2020-01-01",
            "end_date": "2020-06-01",
        }
        response = client.post("/api/risk-analytics/var", json=payload)
        # May fail due to missing data, but should not be 422 (validation error)
        assert response.status_code != 422

    def test_stress_missing_ticker(self):
        response = client.post("/api/risk-analytics/stress", json={})
        assert response.status_code == 422

    def test_kelly_missing_ticker(self):
        response = client.post("/api/risk-analytics/kelly", json={})
        assert response.status_code == 422


class TestBacktestingRouter:
    """Test backtesting endpoint validation."""

    PERIODS = 320

    @staticmethod
    def _make_price_frame(start_price: float = 100.0) -> pd.DataFrame:
        index = pd.date_range("2020-01-01", periods=TestBacktestingRouter.PERIODS, freq="B")
        closes = [start_price + idx for idx in range(len(index))]
        return pd.DataFrame({"Close": closes}, index=index)

    @staticmethod
    def _make_runner_factory() -> type:
        class FakeRunner:
            def __init__(self, **_: object) -> None:
                self._value_history = pd.DataFrame(
                    {
                        "Value": [10000 + idx * 125 for idx in range(TestBacktestingRouter.PERIODS)],
                    },
                    index=pd.date_range("2020-01-01", periods=TestBacktestingRouter.PERIODS, freq="B"),
                )

            def run_backtest(self) -> pd.DataFrame:
                return pd.DataFrame(
                    {
                        "Starting Value": [10000.0],
                        "Ending Value": [15500.0],
                        "ROI": [0.55],
                        "CAGR": [0.12],
                        "Sharpe": [1.05],
                        "Max Drawdown": [-0.14],
                        "Mean Cash Utilization": [0.97],
                    }
                )

            def get_value_history(self) -> pd.DataFrame:
                return self._value_history

            def get_trades(self) -> list[object]:
                return [
                    SimpleNamespace(
                        timestamp=pd.Timestamp("2020-02-03"),
                        symbol="QQQ",
                        size=10.0,
                        price=150.0,
                        value=1500.0,
                    ),
                    SimpleNamespace(
                        timestamp=pd.Timestamp("2020-04-01"),
                        symbol="QQQ",
                        size=-5.0,
                        price=175.0,
                        value=-875.0,
                    ),
                ]

            def get_cashflow_events(self) -> list[dict[str, object]]:
                return [
                    {
                        "scheduled_date": "2020-02-03",
                        "applied_date": "2020-02-03",
                        "label": "Recurring contribution (monthly)",
                        "source": "recurring",
                        "direction": "contribution",
                        "amount": 250.0,
                        "cash_after": 250.0,
                        "portfolio_value_after": 10250.0,
                    }
                ]

            def get_allocation_history(self) -> list[dict[str, object]]:
                return [
                    {"date": "2020-01-01", "QQQ": 1.0, "Cash": 0.0},
                    {"date": "2020-02-03", "QQQ": 0.97, "Cash": 0.03},
                    {"date": "2020-04-01", "QQQ": 0.95, "Cash": 0.05},
                ]

        return FakeRunner

    def test_strategies_endpoint(self):
        response = client.get("/api/backtesting/strategies")
        assert response.status_code == 200
        data = response.json()
        assert any(strategy["name"] == "NoRebalance" for strategy in data)

    def test_rejects_duplicate_tickers(self):
        payload = {
            "tickers": ["SPY", "SPY"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [0.5, 0.5]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
        }
        response = client.post("/api/backtesting/run", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "Tickers must be unique"

    def test_rejects_unbalanced_allocation_weights(self):
        payload = {
            "tickers": ["SPY", "TLT"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [0.7, 0.2]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
        }
        response = client.post("/api/backtesting/run", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "equity_proportions weights must sum to 1.0"

    def test_backtest_returns_benchmark_stats_when_requested(self, monkeypatch: pytest.MonkeyPatch):
        def fake_get_history(ticker: str) -> pd.DataFrame:
            if ticker == "QQQ":
                return self._make_price_frame(150.0)
            if ticker == "SPY":
                return self._make_price_frame(100.0)
            raise AssertionError(f"Unexpected ticker lookup: {ticker}")

        monkeypatch.setattr(backtesting_router, "get_history", fake_get_history)
        monkeypatch.setattr(backtesting_router, "BacktestRunner", self._make_runner_factory())

        payload = {
            "tickers": ["QQQ"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [1.0]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
            "benchmark_ticker": "SPY",
            "risk_free_rate": 0.04,
        }
        response = client.post("/api/backtesting/run", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["benchmark_stats"]["benchmark_name"] == "SPY"
        assert body["benchmark_stats"]["n_observations"] >= 30
        assert len(body["benchmark_value_history"]) >= 30
        assert body["rolling_metrics"]["window"] == 63
        assert len(body["rolling_metrics"]["dates"]) >= 30
        assert len(body["regime_summary"]) == 4
        assert any(row["count_periods"] >= 1 for row in body["regime_summary"])
        assert len(body["regime_periods"]) >= 1
        assert len(body["cashflow_events"]) == 1
        assert len(body["allocation_history"]) == 3
        assert len(body["rebalance_events"]) >= 1
        assert body["withdrawal_durability"] is not None
        assert len(body["monthly_returns"]) >= 2
        assert len(body["annual_returns"]) >= 1

    def test_rejects_zero_recurring_cashflow(self):
        payload = {
            "tickers": ["QQQ"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [1.0]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
            "recurring_cashflows": [
                {
                    "amount": 0,
                    "frequency": "monthly",
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31",
                }
            ],
        }

        response = client.post("/api/backtesting/run", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Recurring cashflow amounts must be non-zero"

    def test_backtest_fails_when_benchmark_data_cannot_load(self, monkeypatch: pytest.MonkeyPatch):
        def fake_get_history(ticker: str) -> pd.DataFrame:
            if ticker == "QQQ":
                return self._make_price_frame(150.0)
            if ticker == "SPY":
                raise RuntimeError("benchmark missing")
            raise AssertionError(f"Unexpected ticker lookup: {ticker}")

        monkeypatch.setattr(backtesting_router, "get_history", fake_get_history)
        monkeypatch.setattr(backtesting_router, "BacktestRunner", self._make_runner_factory())

        payload = {
            "tickers": ["QQQ"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [1.0]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
            "benchmark_ticker": "SPY",
        }
        response = client.post("/api/backtesting/run", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to load price data for SPY: benchmark missing"


class TestExperimentsSaveRouter:
    """Test saving experiment runs from the web backtesting surface."""

    @staticmethod
    def _make_stats_payload() -> dict[str, float]:
        return {
            "Starting Value": 10000.0,
            "Ending Value": 15500.0,
            "ROI": 0.55,
            "CAGR": 0.12,
            "Sharpe": 1.05,
            "Max Drawdown": -0.14,
            "Mean Cash Utilization": 0.97,
        }

    @staticmethod
    def _make_history(start_price: float) -> pd.DataFrame:
        index = pd.date_range("2020-01-01", periods=45, freq="B")
        closes = [start_price + idx for idx in range(len(index))]
        return pd.DataFrame(
            {
                "Open": closes,
                "High": [value + 1 for value in closes],
                "Low": [value - 1 for value in closes],
                "Close": closes,
                "Volume": [1_000_000 for _ in closes],
            },
            index=index,
        )

    def test_save_experiment_persists_snapshot_lineage(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path,
    ):
        monkeypatch.setattr(
            experiments_router,
            "_get_registry",
            lambda: ExperimentRegistry(tmp_path / "experiments"),
        )
        monkeypatch.setattr(
            experiments_router,
            "_get_snapshot_registry",
            lambda: DataSnapshotRegistry(tmp_path / "snapshots"),
        )

        def fake_get_history(ticker: str) -> pd.DataFrame:
            histories = {
                "QQQ": self._make_history(150.0),
                "SPY": self._make_history(100.0),
            }
            return histories[ticker]

        monkeypatch.setattr(experiments_router, "get_history", fake_get_history)

        payload = {
            "tickers": ["QQQ"],
            "strategy": "NoRebalance",
            "strategy_params": {"equity_proportions": [1.0]},
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_cash": 10000,
            "benchmark_ticker": "SPY",
            "risk_free_rate": 0.04,
            "stats": self._make_stats_payload(),
        }
        response = client.post("/api/experiments/save", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["run_id"].startswith("bt-")
        assert body["strategy_name"] == "NoRebalance"
        assert body["data_snapshot_id"].startswith("snap-")

        list_response = client.get("/api/experiments/list")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert len(listed) == 1
        assert listed[0]["data_snapshot_id"] == body["data_snapshot_id"]


class TestPortfolioAnalyticsRouter:
    """Test portfolio analytics endpoint validation."""

    def test_rolling_missing_ticker(self):
        response = client.post("/api/portfolio-analytics/rolling", json={})
        assert response.status_code == 422

    def test_benchmark_missing_fields(self):
        response = client.post("/api/portfolio-analytics/benchmark", json={})
        assert response.status_code == 422

    def test_drawdown_missing_ticker(self):
        response = client.post("/api/portfolio-analytics/drawdown", json={})
        assert response.status_code == 422

    def test_correlation_missing_tickers(self):
        response = client.post("/api/portfolio-analytics/correlation", json={})
        assert response.status_code == 422


class TestRealtimeQuotesRouter:
    """Test realtime quotes endpoint validation."""

    def test_quotes_missing_symbols(self):
        response = client.post("/api/realtime-quotes/quotes", json={})
        assert response.status_code == 422

    def test_provider_status_get(self):
        response = client.get("/api/realtime-quotes/provider-status")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data


class TestFactorAnalyticsRouter:
    """Test factor analytics endpoint validation."""

    def test_regression_missing_fields(self):
        response = client.post("/api/factor-analytics/regression", json={})
        assert response.status_code == 422

    def test_attribution_missing_fields(self):
        response = client.post("/api/factor-analytics/attribution", json={})
        assert response.status_code == 422

    def test_risk_decomposition_missing_fields(self):
        response = client.post("/api/factor-analytics/risk-decomposition", json={})
        assert response.status_code == 422

    def test_rolling_r_squared_missing_fields(self):
        response = client.post("/api/factor-analytics/rolling-r-squared", json={})
        assert response.status_code == 422
