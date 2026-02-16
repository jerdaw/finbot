"""Unit tests for cost model implementations."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts.costs import CostEvent, CostSummary, CostType
from finbot.services.backtesting.costs import (
    FixedSlippage,
    FixedSpread,
    FlatCommission,
    PercentageCommission,
    ZeroCommission,
    ZeroSlippage,
    ZeroSpread,
)
from finbot.services.backtesting.costs.slippage import SqrtSlippage


class TestCostContracts:
    """Tests for cost model contracts and data structures."""

    def test_cost_event_creation(self):
        """Test CostEvent dataclass."""
        event = CostEvent(
            timestamp=pd.Timestamp("2024-01-01"),
            symbol="SPY",
            cost_type=CostType.COMMISSION,
            amount=1.50,
            basis="$0.001/share * 1500 shares",
        )

        assert event.timestamp == pd.Timestamp("2024-01-01")
        assert event.symbol == "SPY"
        assert event.cost_type == CostType.COMMISSION
        assert event.amount == 1.50
        assert event.basis == "$0.001/share * 1500 shares"

    def test_cost_summary_totals(self):
        """Test CostSummary aggregation."""
        summary = CostSummary(
            total_commission=10.0,
            total_spread=5.0,
            total_slippage=3.0,
            total_borrow=2.0,
            total_market_impact=1.0,
        )

        assert summary.total_costs == 21.0
        assert summary.total_commission == 10.0
        assert summary.total_spread == 5.0

    def test_cost_summary_by_type(self):
        """Test cost breakdown by type."""
        summary = CostSummary(
            total_commission=10.0,
            total_spread=5.0,
            total_slippage=3.0,
            total_borrow=2.0,
            total_market_impact=1.0,
        )

        by_type = summary.costs_by_type()
        assert by_type[CostType.COMMISSION] == 10.0
        assert by_type[CostType.SPREAD] == 5.0

    def test_cost_summary_by_symbol(self):
        """Test cost breakdown by symbol."""
        events = (
            CostEvent(pd.Timestamp("2024-01-01"), "SPY", CostType.COMMISSION, 5.0, "test"),
            CostEvent(pd.Timestamp("2024-01-01"), "SPY", CostType.SPREAD, 2.0, "test"),
            CostEvent(pd.Timestamp("2024-01-01"), "TLT", CostType.COMMISSION, 3.0, "test"),
        )

        summary = CostSummary(
            total_commission=8.0,
            total_spread=2.0,
            total_slippage=0.0,
            total_borrow=0.0,
            total_market_impact=0.0,
            cost_events=events,
        )

        by_symbol = summary.costs_by_symbol()
        assert by_symbol["SPY"] == 7.0  # 5.0 + 2.0
        assert by_symbol["TLT"] == 3.0


class TestZeroCommission:
    """Tests for ZeroCommission model."""

    def test_zero_cost(self):
        """Test that ZeroCommission always returns zero."""
        model = ZeroCommission()
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.0

    def test_negative_quantity(self):
        """Test with sell order (negative quantity)."""
        model = ZeroCommission()
        cost = model.calculate_cost("SPY", -100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.0

    def test_name(self):
        """Test model name."""
        model = ZeroCommission()
        assert model.get_name() == "ZeroCommission"


class TestFlatCommission:
    """Tests for FlatCommission model."""

    def test_default_rate(self):
        """Test with default $0.001 per share."""
        model = FlatCommission()
        cost = model.calculate_cost("SPY", 1000, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 1.0  # 1000 shares * $0.001

    def test_custom_rate(self):
        """Test with custom per-share rate."""
        model = FlatCommission(per_share=0.005)
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.5  # 100 shares * $0.005

    def test_minimum_commission(self):
        """Test minimum commission enforcement."""
        model = FlatCommission(per_share=0.001, min_commission=1.0)
        cost = model.calculate_cost("SPY", 10, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 1.0  # min_commission applies

    def test_sell_order(self):
        """Test that sell orders (negative quantity) pay same commission."""
        model = FlatCommission(per_share=0.001)
        cost = model.calculate_cost("SPY", -1000, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 1.0  # abs(quantity) used

    def test_negative_per_share_raises(self):
        """Test that negative per_share raises ValueError."""
        with pytest.raises(ValueError, match="per_share must be non-negative"):
            FlatCommission(per_share=-0.001)

    def test_name(self):
        """Test model name."""
        model = FlatCommission(per_share=0.001, min_commission=1.0)
        assert "$0.0010/share" in model.get_name()
        assert "min=$1.00" in model.get_name()


class TestPercentageCommission:
    """Tests for PercentageCommission model."""

    def test_percentage_calculation(self):
        """Test percentage-based commission."""
        model = PercentageCommission(rate=0.001)  # 0.1%
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        # Trade value: 100 * $500 = $50,000
        # Commission: $50,000 * 0.001 = $50
        assert cost == 50.0

    def test_minimum_commission(self):
        """Test minimum commission enforcement."""
        model = PercentageCommission(rate=0.001, min_commission=10.0)
        cost = model.calculate_cost("SPY", 1, 100.0, pd.Timestamp("2024-01-01"))
        # Trade value: $100, commission: $0.10, but min is $10
        assert cost == 10.0

    def test_maximum_commission(self):
        """Test maximum commission cap."""
        model = PercentageCommission(rate=0.01, min_commission=1.0, max_commission=50.0)
        cost = model.calculate_cost("SPY", 1000, 100.0, pd.Timestamp("2024-01-01"))
        # Trade value: $100,000, commission: $1,000, but max is $50
        assert cost == 50.0

    def test_sell_order(self):
        """Test that sell orders pay same commission."""
        model = PercentageCommission(rate=0.001)
        cost = model.calculate_cost("SPY", -100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 50.0  # Same as buy order

    def test_invalid_max_commission_raises(self):
        """Test that max < min raises ValueError."""
        with pytest.raises(ValueError, match="max_commission must be >= min_commission"):
            PercentageCommission(rate=0.001, min_commission=10.0, max_commission=5.0)

    def test_name(self):
        """Test model name."""
        model = PercentageCommission(rate=0.001, min_commission=1.0, max_commission=50.0)
        name = model.get_name()
        assert "0.1000%" in name
        assert "min=$1.00" in name
        assert "max=$50.00" in name


class TestZeroSpread:
    """Tests for ZeroSpread model."""

    def test_zero_cost(self):
        """Test that ZeroSpread always returns zero."""
        model = ZeroSpread()
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.0

    def test_name(self):
        """Test model name."""
        model = ZeroSpread()
        assert model.get_name() == "ZeroSpread"


class TestFixedSpread:
    """Tests for FixedSpread model."""

    def test_spread_calculation(self):
        """Test spread cost calculation."""
        model = FixedSpread(bps=10)  # 10 bps = 0.10%
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        # Trade value: $50,000
        # Half-spread: 0.10% / 2 = 0.05%
        # Cost: $50,000 * 0.0005 = $25
        assert cost == 25.0

    def test_sell_order(self):
        """Test that sell orders pay same spread cost."""
        model = FixedSpread(bps=10)
        cost = model.calculate_cost("SPY", -100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 25.0

    def test_negative_bps_raises(self):
        """Test that negative bps raises ValueError."""
        with pytest.raises(ValueError, match="bps must be non-negative"):
            FixedSpread(bps=-10)

    def test_name(self):
        """Test model name."""
        model = FixedSpread(bps=10.5)
        assert "10.5 bps" in model.get_name()


class TestZeroSlippage:
    """Tests for ZeroSlippage model."""

    def test_zero_cost(self):
        """Test that ZeroSlippage always returns zero."""
        model = ZeroSlippage()
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.0

    def test_name(self):
        """Test model name."""
        model = ZeroSlippage()
        assert model.get_name() == "ZeroSlippage"


class TestFixedSlippage:
    """Tests for FixedSlippage model."""

    def test_slippage_calculation(self):
        """Test slippage cost calculation."""
        model = FixedSlippage(bps=5)  # 5 bps = 0.05%
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"))
        # Trade value: $50,000
        # Slippage: $50,000 * 0.0005 = $25
        assert cost == 25.0

    def test_sell_order(self):
        """Test that sell orders pay same slippage cost."""
        model = FixedSlippage(bps=5)
        cost = model.calculate_cost("SPY", -100, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 25.0

    def test_negative_bps_raises(self):
        """Test that negative bps raises ValueError."""
        with pytest.raises(ValueError, match="bps must be non-negative"):
            FixedSlippage(bps=-5)

    def test_name(self):
        """Test model name."""
        model = FixedSlippage(bps=5.5)
        assert "5.5 bps" in model.get_name()


class TestSqrtSlippage:
    """Tests for SqrtSlippage model."""

    def test_zero_cost_below_threshold(self):
        """Test that small orders below threshold have zero impact."""
        model = SqrtSlippage(coefficient=0.1, adv_fraction_threshold=0.01)
        # 100 shares out of 100,000 daily volume = 0.1% (above 1% threshold? No)
        # Wait, 0.1% is 0.001, which is < 0.01 threshold, so zero cost
        cost = model.calculate_cost("SPY", 100, 500.0, pd.Timestamp("2024-01-01"), daily_volume=100000)
        assert cost == 0.0

    def test_impact_above_threshold(self):
        """Test that large orders above threshold incur impact cost."""
        model = SqrtSlippage(coefficient=0.1, adv_fraction_threshold=0.01)
        # 2000 shares out of 100,000 daily volume = 2% (above 1% threshold)
        cost = model.calculate_cost("SPY", 2000, 500.0, pd.Timestamp("2024-01-01"), daily_volume=100000)
        # Trade value: $1,000,000
        # Impact factor: sqrt(2000 / 100000) = sqrt(0.02) ≈ 0.1414
        # Cost: 0.1 * 1,000,000 * 0.1414 ≈ 14,142
        assert cost > 0.0
        assert cost == pytest.approx(14142.14, rel=0.01)

    def test_zero_cost_no_volume_data(self):
        """Test that no volume data results in zero cost."""
        model = SqrtSlippage(coefficient=0.1)
        cost = model.calculate_cost("SPY", 2000, 500.0, pd.Timestamp("2024-01-01"))
        assert cost == 0.0

    def test_sell_order(self):
        """Test that sell orders incur same impact cost."""
        model = SqrtSlippage(coefficient=0.1, adv_fraction_threshold=0.01)
        cost = model.calculate_cost("SPY", -2000, 500.0, pd.Timestamp("2024-01-01"), daily_volume=100000)
        assert cost > 0.0

    def test_name(self):
        """Test model name."""
        model = SqrtSlippage(coefficient=0.15, adv_fraction_threshold=0.02)
        name = model.get_name()
        assert "coef=0.150" in name
        assert "threshold=2.00%" in name
