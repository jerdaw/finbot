from __future__ import annotations

from backtrader import Max
from backtrader.indicators import Indicator


class PositiveReturns(Indicator):
    lines = ("pos_returns",)
    params = (("period", 20),)

    def _plotlabel(self) -> list[int]:
        return [self.p.period]

    def __init__(self) -> None:
        self.lines.returns = self.data / self.data(-self.p.period) - 1.0  # type: ignore[attr-defined]
        self.lines.pos_returns = Max(0.0, self.lines.returns)  # type: ignore[attr-defined]
