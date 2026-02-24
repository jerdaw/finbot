from __future__ import annotations

from typing import Any

import backtrader as bt
from numpy import quantile

from finbot.services.backtesting.indicators.negative_returns import NegativeReturns
from finbot.services.backtesting.indicators.positive_returns import PositiveReturns


class DipBuyStdev(bt.Strategy):
    """Dip-buying strategy using return distribution quantiles.

    Buys when the current negative return falls below its historical
    quantile (indicating a significant dip) and sells when the current
    positive return exceeds its historical quantile (indicating unusual
    strength). Optionally rotates between datas[0] and datas[1].

    Uses a 252-bar window for positive returns and a 63-bar window
    (~1 quarter) for negative returns.

    Args:
        buy_quantile: Quantile threshold for negative returns to trigger a buy
            (e.g., 0.1 means buy on the worst 10% of negative returns).
        sell_quantile: Quantile threshold for positive returns to trigger a sell
            (default 1.0 effectively disables selling on positive returns).

    Data feeds:
        datas[0]: Primary equity to buy on dips.
        datas[1] (optional): Alternative asset to rotate into on sells.
    """

    def __init__(self, buy_quantile: float, sell_quantile: float = 1.0) -> None:
        """Initialize the standard-deviation dip-buy strategy.

        Args:
            buy_quantile: Quantile threshold for negative returns (buy trigger).
            sell_quantile: Quantile threshold for positive returns (sell trigger).
        """
        self.buy_quantile = buy_quantile
        self.sell_quantile = sell_quantile
        self.d_since_last_sale = 0
        self.dataclose = self.datas[0].close
        self.order: Any = None
        self.pos_returns = PositiveReturns(self.datas[0], period=252)  # type: ignore[call-arg]
        self.neg_returns = NegativeReturns(self.datas[0], period=round(252 / 4))  # type: ignore[call-arg]

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Execute quantile-based dip-buy logic on each bar.

        Buys datas[0] when negative returns fall below buy_quantile, selling
        datas[1] if needed to fund the purchase. Sells datas[0] when positive
        returns exceed sell_quantile, optionally buying datas[1] with proceeds.
        """
        if self.order:
            return

        neg_q = quantile(self.neg_returns, self.buy_quantile, method="linear")
        pos_q = quantile(self.pos_returns, self.sell_quantile, method="linear")
        n_equities = self.getposition(data=self.datas[0]).size

        if self.neg_returns[0] <= neg_q:
            cash = self.broker.get_cash()
            cash_to_spend = cash * max(0, min(1, abs(neg_q)))
            close = self.datas[0][0]
            if cash_to_spend:
                if len(self.datas) > 1:
                    d1_close = self.datas[1].close[0]
                    d1_pos = self.getposition(data=self.datas[1]).size
                    self.sell(data=self.datas[1], size=min(d1_pos, cash_to_spend // d1_close + 1))
                self.buy(data=self.datas[0], size=round(cash_to_spend // close))
        elif self.pos_returns[0] >= pos_q and n_equities:
            n_to_sell = round(n_equities * max(0, min(1, abs(pos_q - 1))))
            dollars_sold = n_to_sell * self.datas[0].close[0]
            if n_to_sell:
                self.sell(data=self.datas[0], size=n_to_sell)
                if len(self.datas) > 1:
                    d1_close = self.datas[1].close[0]
                    max_buy = round(self.broker.get_cash() // d1_close)
                    self.buy(data=self.datas[1], size=min(max_buy, round(dollars_sold // d1_close)))

        self.d_since_last_sale += 1
