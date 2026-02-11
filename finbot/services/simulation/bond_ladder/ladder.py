"""BondLadder class — replaces numba @jitclass with plain Python."""

from __future__ import annotations

import numpy as np

from finbot.services.simulation.bond_ladder.bond import Bond


def make_annual_ladder(
    max_maturity: int,
    min_maturity: int,
    yields: np.ndarray,
    periods_per_year: int,
) -> BondLadder:
    rate = yields[max_maturity - 1]
    face_value = 50.0
    bonds: dict[int, Bond] = {}
    for i, m in enumerate(range(min_maturity, max_maturity + 1)):
        b = Bond(face_value * (1 + rate / periods_per_year) ** i, rate, m, periods_per_year)
        bonds[hash(b)] = b
    ladder = BondLadder(min_maturity - periods_per_year, max_maturity, periods_per_year, bonds)
    return ladder


class BondLadder:
    __slots__ = ("bonds", "cash", "max_maturity", "min_maturity", "periods_per_year")

    def __init__(
        self,
        min_maturity: int,
        max_maturity: int,
        periods_per_year: int,
        bonds: dict[int, Bond],
    ):
        self.min_maturity = min_maturity
        self.max_maturity = max_maturity
        self.periods_per_year = periods_per_year
        self.cash = 0.0
        self.bonds = bonds

    def buy_bond(self, rate: float, maturity: int) -> Bond:
        b = Bond(self.cash, rate, maturity, self.periods_per_year)
        self.bonds[hash(b)] = b
        self.cash = 0.0
        return b

    def get_nav(self, rates: np.ndarray) -> float:
        bond_vals = sum(b.value(rates) for b in self.bonds.values())
        return self.cash + bond_vals

    def generate_payments(self) -> None:
        for b in self.bonds.values():
            self.cash += b.gen_payment()

    def reduce_maturities(self) -> None:
        for b in self.bonds.values():
            b.maturity -= 1
        self._regen_bonds_hashes()

    def sell_bonds(self, rates: np.ndarray) -> bool:
        bonds_sold = False
        for h, b in list(self.bonds.items()):
            if b.maturity <= self.min_maturity:
                self.cash += b.value(rates)
                del self.bonds[h]
                bonds_sold = True
        return bonds_sold

    def _regen_bonds_hashes(self) -> None:
        self.bonds = {hash(b): b for b in self.bonds.values()}
