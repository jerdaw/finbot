from __future__ import annotations

from typing import Any

import backtrader as bt


class DipBuySMA(bt.Strategy):
    """Dip-buying strategy using SMA ordering as a buy trigger.

    Buys aggressively when the SMA ordering indicates a dip
    (slow > med > fast), deploying all available cash. When no dip is
    detected, periodically sells 5% of the position every quarter
    (~63 trading days) to lock in profits.

    Args:
        fast_ma: Period for the fast simple moving average.
        med_ma: Period for the medium simple moving average.
        slow_ma: Period for the slow simple moving average.

    Data feeds:
        datas[0]: The equity to trade on dip signals.
    """

    def __init__(self, fast_ma: int, med_ma: int, slow_ma: int) -> None:
        """Initialize the SMA dip-buy strategy.

        Args:
            fast_ma: Period for the fast simple moving average.
            med_ma: Period for the medium simple moving average.
            slow_ma: Period for the slow simple moving average.
        """
        self.fast_ma = fast_ma
        self.med_ma = med_ma
        self.slow_ma = slow_ma
        self.d_since_last_sale = 0
        self.dataclose = self.datas[0].close
        self.order: Any = None
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.fast_ma)
        self.med_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.med_ma)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.slow_ma)

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Execute dip-buy logic on each bar.

        When slow > med > fast SMA, buys with all available cash.
        Otherwise, sells 5% of holdings every ~63 bars to take profits.
        """
        if self.order:
            return

        f_sma, m_sma, s_sma = self.fast_sma[0], self.med_sma[0], self.slow_sma[0]

        if s_sma > m_sma > f_sma:
            cash = self.broker.get_cash()
            close = self.datas[0][0]
            n_to_buy = round(cash // close)
            if n_to_buy:
                self.buy(data=self.datas[0], size=n_to_buy)
        elif self.d_since_last_sale > round(252 / 4):
            n_equities = self.getposition(data=self.datas[0]).size
            n_to_sell = round(n_equities * 0.05)
            if n_to_sell:
                self.sell(data=self.datas[0], size=n_to_sell)
                self.d_since_last_sale = 0
        self.d_since_last_sale += 1
