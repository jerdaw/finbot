from __future__ import annotations

from typing import Any

from backtrader import Analyzer


class CVTracker(Analyzer):
    """Backtrader analyzer that records cash and portfolio value on each bar.

    Collects starting/ending values and full time series of cash and
    portfolio value for use in performance metric calculations.
    """

    def __init__(self) -> None:
        """Initialize cash and value tracking lists."""
        super().__init__()
        self.rets: dict[str, Any] = {}
        self.value: list[float] = []
        self.cash: list[float] = []

    def start(self) -> None:
        """Called at backtest start. No-op for this analyzer."""
        pass

    def next(self) -> None:
        """Called on each bar. No-op; data is captured via notify_cashvalue."""
        pass

    def stop(self) -> None:
        """Called at backtest end. No-op for this analyzer."""
        pass

    def notify_cashvalue(self, cash: float, value: float) -> None:
        """Record cash and portfolio value on each broker notification.

        Args:
            cash: Current cash balance in the broker account.
            value: Current total portfolio value (cash + positions).
        """
        self.cash.append(cash)
        self.value.append(value)

    def get_analysis(self) -> dict[str, Any]:
        """Return analysis results with starting/ending values and full series.

        Returns:
            Dictionary with keys: "Starting Value", "Ending Value",
            "Value List", "Starting Cash", "Ending Cash", "Cash List".
        """
        self.rets = {
            "Starting Value": self.value[0],
            "Ending Value": self.value[-1],
            "Value List": self.value,
            "Starting Cash": self.cash[0],
            "Ending Cash": self.cash[-1],
            "Cash List": self.cash,
        }
        return self.rets
