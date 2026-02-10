from __future__ import annotations

from backtrader import Min
from backtrader.indicators import Indicator


class NegativeReturns(Indicator):
    lines = ("neg_returns",)
    params = (("period", 20),)

    def _plotlabel(self):
        return [self.p.period]

    def __init__(self):
        self.lines.returns = self.data / self.data(-self.p.period) - 1.0
        self.lines.neg_returns = Min(0.0, self.lines.returns)
