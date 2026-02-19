"""Regime-adaptive allocation strategy.

Dynamically adjusts equity vs. bond allocation based on the current market
regime, detected inline from a rolling window of the primary asset's returns.

This strategy is intended as a **demonstration** of how regime detection can
be integrated with Backtrader.  It should not be treated as a trading
recommendation.

Regime classification (applied to the last *lookback* bars of datas[0]):
  - VOLATILE : annualised volatility > vol_threshold
  - BULL     : not VOLATILE and annualised return > bull_threshold
  - BEAR     : not VOLATILE and annualised return < bear_threshold
  - SIDEWAYS : everything else

Allocation per regime:
  - BULL     : equity_pct = bull_equity_pct (default 0.90)
  - SIDEWAYS : equity_pct = sideways_equity_pct (default 0.60)
  - VOLATILE : equity_pct = volatile_equity_pct (default 0.30)
  - BEAR     : equity_pct = bear_equity_pct (default 0.10)

Requires exactly 2 data feeds:
  datas[0] — equity asset (e.g. SPY)
  datas[1] — safe asset / bond proxy (e.g. TLT or IEF)

DISCLAIMER: For educational and research purposes only.  Past performance
does not predict future results.
"""

from __future__ import annotations

import backtrader as bt
import numpy as np

# Regime label constants (strings avoid importing the StrEnum at strategy import time)
_REGIME_BULL = "bull"
_REGIME_BEAR = "bear"
_REGIME_VOLATILE = "volatile"
_REGIME_SIDEWAYS = "sideways"


class RegimeAdaptive(bt.Strategy):
    """Regime-adaptive equity/bond allocation with periodic rebalancing.

    Parameters:
        lookback: Rolling window (bars) used for regime classification.
            Default 252 (~1 trading year).
        rebal_interval: Bars between rebalance events.  Default 21 (~1 month).
        bull_threshold: Annualised return threshold that triggers BULL regime.
            Default 0.15 (15 %).
        bear_threshold: Annualised return threshold that triggers BEAR regime.
            Default -0.10 (-10 %).
        vol_threshold: Annualised volatility threshold that triggers VOLATILE
            regime.  Default 0.25 (25 %).
        bull_equity_pct: Equity fraction during BULL regime.  Default 0.90.
        sideways_equity_pct: Equity fraction during SIDEWAYS regime.
            Default 0.60.
        volatile_equity_pct: Equity fraction during VOLATILE regime.
            Default 0.30.
        bear_equity_pct: Equity fraction during BEAR regime.  Default 0.10.
    """

    def __init__(
        self,
        lookback: int = 252,
        rebal_interval: int = 21,
        bull_threshold: float = 0.15,
        bear_threshold: float = -0.10,
        vol_threshold: float = 0.25,
        bull_equity_pct: float = 0.90,
        sideways_equity_pct: float = 0.60,
        volatile_equity_pct: float = 0.30,
        bear_equity_pct: float = 0.10,
    ) -> None:
        self.lookback = lookback
        self.rebal_interval = rebal_interval
        self.bull_threshold = bull_threshold
        self.bear_threshold = bear_threshold
        self.vol_threshold = vol_threshold

        self.bull_equity_pct = bull_equity_pct
        self.sideways_equity_pct = sideways_equity_pct
        self.volatile_equity_pct = volatile_equity_pct
        self.bear_equity_pct = bear_equity_pct

        self.periods_elapsed: int = 0
        self.order: bt.Order | None = None

    def notify_order(self, order: bt.Order) -> None:
        if order.status in (order.Completed, order.Cancelled, order.Rejected):
            self.order = None

    def _classify_regime(self) -> str:
        """Classify the current market regime from rolling primary-asset returns.

        Returns one of: "bull", "bear", "volatile", "sideways".
        Falls back to "sideways" when insufficient history is available.
        """
        equity = self.datas[0]
        n_available = len(equity)
        window_size = min(self.lookback + 1, n_available)

        if window_size < 2:
            return _REGIME_SIDEWAYS

        prices = np.array(equity.close.get(size=window_size), dtype=float)
        # get() returns newest-first; reverse to chronological order
        prices = prices[::-1]

        daily_returns = np.diff(prices) / prices[:-1]
        ann_return = float(np.mean(daily_returns) * 252)
        ann_vol = float(np.std(daily_returns, ddof=1) * (252**0.5))

        if ann_vol > self.vol_threshold:
            return _REGIME_VOLATILE
        if ann_return > self.bull_threshold:
            return _REGIME_BULL
        if ann_return < self.bear_threshold:
            return _REGIME_BEAR
        return _REGIME_SIDEWAYS

    def _equity_pct_for(self, regime: str) -> float:
        """Return the target equity fraction for a given regime label."""
        return {
            _REGIME_BULL: self.bull_equity_pct,
            _REGIME_BEAR: self.bear_equity_pct,
            _REGIME_VOLATILE: self.volatile_equity_pct,
            _REGIME_SIDEWAYS: self.sideways_equity_pct,
        }[regime]

    def _set_target_value(self, data: bt.feeds.PandasData, target_value: float) -> None:
        """Adjust a position toward a target dollar value (sell first)."""
        current_shares = self.getposition(data).size
        current_value = current_shares * data.close[0]
        diff_value = target_value - current_value

        if diff_value < 0:
            # Need to sell
            shares_to_sell = int(abs(diff_value) // data.close[0])
            if shares_to_sell > 0 and current_shares >= shares_to_sell:
                self.sell(data=data, size=shares_to_sell)
        elif diff_value > 0:
            # Need to buy
            shares_to_buy = int(diff_value // data.close[0])
            if shares_to_buy > 0:
                self.buy(data=data, size=shares_to_buy)

    def next(self) -> None:
        if self.order:
            return

        # Wait for enough history
        if len(self.datas[0]) < self.lookback:
            return

        self.periods_elapsed += 1
        if self.periods_elapsed < self.rebal_interval:
            return
        self.periods_elapsed = 0

        regime = self._classify_regime()
        equity_pct = self._equity_pct_for(regime)
        bond_pct = 1.0 - equity_pct

        total_value = self.broker.get_value()
        equity_target = equity_pct * total_value
        bond_target = bond_pct * total_value

        equity_data = self.datas[0]
        bond_data = self.datas[1]

        # Sell overweight positions first to free cash
        equity_current = self.getposition(equity_data).size * equity_data.close[0]
        bond_current = self.getposition(bond_data).size * bond_data.close[0]

        if equity_current > equity_target:
            self._set_target_value(equity_data, equity_target)
        if bond_current > bond_target:
            self._set_target_value(bond_data, bond_target)

        # Then buy underweight positions
        if equity_current < equity_target:
            self._set_target_value(equity_data, equity_target)
        if bond_current < bond_target:
            self._set_target_value(bond_data, bond_target)
