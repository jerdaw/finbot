from __future__ import annotations

from typing import Any

import backtrader as bt


class MACDSingle(bt.Strategy):
    """Single-equity MACD crossover strategy.

    Buys when the MACD line crosses above the signal line and sells when
    the MACD line crosses below the signal line. Operates on a single
    data feed.

    Args:
        fast_ma: Period for the fast EMA (MACD period_me1).
        slow_ma: Period for the slow EMA (MACD period_me2).
        signal_period: Period for the signal line EMA.

    Data feeds:
        datas[0]: The equity to trade.
    """

    def __init__(self, fast_ma: int, slow_ma: int, signal_period: int) -> None:
        """Initialize the MACD single-equity strategy.

        Args:
            fast_ma: Period for the fast EMA component.
            slow_ma: Period for the slow EMA component.
            signal_period: Period for the signal line smoothing.
        """
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.signal_period = signal_period
        self.dataclose = self.datas[0].close
        self.order: Any = None
        self.macd = bt.indicators.MACD(
            self.data,
            period_me1=self.fast_ma,
            period_me2=self.slow_ma,
            period_signal=self.signal_period,
        )
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Execute MACD crossover logic on each bar.

        Buys on positive crossover (MACD > signal) when no position is held.
        Sells on negative crossover (MACD < signal) when a position is held.
        """
        if self.order:
            return
        if not self.getposition(self.datas[0]):
            if self.mcross[0] > 0.0:
                self.buy()
        else:
            if self.mcross[0] < 0.0:
                self.sell()
