from __future__ import annotations

from typing import Any

import backtrader as bt


class SMACrossover(bt.Strategy):
    """Single-equity SMA crossover strategy.

    Buys when the fast SMA crosses above the slow SMA and sells when the
    slow SMA crosses above the fast SMA. Operates on a single data feed.

    Args:
        fast_ma: Period for the fast simple moving average.
        slow_ma: Period for the slow simple moving average.

    Data feeds:
        datas[0]: The equity to trade.
    """

    def __init__(self, fast_ma: int, slow_ma: int) -> None:
        """Initialize the SMA crossover strategy.

        Args:
            fast_ma: Period for the fast simple moving average.
            slow_ma: Period for the slow simple moving average.
        """
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.dataclose = self.datas[0].close
        self.order: Any = None
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.fast_ma)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.slow_ma)

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Execute crossover logic on each bar.

        Buys when fast SMA >= slow SMA and no position is held.
        Sells when slow SMA > fast SMA and a position is held.
        """
        if self.order:
            return
        if not self.position:
            if self.fast_sma[0] >= self.slow_sma[0]:
                self.order = self.buy()
        else:
            if self.slow_sma[0] > self.fast_sma[0]:
                self.order = self.sell()
