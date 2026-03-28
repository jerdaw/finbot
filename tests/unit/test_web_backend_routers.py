"""Tests for web backend API routers.

Uses FastAPI TestClient to validate endpoint registration, request validation,
and error handling without requiring external data or API keys.
"""

import pytest
from fastapi.testclient import TestClient

from web.backend.main import app

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
