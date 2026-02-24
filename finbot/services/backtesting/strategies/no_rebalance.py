from __future__ import annotations

from typing import Any

import backtrader as bt


class NoRebalance(bt.Strategy):
    """Buy-and-hold strategy that allocates once and never rebalances.

    On the first bar with no existing position, allocates available cash
    across all data feeds according to the specified proportions.

    Args:
        equity_proportions: Target weight for each data feed (must sum to 1.0).

    Data feeds:
        Accepts N data feeds, one per equity to hold.
    """

    def __init__(self, equity_proportions: list[float]) -> None:
        """Initialize the buy-and-hold strategy.

        Args:
            equity_proportions: Target allocation weights for each data feed.
        """
        self.equity_proportions = equity_proportions
        self.dataclose = self.datas[0].close
        self.order: Any = None

    def notify_order(self, order: bt.Order) -> None:
        """Reset pending order flag when an order completes."""
        self.order = None

    def next(self) -> None:
        """Buy all positions on the first bar with no existing position.

        Skips if an order is pending or any position already exists.
        Allocates available cash according to equity_proportions.
        """
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
