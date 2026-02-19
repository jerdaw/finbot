"""Tests for optimization.rebalance_optimizer module behavior."""

from __future__ import annotations

import pytest

from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer
from finbot.services.optimization.rebalance_optimizer import RebalanceOptimizer, optimize_rebalance


def test_rebalance_optimizer_placeholder_run_raises() -> None:
    optimizer = RebalanceOptimizer(stocks=["SPY", "TLT"], transaction_cost=0.001)
    with pytest.raises(NotImplementedError, match="not yet implemented"):
        optimizer.run()


def test_rebalance_optimizer_init_defaults() -> None:
    optimizer = RebalanceOptimizer()
    assert optimizer.stocks == []
    assert optimizer.transaction_cost == 0.0


def test_optimize_rebalance_alias_points_to_backtesting_impl() -> None:
    assert optimize_rebalance is rebalance_optimizer
