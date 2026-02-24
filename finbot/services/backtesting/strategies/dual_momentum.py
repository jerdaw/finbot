"""Dual momentum strategy combining absolute and relative momentum.

Implements Gary Antonacci's dual momentum approach:
1. Absolute momentum: Is the primary asset's return over the lookback
   period positive? If not, stay in cash.
2. Relative momentum: Among available assets, which has the highest
   return over the lookback? Invest in the strongest.

Requires at least 2 data feeds: the primary asset(s) and a safe asset
(e.g., bonds or T-bills) used as the fallback when absolute momentum
is negative.
"""

import backtrader as bt


class DualMomentum(bt.Strategy):
    """Dual momentum: absolute + relative momentum with safe-asset fallback.

    Parameters:
        lookback: Number of periods for momentum calculation (default 252 = ~1 year).
        rebal_interval: Periods between rebalance checks (default 21 = ~1 month).

    Data feeds:
        datas[0]: Primary asset (e.g., SPY)
        datas[1]: Alternative/safe asset (e.g., TLT, IEF, SHY)
    """

    def __init__(self, lookback: int = 252, rebal_interval: int = 21):
        """Initialize the dual momentum strategy.

        Args:
            lookback: Number of periods for momentum calculation.
            rebal_interval: Periods between rebalance checks.
        """
        self.lookback = lookback
        self.rebal_interval = rebal_interval
        self.periods_elapsed = 0
        self.order = None

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def _momentum(self, data: bt.feeds.PandasData) -> float:
        """Return the return over the lookback period for a data feed."""
        if len(data) <= self.lookback:
            return 0.0
        return (data.close[0] - data.close[-self.lookback]) / data.close[-self.lookback]

    def _select_target(self) -> int:
        """Return the index of the asset to hold, or -1 for cash."""
        primary_mom = self._momentum(self.datas[0])
        alt_mom = self._momentum(self.datas[1]) if len(self.datas) > 1 else 0.0

        if primary_mom > 0 and primary_mom >= alt_mom:
            return 0
        if alt_mom > 0:
            return 1
        return -1  # Both negative — go to cash

    def _rebalance_to(self, target_idx: int) -> None:
        """Sell non-target positions and buy the target."""
        for i, d in enumerate(self.datas):
            pos = self.getposition(d).size
            if i == target_idx and pos == 0:
                cash = self.broker.get_cash()
                size = int(cash // d.close[0])
                if size > 0:
                    self.buy(data=d, size=size)
            elif i != target_idx and pos > 0:
                self.sell(data=d, size=pos)

    def next(self) -> None:
        """Execute dual momentum logic on each bar.

        Waits for sufficient lookback history, then rebalances at the
        configured interval by selecting the strongest asset or moving
        to cash if both assets show negative momentum.
        """
        if self.order:
            return  # type: ignore[unreachable]
        if len(self.datas[0]) <= self.lookback:
            return

        self.periods_elapsed += 1
        if self.periods_elapsed < self.rebal_interval:
            return
        self.periods_elapsed = 0

        self._rebalance_to(self._select_target())
