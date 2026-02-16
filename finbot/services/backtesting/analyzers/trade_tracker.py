"""Analyzer to track all executed trades during backtest."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import backtrader as bt

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True, slots=True)
class TradeInfo:
    """Information about a single executed trade."""

    timestamp: pd.Timestamp
    symbol: str
    size: float  # Positive for buy, negative for sell
    price: float
    value: float  # Total trade value (size * price)
    commission: float  # Commission charged by broker


class TradeTracker(bt.Analyzer):
    """Analyzer that tracks all executed trades.

    Captures trade execution details including timestamp, symbol, size,
    price, and commission for cost model calculations.
    """

    def __init__(self):
        super().__init__()
        self.trades: list[TradeInfo] = []

    def notify_trade(self, trade):
        """Called by backtrader when a trade is closed.

        Note: This captures closed trades only. For open positions,
        we track individual order executions via notify_order.
        """
        pass  # We use notify_order instead for more granular tracking

    def notify_order(self, order):
        """Called when an order is executed, partially filled, or completed."""
        if order.status in [order.Completed] and order.executed.size != 0:
            # Order was fully executed (ignore zero-size orders)
            # Get the data name (symbol) for this order
            symbol = order.data._name if hasattr(order.data, "_name") else "UNKNOWN"

            trade_info = TradeInfo(
                timestamp=bt.num2date(order.executed.dt),
                symbol=symbol,
                size=order.executed.size,
                price=order.executed.price,
                value=order.executed.value,
                commission=order.executed.comm,
            )
            self.trades.append(trade_info)

    def get_analysis(self):
        """Return collected trade information."""
        return {"trades": self.trades, "trade_count": len(self.trades)}
