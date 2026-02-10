"""Bond class — replaces numba @jitclass with plain Python class."""
from __future__ import annotations

import numpy as np
import numpy_financial as npf


class Bond:
    __slots__ = ("face_value", "yield_pct", "maturity", "periods_per_year")

    def __init__(self, face_value: float, yield_pct: float, maturity: int, periods_per_year: int):
        self.face_value = face_value
        self.yield_pct = yield_pct
        self.maturity = maturity
        self.periods_per_year = periods_per_year

    def __repr__(self) -> str:
        return f"Maturity: {self.maturity} | Yield: {self.yield_pct * 100:.2f}% | Face Value: ${self.face_value:.2f}"

    def gen_payment(self) -> float:
        return self.face_value * self.yield_pct / self.periods_per_year

    def value(self, rates: np.ndarray) -> float:
        rate = rates[round(self.maturity) - 1]
        nper = self.maturity / self.periods_per_year
        pmt = self.face_value * self.yield_pct
        fv = self.face_value
        pv = npf.pv(rate, nper, pmt, fv)
        return -float(pv)

    def _key(self) -> tuple:
        return (self.face_value, self.yield_pct, float(self.maturity), float(self.periods_per_year))

    def __hash__(self) -> int:
        return hash(self._key())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Bond):
            return self._key() == other._key()
        return NotImplemented
