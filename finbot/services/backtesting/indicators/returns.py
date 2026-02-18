from __future__ import annotations

from backtrader.indicators import Indicator


class Returns(Indicator):
    lines = ("returns",)
    params = (("period", 20),)

    def _plotlabel(self) -> list[int]:
        return [self.p.period]

    def __init__(self) -> None:
        self.lines.returns = self.data / self.data(-self.p.period) - 1.0  # type: ignore[attr-defined]
