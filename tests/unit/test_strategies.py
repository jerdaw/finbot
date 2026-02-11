"""Unit tests for backtesting strategies."""

from __future__ import annotations

import backtrader as bt
import pandas as pd
import pytest


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing strategies."""
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    data = pd.DataFrame(
        {
            "Open": range(100, 200),
            "High": range(101, 201),
            "Low": range(99, 199),
            "Close": range(100, 200),
            "Volume": [1000000] * 100,
        },
        index=dates,
    )
    return data


class TestRebalanceStrategy:
    """Tests for the Rebalance strategy."""

    def test_rebalance_strategy_import(self):
        """Test that Rebalance strategy can be imported."""
        from finbot.services.backtesting.strategies.rebalance import Rebalance

        assert Rebalance is not None
        assert issubclass(Rebalance, bt.Strategy)

    def test_rebalance_strategy_has_params(self):
        """Test that Rebalance strategy has params attribute."""
        from finbot.services.backtesting.strategies.rebalance import Rebalance

        # Check that params attribute exists
        assert hasattr(Rebalance, "params")


class TestNoRebalanceStrategy:
    """Tests for the NoRebalance strategy."""

    def test_no_rebalance_strategy_import(self):
        """Test that NoRebalance strategy can be imported."""
        from finbot.services.backtesting.strategies.no_rebalance import NoRebalance

        assert NoRebalance is not None
        assert issubclass(NoRebalance, bt.Strategy)

    def test_no_rebalance_strategy_has_params(self):
        """Test that NoRebalance strategy has params attribute."""
        from finbot.services.backtesting.strategies.no_rebalance import NoRebalance

        # Check that params attribute exists
        assert hasattr(NoRebalance, "params")


class TestSMACrossoverStrategy:
    """Tests for the SMA Crossover strategy."""

    def test_sma_crossover_import(self):
        """Test that SMACrossover strategy can be imported."""
        from finbot.services.backtesting.strategies.sma_crossover import SMACrossover

        assert SMACrossover is not None
        assert issubclass(SMACrossover, bt.Strategy)

    def test_sma_crossover_has_params(self):
        """Test that SMACrossover strategy has params attribute."""
        from finbot.services.backtesting.strategies.sma_crossover import SMACrossover

        # Check that params attribute exists
        assert hasattr(SMACrossover, "params")


class TestMACDStrategy:
    """Tests for the MACD strategy."""

    def test_macd_single_import(self):
        """Test that MACDSingle strategy can be imported."""
        from finbot.services.backtesting.strategies.macd_single import MACDSingle

        assert MACDSingle is not None
        assert issubclass(MACDSingle, bt.Strategy)

    def test_macd_dual_import(self):
        """Test that MACDDual strategy can be imported."""
        from finbot.services.backtesting.strategies.macd_dual import MACDDual

        assert MACDDual is not None
        assert issubclass(MACDDual, bt.Strategy)


class TestDipBuyStrategies:
    """Tests for dip buying strategies."""

    def test_dip_buy_sma_import(self):
        """Test that DipBuySMA strategy can be imported."""
        from finbot.services.backtesting.strategies.dip_buy_sma import DipBuySMA

        assert DipBuySMA is not None
        assert issubclass(DipBuySMA, bt.Strategy)

    def test_dip_buy_stdev_import(self):
        """Test that DipBuyStdev strategy can be imported."""
        from finbot.services.backtesting.strategies.dip_buy_stdev import DipBuyStdev

        assert DipBuyStdev is not None
        assert issubclass(DipBuyStdev, bt.Strategy)


class TestStrategyAnalyzers:
    """Tests for strategy analyzers."""

    def test_cv_tracker_import(self):
        """Test that CVTracker analyzer can be imported."""
        from finbot.services.backtesting.analyzers.cv_tracker import CVTracker

        assert CVTracker is not None
        assert issubclass(CVTracker, bt.Analyzer)


class TestStrategySizers:
    """Tests for position sizers."""

    def test_sizers_module_exists(self):
        """Test that sizers module can be imported."""
        from finbot.services.backtesting import sizers

        assert sizers is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
