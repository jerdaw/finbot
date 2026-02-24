from __future__ import annotations

from typing import Any

import backtrader as bt


class MACDDual(bt.Strategy):
    """Two-equity MACD crossover that rotates between data[0] and data[1].

    Uses the MACD crossover signal on datas[0] to decide which asset to hold.
    When MACD >= signal, holds datas[0] (risk-on); otherwise holds datas[1]
    (risk-off / safe asset).

    Args:
        fast_ma: Period for the fast EMA (MACD period_me1).
        slow_ma: Period for the slow EMA (MACD period_me2).
        signal_period: Period for the signal line EMA.

    Data feeds:
        datas[0]: Primary / risk-on asset.
        datas[1]: Alternative / risk-off asset.
    """

    def __init__(self, fast_ma: int, slow_ma: int, signal_period: int) -> None:
        """Initialize the MACD dual-equity strategy.

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
        """Rotate between two equities based on MACD crossover signal.

        Holds datas[0] when MACD crossover >= 0, otherwise holds datas[1].
        Sells the current holding before buying the other.
        """
        if self.order:
            return
        if self.mcross[0] >= 0.0:
            if self.getposition(data=self.datas[1]):
                self.sell(data=self.datas[1])
            self.buy(data=self.datas[0])
        else:
            if self.getposition(data=self.datas[0]):
                self.sell(data=self.datas[0])
            self.buy(data=self.datas[1])
