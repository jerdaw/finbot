from __future__ import annotations

from backtrader.indicators import Indicator


class Returns(Indicator):
    lines = ("returns",)
    params = (("period", 20),)

    def _plotlabel(self):
        return [self.p.period]

    def __init__(self):
        self.lines.returns = self.data / self.data(-self.p.period) - 1.0
