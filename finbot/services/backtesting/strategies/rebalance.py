from __future__ import annotations

from typing import Any

import backtrader as bt


class Rebalance(bt.Strategy):
    """Rebalance multiple stocks with configurable proportions and interval."""

    def __init__(self, rebal_proportions: list[float], rebal_interval: int) -> None:
        self.rebal_proportions = rebal_proportions
        self.rebal_interval = rebal_interval
        self.periods_since_last_rebal = rebal_interval
        self.dataclose = self.datas[0].close
        self.order: Any = None

    def notify_order(self, order: bt.Order) -> None:
        self.order = None

    def next(self) -> None:
        if self.order:
            return

        if self.periods_since_last_rebal >= self.rebal_interval:
            n_stocks = len(self.datas)
            cur_tot_value = self.broker.get_value()
            cur_n_stocks = [self.getposition(d).size for d in self.datas]
            des_values = [self.rebal_proportions[i] * cur_tot_value for i in range(n_stocks)]
            des_n_stocks = [round(des_values[i] // self.datas[i].close) for i in range(n_stocks)]

            # Sell overweight first to free cash
            for d_idx in range(n_stocks):
                n_diff = cur_n_stocks[d_idx] - des_n_stocks[d_idx]
                if round(n_diff) > 0:
                    self.sell(data=self.datas[d_idx], size=abs(round(n_diff)))

            # Recalculate and buy underweight
            des_values = [self.rebal_proportions[i] * cur_tot_value for i in range(n_stocks)]
            des_n_stocks = [round(des_values[i] // self.datas[i].close) for i in range(n_stocks)]
            for d_idx in range(n_stocks):
                n_diff = cur_n_stocks[d_idx] - des_n_stocks[d_idx]
                if round(n_diff) < 0:
                    self.buy(data=self.datas[d_idx], size=abs(round(n_diff)))

            self.periods_since_last_rebal = 0
        else:
            self.periods_since_last_rebal += 1
