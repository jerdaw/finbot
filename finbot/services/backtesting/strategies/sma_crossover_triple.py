from __future__ import annotations

from typing import Any

import backtrader as bt


class SMACrossoverTriple(bt.Strategy):
    """Three-equity SMA crossover allocating based on fast/med/slow SMA ordering.

    Uses the relative ordering of three SMA periods on datas[0] to classify
    the market as uptrend, mid, or downtrend, and allocates to the
    corresponding equity:

    - Uptrend (fast > med > slow or fast > slow > med): Hold aggressive asset.
    - Mid (med > fast > slow or med > slow > fast): Hold moderate asset.
    - Downtrend (slow > med > fast or slow > fast > med): Hold defensive asset.

    Args:
        fast_ma: Period for the fast simple moving average.
        med_ma: Period for the medium simple moving average.
        slow_ma: Period for the slow simple moving average.

    Data feeds:
        datas[0]: Aggressive / high-beta asset.
        datas[1]: Moderate / balanced asset.
        datas[2]: Defensive / low-beta asset.
    """

    def __init__(self, fast_ma: int, med_ma: int, slow_ma: int) -> None:
        """Initialize the triple SMA crossover strategy.

        Args:
            fast_ma: Period for the fast simple moving average.
            med_ma: Period for the medium simple moving average.
            slow_ma: Period for the slow simple moving average.
        """
        self.fast_ma = fast_ma
        self.med_ma = med_ma
        self.slow_ma = slow_ma
        self.dataclose = self.datas[0].close
        self.order: Any = None
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.fast_ma)
        self.med_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.med_ma)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.slow_ma)

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Select target equity based on SMA ordering and rebalance.

        Classifies the trend from the fast/med/slow SMA values, sells
        non-target positions, and buys the target equity.
        """
        if self.order:
            return

        f_sma, m_sma, s_sma = self.fast_sma[0], self.med_sma[0], self.slow_sma[0]
        d_f, d_m, d_s = self.datas[0], self.datas[1], self.datas[2]

        if f_sma > m_sma > s_sma or f_sma > s_sma > m_sma:
            # Uptrend: buy aggressive (d_f if fms, d_m if fsm)
            target = d_f if f_sma > m_sma > s_sma else d_m
            others = [d for d in (d_f, d_m, d_s) if d is not target]
            for d in others:
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=target)
        elif m_sma > f_sma > s_sma or m_sma > s_sma > f_sma:
            # Mid: buy moderate (d_m)
            for d in (d_f, d_s):
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=d_m)
        else:
            # Downtrend: buy defensive (d_s)
            for d in (d_f, d_m):
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=d_s)
