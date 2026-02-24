"""Unit tests for custom Backtrader indicators and analyzers."""

from __future__ import annotations

import pytest


class TestReturnsIndicator:
    """Tests for Returns indicator."""

    def test_import(self):
        from finbot.services.backtesting.indicators.returns import Returns

        assert Returns is not None

    def test_has_lines_and_params(self):
        from finbot.services.backtesting.indicators.returns import Returns

        assert hasattr(Returns, "lines")
        assert hasattr(Returns, "params")

    def test_plotlabel_returns_period(self):
        from finbot.services.backtesting.indicators.returns import Returns

        # Verify _plotlabel method exists
        assert hasattr(Returns, "_plotlabel")


class TestPositiveReturnsIndicator:
    """Tests for PositiveReturns indicator."""

    def test_import(self):
        from finbot.services.backtesting.indicators.positive_returns import (
            PositiveReturns,
        )

        assert PositiveReturns is not None

    def test_has_lines_and_params(self):
        from finbot.services.backtesting.indicators.positive_returns import (
            PositiveReturns,
        )

        assert hasattr(PositiveReturns, "lines")
        assert hasattr(PositiveReturns, "params")


class TestNegativeReturnsIndicator:
    """Tests for NegativeReturns indicator."""

    def test_import(self):
        from finbot.services.backtesting.indicators.negative_returns import (
            NegativeReturns,
        )

        assert NegativeReturns is not None

    def test_has_lines_and_params(self):
        from finbot.services.backtesting.indicators.negative_returns import (
            NegativeReturns,
        )

        assert hasattr(NegativeReturns, "lines")
        assert hasattr(NegativeReturns, "params")


class TestCVTracker:
    """Tests for CVTracker analyzer."""

    def test_import(self):
        from finbot.services.backtesting.analyzers.cv_tracker import CVTracker

        assert CVTracker is not None


class TestTradeTracker:
    """Tests for TradeTracker analyzer."""

    def test_import(self):
        from finbot.services.backtesting.analyzers.trade_tracker import TradeTracker

        assert TradeTracker is not None

    def test_trade_info_dataclass(self):
        import pandas as pd

        from finbot.services.backtesting.analyzers.trade_tracker import TradeInfo

        info = TradeInfo(
            timestamp=pd.Timestamp("2021-01-01"),
            symbol="SPY",
            size=100.0,
            price=400.0,
            value=40000.0,
            commission=1.0,
        )
        assert info.symbol == "SPY"
        assert info.size == 100.0

    def test_trade_info_is_frozen(self):
        import pandas as pd

        from finbot.services.backtesting.analyzers.trade_tracker import TradeInfo

        info = TradeInfo(
            timestamp=pd.Timestamp("2021-01-01"),
            symbol="SPY",
            size=100.0,
            price=400.0,
            value=40000.0,
            commission=1.0,
        )
        with pytest.raises(AttributeError):
            info.symbol = "QQQ"  # type: ignore[misc]
