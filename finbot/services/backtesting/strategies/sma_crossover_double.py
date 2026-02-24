from __future__ import annotations

from typing import Any

import backtrader as bt


class SMACrossoverDouble(bt.Strategy):
    """Two-equity SMA crossover that rotates between data[0] and data[1].

    Uses the SMA crossover signal on datas[0] to decide which asset to hold.
    When the fast SMA is above the slow SMA, holds datas[0] (risk-on);
    otherwise, holds datas[1] (risk-off / safe asset).

    Args:
        fast_ma: Period for the fast simple moving average on datas[0].
        slow_ma: Period for the slow simple moving average on datas[0].

    Data feeds:
        datas[0]: Primary / risk-on asset.
        datas[1]: Alternative / risk-off asset.
    """

    def __init__(self, fast_ma: int, slow_ma: int) -> None:
        """Initialize the double SMA crossover strategy.

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
        """Rotate between two equities based on SMA crossover signal.

        Holds datas[0] when fast SMA >= slow SMA, otherwise holds datas[1].
        Sells the current holding before buying the other.
        """
        if self.order:
            return
        if self.fast_sma[0] >= self.slow_sma[0]:
            if self.getposition(self.datas[1]):
                self.order = self.sell(data=self.datas[1])
            else:
                self.order = self.buy(data=self.datas[0])
        else:
            if self.getposition(self.datas[0]):
                self.order = self.sell(data=self.datas[0])
            else:
                self.order = self.buy(data=self.datas[1])
