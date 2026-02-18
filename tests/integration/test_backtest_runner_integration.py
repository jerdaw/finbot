"""Integration tests for backtest runner workflows.

Tests end-to-end backtesting including strategy execution, analysis,
and results generation.
"""

from __future__ import annotations

import backtrader as bt
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance

from ..integration.conftest import assert_valid_backtest_stats


class TestBacktestRunnerIntegration:
    """Integration tests for complete backtesting workflows."""

    def test_simple_backtest_single_asset(self, sample_spy_data):
        """Test basic backtest with single asset and NoRebalance strategy."""
        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},  # 100% in single asset
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        stats = runner.run_backtest()

        # Validate results
        assert_valid_backtest_stats(stats)

        # Check that we have value history
        value_history = runner.get_value_history()
        assert isinstance(value_history, pd.DataFrame)
        assert "Value" in value_history.columns
        assert "Cash" in value_history.columns
        assert len(value_history) > 0

    def test_backtest_multi_asset_rebalance(self, sample_multi_asset_data):
        """Test backtest with multi-asset portfolio and rebalancing."""
        runner = BacktestRunner(
            price_histories=sample_multi_asset_data,
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=Rebalance,
            strat_kwargs={
                "rebal_proportions": (0.6, 0.4),  # 60/40 portfolio
                "rebal_interval": 21,  # Monthly rebalance
            },
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        stats = runner.run_backtest()

        # Validate results
        assert_valid_backtest_stats(stats)

        # Check trades occurred (rebalancing)
        trades = runner.get_trades()
        assert len(trades) > 0, "Rebalancing strategy should generate trades"

    def test_backtest_with_date_range(self, sample_spy_data):
        """Test backtest with specific date range."""
        # Use only first half of data
        start_date = sample_spy_data.index[0]
        end_date = sample_spy_data.index[len(sample_spy_data) // 2]

        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=start_date,
            end=end_date,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        runner.run_backtest()
        value_history = runner.get_value_history()

        # Should have roughly half the data points
        assert len(value_history) < len(sample_spy_data)
        assert len(value_history) > len(sample_spy_data) // 2 - 10  # Some tolerance

    def test_backtest_with_duration(self, sample_spy_data):
        """Test backtest with duration parameter."""
        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=sample_spy_data.index[0],
            end=None,
            duration=pd.Timedelta(days=90),  # ~3 months
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        runner.run_backtest()
        value_history = runner.get_value_history()

        # Should have ~60 trading days (90 calendar days)
        assert 40 < len(value_history) < 80, f"Expected ~60 days, got {len(value_history)}"

    def test_backtest_initial_cash_levels(self, sample_spy_data):
        """Test backtest with different initial cash levels."""
        cash_levels = [10000, 100000, 1000000]
        results = {}

        for cash in cash_levels:
            runner = BacktestRunner(
                price_histories={"SPY": sample_spy_data},
                start=None,
                end=None,
                duration=None,
                start_step=None,
                init_cash=cash,
                strat=NoRebalance,
                strat_kwargs={"equity_proportions": (1.0,)},
                broker=bt.brokers.BackBroker,
                broker_kwargs={},
                broker_commission=FixedCommissionScheme,
                sizer=bt.sizers.AllInSizer,
                sizer_kwargs={},
                plot=False,
            )

            stats = runner.run_backtest()
            results[cash] = stats

        # Returns should be similar regardless of initial cash (access CAGR column)
        returns = [results[c]["CAGR"].iloc[0] for c in cash_levels]

        # All returns should be within 0.02 of each other (allowing for commission impact)
        assert max(returns) - min(returns) < 0.02, "Returns should be similar across cash levels"

    def test_backtest_trade_tracking(self, sample_multi_asset_data):
        """Test that trades are properly tracked."""
        runner = BacktestRunner(
            price_histories=sample_multi_asset_data,
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=Rebalance,
            strat_kwargs={
                "rebal_proportions": (0.6, 0.4),
                "rebal_interval": 21,
            },
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        runner.run_backtest()
        trades = runner.get_trades()

        # Should have trades from rebalancing
        assert len(trades) > 0

        # Trades should have expected attributes
        if len(trades) > 0:
            trade = trades[0]
            assert hasattr(trade, "size") or hasattr(trade, "quantity")
            # Note: Trade structure depends on TradeTracker implementation

    def test_backtest_value_history_continuity(self, sample_spy_data):
        """Test that value history is continuous (no gaps)."""
        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        runner.run_backtest()
        value_history = runner.get_value_history()

        # Check no NaN values
        assert not value_history["Value"].isna().any(), "Value should have no NaN"
        assert not value_history["Cash"].isna().any(), "Cash should have no NaN"

        # Value + Cash should equal total portfolio value
        # (In NoRebalance, Cash should be 0 after initial purchase)

    def test_backtest_stats_completeness(self, sample_spy_data):
        """Test that all expected statistics are generated."""
        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        stats = runner.run_backtest()

        # Check for comprehensive metrics (stats are columns)
        expected_metrics = [
            "ROI",
            "CAGR",
            "Sharpe",
            "Calmar",
            "Max Drawdown",
            "Annualized Volatility",
        ]

        for metric in expected_metrics:
            assert metric in stats.columns, f"Missing metric: {metric}"


@pytest.mark.slow
class TestBacktestRunnerPerformance:
    """Performance tests for backtest runner (marked as slow)."""

    def test_backtest_performance_single_asset(self, sample_spy_data):
        """Test backtest performance with single asset."""
        import time

        start = time.time()

        runner = BacktestRunner(
            price_histories={"SPY": sample_spy_data},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": (1.0,)},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )

        runner.run_backtest()
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 3.0, f"Backtest took {duration:.2f}s, expected <3s"
