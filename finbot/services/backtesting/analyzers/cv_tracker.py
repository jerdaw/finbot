from __future__ import annotations

from typing import Any

from backtrader import Analyzer


class CVTracker(Analyzer):
    def __init__(self) -> None:
        super().__init__()
        self.rets: dict[str, Any] = {}
        self.value: list[float] = []
        self.cash: list[float] = []

    def start(self) -> None:
        pass

    def next(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def notify_cashvalue(self, cash: float, value: float) -> None:
        self.cash.append(cash)
        self.value.append(value)

    def get_analysis(self) -> dict[str, Any]:
        self.rets = {
            "Starting Value": self.value[0],
            "Ending Value": self.value[-1],
            "Value List": self.value,
            "Starting Cash": self.cash[0],
            "Ending Cash": self.cash[-1],
            "Cash List": self.cash,
        }
        return self.rets
