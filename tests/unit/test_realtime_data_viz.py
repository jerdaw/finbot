"""Smoke tests for real-time data visualisation functions."""

from __future__ import annotations

from datetime import UTC, datetime

import plotly.graph_objects as go

from finbot.core.contracts.realtime_data import ProviderStatus, Quote, QuoteProvider
from finbot.services.realtime_data.viz import (
    plot_provider_status,
    plot_quote_table,
    plot_sparkline,
)


def _make_quote(symbol: str = "SPY", price: float = 500.0) -> Quote:
    return Quote(
        symbol=symbol,
        price=price,
        timestamp=datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
        provider=QuoteProvider.ALPACA,
        change=1.50,
        change_percent=0.30,
        volume=1_234_567,
    )


def test_plot_quote_table_returns_figure() -> None:
    """plot_quote_table returns a go.Figure."""
    quotes = [_make_quote("SPY"), _make_quote("QQQ", 420.0)]
    fig = plot_quote_table(quotes)
    assert isinstance(fig, go.Figure)


def test_plot_quote_table_empty() -> None:
    """plot_quote_table with empty list returns a figure."""
    fig = plot_quote_table([])
    assert isinstance(fig, go.Figure)


def test_plot_quote_table_negative_change() -> None:
    """plot_quote_table handles negative change values."""
    q = Quote(
        symbol="SPY",
        price=498.0,
        timestamp=datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
        provider=QuoteProvider.ALPACA,
        change=-2.0,
        change_percent=-0.40,
    )
    fig = plot_quote_table([q])
    assert isinstance(fig, go.Figure)


def test_plot_sparkline_returns_figure() -> None:
    """plot_sparkline with prices returns a go.Figure."""
    prices = [100.0, 100.5, 101.0, 100.8, 101.2]
    fig = plot_sparkline(prices, symbol="SPY")
    assert isinstance(fig, go.Figure)


def test_plot_sparkline_empty() -> None:
    """plot_sparkline with empty list returns a figure."""
    fig = plot_sparkline([], symbol="SPY")
    assert isinstance(fig, go.Figure)


def test_plot_sparkline_declining() -> None:
    """plot_sparkline with declining prices uses red."""
    prices = [101.0, 100.5, 100.0, 99.5, 99.0]
    fig = plot_sparkline(prices, symbol="SPY")
    assert isinstance(fig, go.Figure)


def test_plot_provider_status_returns_figure() -> None:
    """plot_provider_status returns a go.Figure."""
    statuses = [
        ProviderStatus(provider=QuoteProvider.ALPACA, is_available=True, total_requests=10, total_errors=1),
        ProviderStatus(provider=QuoteProvider.TWELVEDATA, is_available=False, total_requests=0, total_errors=0),
        ProviderStatus(provider=QuoteProvider.YFINANCE, is_available=True, total_requests=5, total_errors=0),
    ]
    fig = plot_provider_status(statuses)
    assert isinstance(fig, go.Figure)


def test_plot_provider_status_empty() -> None:
    """plot_provider_status with empty list returns a figure."""
    fig = plot_provider_status([])
    assert isinstance(fig, go.Figure)


def test_plot_quote_table_with_none_fields() -> None:
    """plot_quote_table handles quotes with None fields."""
    q = Quote(
        symbol="TEST",
        price=50.0,
        timestamp=datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
        provider=QuoteProvider.YFINANCE,
    )
    fig = plot_quote_table([q])
    assert isinstance(fig, go.Figure)
