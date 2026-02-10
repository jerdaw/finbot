from __future__ import annotations

from backtrader import Analyzer


class CVTracker(Analyzer):
    def __init__(self):
        super().__init__()
        self.rets = {}
        self.value = []
        self.cash = []

    def start(self):
        pass

    def next(self):
        pass

    def stop(self):
        pass

    def notify_cashvalue(self, cash, value):
        self.cash.append(cash)
        self.value.append(value)

    def get_analysis(self):
        self.rets = {
            "Starting Value": self.value[0],
            "Ending Value": self.value[-1],
            "Value List": self.value,
            "Starting Cash": self.cash[0],
            "Ending Cash": self.cash[-1],
            "Cash List": self.cash,
        }
        return self.rets
