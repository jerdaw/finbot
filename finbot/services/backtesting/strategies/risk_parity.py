"""Risk parity strategy that allocates inversely proportional to volatility.

Each asset receives a weight inversely proportional to its rolling
standard deviation of returns, so that each contributes roughly equal
risk to the portfolio.  Rebalances periodically.

Requires at least 2 data feeds.
"""

import backtrader as bt
import numpy as np


class RiskParity(bt.Strategy):
    """Risk parity: inverse-volatility weighting with periodic rebalance.

    Parameters:
        vol_window: Rolling window for volatility calculation (default 63 = ~3 months).
        rebal_interval: Periods between rebalances (default 21 = ~1 month).
    """

    def __init__(self, vol_window: int = 63, rebal_interval: int = 21):
        self.vol_window = vol_window
        self.rebal_interval = rebal_interval
        self.periods_elapsed = 0
        self.order = None

        # Track close prices for volatility calculation
        self.returns: dict[int, list[float]] = {i: [] for i in range(len(self.datas))}
        self.prev_close: dict[int, float | None] = dict.fromkeys(range(len(self.datas)))

    def notify_order(self, order):
        self.order = None

    def _compute_weights(self) -> list[float]:
        """Compute inverse-volatility weights for all assets."""
        inv_vols = []
        for i in range(len(self.datas)):
            rets = self.returns[i]
            if len(rets) >= self.vol_window:
                window = rets[-self.vol_window :]
                vol = float(np.std(window))
                inv_vols.append(1.0 / vol if vol > 0 else 0.0)
            else:
                inv_vols.append(0.0)

        total = sum(inv_vols)
        if total <= 0:
            # Equal weight fallback
            n = len(self.datas)
            return [1.0 / n] * n
        return [v / total for v in inv_vols]

    def next(self):
        if self.order:
            return  # type: ignore[unreachable]

        # Track returns
        for i, d in enumerate(self.datas):
            if self.prev_close[i] is not None:
                ret = (d.close[0] - self.prev_close[i]) / self.prev_close[i]
                self.returns[i].append(ret)
            self.prev_close[i] = d.close[0]

        # Wait for enough data
        if len(self.returns[0]) < self.vol_window:
            return

        self.periods_elapsed += 1
        if self.periods_elapsed < self.rebal_interval:
            return
        self.periods_elapsed = 0

        weights = self._compute_weights()
        total_value = self.broker.get_value()

        # Sell overweight first
        for i, d in enumerate(self.datas):
            target_value = weights[i] * total_value
            current_shares = self.getposition(d).size
            current_value = current_shares * d.close[0]
            diff_shares = int((current_value - target_value) // d.close[0])
            if diff_shares > 0:
                self.sell(data=d, size=diff_shares)

        # Buy underweight
        for i, d in enumerate(self.datas):
            target_value = weights[i] * total_value
            current_shares = self.getposition(d).size
            current_value = current_shares * d.close[0]
            diff_shares = int((target_value - current_value) // d.close[0])
            if diff_shares > 0:
                self.buy(data=d, size=diff_shares)
