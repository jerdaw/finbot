"""Integration tests for cost tracking in backtests."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts import BacktestRunRequest, CostType
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.costs import FixedSlippage, FixedSpread, FlatCommission, ZeroCommission
from finbot.utils.pandas_utils.load_dataframe import load_dataframe


@pytest.fixture
def price_histories():
    """Load SPY price history for testing."""
    spy_df = load_dataframe("finbot/data/yfinance_data/history/SPY_history_1d.parquet")
    return {"SPY": spy_df}


def test_zero_cost_models_produce_zero_costs(price_histories):
    """Test that zero-cost models produce zero total costs."""
    adapter = BacktraderAdapter(
        price_histories=price_histories,
        commission_model=ZeroCommission(),
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2021-01-01"),
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    assert result.costs is not None, "Costs should be tracked"
    assert result.costs.total_costs == 0.0, "Zero cost models should produce zero total costs"
    assert result.costs.total_commission == 0.0
    assert result.costs.total_spread == 0.0
    assert result.costs.total_slippage == 0.0
    assert len(result.costs.cost_events) == 0, "Zero cost models should not create cost events"


def test_flat_commission_tracking(price_histories):
    """Test that flat commission is tracked correctly."""
    adapter = BacktraderAdapter(
        price_histories=price_histories,
        commission_model=FlatCommission(per_share=0.01, min_commission=1.0),
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2021-01-01"),
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    assert result.costs is not None, "Costs should be tracked"
    assert result.costs.total_commission > 0.0, "Commission should be positive with FlatCommission"
    assert result.costs.total_spread == 0.0, "Spread should be zero with default ZeroSpread"
    assert result.costs.total_slippage == 0.0, "Slippage should be zero with default ZeroSlippage"

    # Check that commission events were recorded
    commission_events = [e for e in result.costs.cost_events if e.cost_type == CostType.COMMISSION]
    assert len(commission_events) > 0, "Commission events should be recorded"
    assert all(e.amount > 0 for e in commission_events), "All commission amounts should be positive"


def test_multiple_cost_types(price_histories):
    """Test tracking multiple cost types simultaneously."""
    adapter = BacktraderAdapter(
        price_histories=price_histories,
        commission_model=FlatCommission(per_share=0.01),
        spread_model=FixedSpread(bps=5),  # 5 bps spread
        slippage_model=FixedSlippage(bps=3),  # 3 bps slippage
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2021-01-01"),
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    assert result.costs is not None, "Costs should be tracked"
    assert result.costs.total_commission > 0.0, "Commission should be positive"
    assert result.costs.total_spread > 0.0, "Spread should be positive"
    assert result.costs.total_slippage > 0.0, "Slippage should be positive"

    # Verify all cost types are present
    cost_types = {e.cost_type for e in result.costs.cost_events}
    assert CostType.COMMISSION in cost_types
    assert CostType.SPREAD in cost_types
    assert CostType.SLIPPAGE in cost_types

    # Total costs should be sum of all components
    expected_total = (
        result.costs.total_commission
        + result.costs.total_spread
        + result.costs.total_slippage
        + result.costs.total_borrow
        + result.costs.total_market_impact
    )
    assert result.costs.total_costs == expected_total


def test_cost_assumptions_recorded(price_histories):
    """Test that cost model assumptions are recorded in result."""
    adapter = BacktraderAdapter(
        price_histories=price_histories,
        commission_model=FlatCommission(per_share=0.005, min_commission=2.0),
        spread_model=FixedSpread(bps=8),
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2021-01-01"),
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    # Cost model names should be in assumptions
    assert "commission_model" in result.assumptions
    assert "spread_model" in result.assumptions
    assert "slippage_model" in result.assumptions

    # Check that model names match
    assert "FlatCommission" in result.assumptions["commission_model"]
    assert "FixedSpread" in result.assumptions["spread_model"]
    assert "ZeroSlippage" in result.assumptions["slippage_model"]


def test_cost_serialization(price_histories):
    """Test that costs can be serialized and deserialized."""
    from finbot.core.contracts.serialization import backtest_result_from_payload, backtest_result_to_payload

    adapter = BacktraderAdapter(
        price_histories=price_histories,
        commission_model=FlatCommission(per_share=0.01),
        spread_model=FixedSpread(bps=5),
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2021-01-01"),
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)
    original_costs = result.costs

    # Serialize and deserialize
    payload = backtest_result_to_payload(result)
    deserialized = backtest_result_from_payload(payload)

    # Verify costs are preserved
    assert deserialized.costs is not None
    assert deserialized.costs.total_commission == original_costs.total_commission
    assert deserialized.costs.total_spread == original_costs.total_spread
    assert deserialized.costs.total_slippage == original_costs.total_slippage
    assert len(deserialized.costs.cost_events) == len(original_costs.cost_events)
