from __future__ import annotations

from typing import Any

import backtrader as bt


class NoRebalance(bt.Strategy):
    """Basic buy and hold strategy with no rebalancing."""

    def __init__(self, equity_proportions: list[float]) -> None:
        self.equity_proportions = equity_proportions
        self.dataclose = self.datas[0].close
        self.order: Any = None

    def notify_order(self, order: bt.Order) -> None:
        self.order = None

    def next(self) -> None:
        if self.order:
            return
        if not self.getposition():
            n_stocks = len(self.datas)
            cur_tot_cash = self.broker.get_cash()
            des_values = [self.equity_proportions[i] * cur_tot_cash for i in range(n_stocks)]
            des_n_stocks = [round(des_values[i] // self.datas[i].close) for i in range(n_stocks)]
            for d_idx in range(n_stocks):
                des_n = des_n_stocks[d_idx]
                self.buy(data=self.datas[d_idx], size=abs(round(des_n)))
