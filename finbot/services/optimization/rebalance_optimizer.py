"""Rebalance optimizer.

Placeholder for portfolio rebalance optimization. The backtest-based
rebalance optimizer lives in finbot.services.backtesting.rebalance_optimizer.
"""

from collections.abc import Sequence

import pandas as pd


class RebalanceOptimizer:
    """Optimizer for portfolio rebalance strategies.

    Planned optimization targets:
    - Static allocations (60/40, equal weight, etc.)
    - Dynamic allocations (MA crossovers, CAGR-based, volatility-based)
    - Rebalance frequency (daily, monthly, etc.) with transaction costs
    - Combinations of technical indicators for allocation shifts
    """

    def __init__(
        self,
        stocks: Sequence[str] | None = None,
        transaction_cost: float = 0.0,
    ) -> None:
        self.stocks = list(stocks) if stocks else []
        self.transaction_cost = transaction_cost

    def run(self) -> pd.DataFrame:
        raise NotImplementedError(
            "RebalanceOptimizer is not yet implemented. "
            "Use finbot.services.backtesting.rebalance_optimizer for "
            "backtest-based rebalance optimization."
        )
