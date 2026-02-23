"""Tests for bond ladder low-level components."""

from __future__ import annotations

import numpy as np

from finbot.services.simulation.bond_ladder.bond import Bond
from finbot.services.simulation.bond_ladder.build_yield_curve import build_yield_curve
from finbot.services.simulation.bond_ladder.ladder import BondLadder, make_annual_ladder
from finbot.services.simulation.bond_ladder.loop import iterate_fund


def test_build_yield_curve_interpolates_and_scales() -> None:
    curve = build_yield_curve(raw_rates={"DGS1": 3.0, "DGS10": 4.0}, yield_curve_size=12, periods_per_year=1)
    assert len(curve) == 12
    assert np.isclose(curve[0], 0.03)
    assert np.isclose(curve[9], 0.04)
    assert np.all(curve >= 0)


def test_bond_value_and_payments_positive() -> None:
    bond = Bond(face_value=100.0, yield_pct=0.05, maturity=2, periods_per_year=1)
    rates = np.array([0.04, 0.04])
    assert bond.gen_payment() == 5.0
    assert bond.value(rates) > 0


def test_make_annual_ladder_and_sell_bonds_flow() -> None:
    yields = np.array([0.02, 0.025, 0.03])
    ladder = make_annual_ladder(max_maturity=3, min_maturity=1, yields=yields, periods_per_year=1)
    assert isinstance(ladder, BondLadder)
    assert len(ladder.bonds) == 3

    rates = np.array([0.02, 0.025, 0.03])
    ladder.reduce_maturities()
    sold = ladder.sell_bonds(rates)
    assert isinstance(sold, bool)


def test_iterate_fund_returns_nav() -> None:
    rates = np.array([0.02, 0.025, 0.03])
    ladder = make_annual_ladder(max_maturity=3, min_maturity=1, yields=rates, periods_per_year=1)
    updated_ladder, nav = iterate_fund(ladder=ladder, yield_curve=rates, max_maturity=3)
    assert isinstance(updated_ladder, BondLadder)
    assert nav > 0
