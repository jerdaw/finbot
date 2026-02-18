"""Unit tests for bond ladder simulator components.

All tests use synthetic yield data — no FRED API calls required.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.services.simulation.bond_ladder.bond import Bond
from finbot.services.simulation.bond_ladder.build_yield_curve import build_yield_curve
from finbot.services.simulation.bond_ladder.ladder import BondLadder, make_annual_ladder

# ── Helpers ───────────────────────────────────────────────────────────────────


PERIODS_PER_YEAR = 12  # monthly data


def _flat_yield_curve(rate: float = 0.04, size: int = 360) -> np.ndarray:
    """Build a flat yield curve at a constant rate."""
    return np.full(size, rate)


def _synthetic_yield_history(n: int = 36, rate: float = 0.04) -> pd.DataFrame:
    """Minimal yield history DataFrame for bond_ladder_simulator tests."""
    dates = pd.date_range("2018-01-31", periods=n, freq="ME")
    return pd.DataFrame(
        {"DGS1": rate * 100, "DGS10": rate * 100, "DGS30": rate * 100},
        index=dates,
    )


# ── Bond ─────────────────────────────────────────────────────────────────────


def test_bond_creation():
    b = Bond(face_value=1000.0, yield_pct=0.04, maturity=12, periods_per_year=12)
    assert b.face_value == 1000.0
    assert b.yield_pct == pytest.approx(0.04)
    assert b.maturity == 12
    assert b.periods_per_year == 12


def test_bond_gen_payment():
    # Monthly payment = face_value * yield_pct / periods_per_year
    b = Bond(face_value=1000.0, yield_pct=0.12, maturity=12, periods_per_year=12)
    expected = 1000.0 * 0.12 / 12  # = 10.0
    assert b.gen_payment() == pytest.approx(expected)


def test_bond_value_positive():
    b = Bond(face_value=1000.0, yield_pct=0.04, maturity=12, periods_per_year=12)
    rates = _flat_yield_curve(0.04)
    value = b.value(rates)
    assert value > 0


def test_bond_value_higher_rate_lowers_value():
    """When market rates rise, a bond's present value should fall."""
    b = Bond(face_value=1000.0, yield_pct=0.04, maturity=120, periods_per_year=12)
    rates_low = _flat_yield_curve(0.03)
    rates_high = _flat_yield_curve(0.07)
    assert b.value(rates_low) > b.value(rates_high)


def test_bond_equality():
    b1 = Bond(1000.0, 0.04, 12, 12)
    b2 = Bond(1000.0, 0.04, 12, 12)
    b3 = Bond(1000.0, 0.05, 12, 12)
    assert b1 == b2
    assert b1 != b3


def test_bond_hash_consistent():
    b = Bond(1000.0, 0.04, 12, 12)
    assert hash(b) == hash(b)


def test_bond_repr_contains_maturity():
    b = Bond(1000.0, 0.04, 12, 12)
    assert "12" in repr(b)


# ── BondLadder ────────────────────────────────────────────────────────────────


def test_ladder_empty():
    ladder = BondLadder(
        min_maturity=0,
        max_maturity=120,
        periods_per_year=12,
        bonds={},
    )
    rates = _flat_yield_curve()
    assert ladder.get_nav(rates) == pytest.approx(0.0)


def test_ladder_with_one_bond():
    b = Bond(1000.0, 0.04, 60, 12)
    ladder = BondLadder(
        min_maturity=0,
        max_maturity=120,
        periods_per_year=12,
        bonds={hash(b): b},
    )
    rates = _flat_yield_curve(0.04)
    assert ladder.get_nav(rates) > 0


def test_ladder_generate_payments_increases_cash():
    b = Bond(1000.0, 0.04, 60, 12)
    ladder = BondLadder(0, 120, 12, {hash(b): b})
    assert ladder.cash == pytest.approx(0.0)
    ladder.generate_payments()
    assert ladder.cash > 0


def test_ladder_reduce_maturities():
    b = Bond(1000.0, 0.04, 60, 12)
    ladder = BondLadder(0, 120, 12, {hash(b): b})
    original_maturity = next(iter(ladder.bonds.values())).maturity
    ladder.reduce_maturities()
    new_maturity = next(iter(ladder.bonds.values())).maturity
    assert new_maturity == original_maturity - 1


def test_ladder_sell_bonds_when_maturity_low():
    """Bonds at or below min_maturity should be sold and proceeds added to cash."""
    b = Bond(1000.0, 0.04, 1, 12)  # maturity 1 — at the edge
    ladder = BondLadder(min_maturity=1, max_maturity=120, periods_per_year=12, bonds={hash(b): b})
    rates = _flat_yield_curve(0.04)
    cash_before = ladder.cash
    sold = ladder.sell_bonds(rates)
    assert sold is True
    assert ladder.cash > cash_before
    assert len(ladder.bonds) == 0


def test_ladder_buy_bond_clears_cash():
    b = Bond(1000.0, 0.04, 60, 12)
    ladder = BondLadder(0, 120, 12, {hash(b): b})
    ladder.cash = 500.0
    ladder.buy_bond(rate=0.04, maturity=60)
    assert ladder.cash == pytest.approx(0.0)
    assert len(ladder.bonds) == 2  # original + new


# ── make_annual_ladder ────────────────────────────────────────────────────────


def test_make_annual_ladder_returns_ladder():
    yields = _flat_yield_curve(0.04, size=360)
    ladder = make_annual_ladder(max_maturity=120, min_maturity=12, yields=yields, periods_per_year=12)
    assert isinstance(ladder, BondLadder)


def test_make_annual_ladder_has_bonds():
    yields = _flat_yield_curve(0.04, size=360)
    ladder = make_annual_ladder(max_maturity=120, min_maturity=12, yields=yields, periods_per_year=12)
    assert len(ladder.bonds) > 0


# ── build_yield_curve ─────────────────────────────────────────────────────────


def test_build_yield_curve_returns_array():
    raw = {"DGS1": 3.5, "DGS10": 4.0, "DGS30": 4.5}
    yc = build_yield_curve(raw, yield_curve_size=360, periods_per_year=12)
    assert len(yc) == 360
    assert not np.any(np.isnan(yc))


def test_build_yield_curve_values_in_decimal_form():
    # Input is in percent (e.g. 4.0), output should be decimal (0.04)
    raw = {"DGS1": 4.0, "DGS10": 4.0, "DGS30": 4.0}
    yc = build_yield_curve(raw, yield_curve_size=360, periods_per_year=12)
    # All values should be between 0 and 1 (not 0 and 100)
    assert float(np.max(yc)) < 1.0


def test_build_yield_curve_interpolates_gaps():
    # Only provide a few anchor rates — gaps should be interpolated
    raw = {"DGS1": 3.0, "DGS30": 5.0}
    yc = build_yield_curve(raw, yield_curve_size=360, periods_per_year=12)
    # No NaNs after interpolation
    assert not np.any(np.isnan(yc))


# ── bond_ladder_simulator (end-to-end with synthetic yield history) ───────────


def test_bond_ladder_simulator_returns_dataframe():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    yh = _synthetic_yield_history(n=36, rate=0.04)
    result = bond_ladder_simulator(min_maturity_years=1, max_maturity_years=5, yield_history=yh, save_db=False)
    assert isinstance(result, pd.DataFrame)


def test_bond_ladder_simulator_has_close_and_change_columns():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    yh = _synthetic_yield_history(n=36, rate=0.04)
    result = bond_ladder_simulator(min_maturity_years=1, max_maturity_years=5, yield_history=yh, save_db=False)
    assert "Close" in result.columns
    assert "Change" in result.columns


def test_bond_ladder_simulator_starts_at_one():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    yh = _synthetic_yield_history(n=36, rate=0.04)
    result = bond_ladder_simulator(min_maturity_years=1, max_maturity_years=5, yield_history=yh, save_db=False)
    # Simulator scales output to start at 1
    assert result["Close"].iloc[0] == pytest.approx(1.0)


def test_bond_ladder_simulator_length_matches_yield_history():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    n = 24
    yh = _synthetic_yield_history(n=n, rate=0.04)
    result = bond_ladder_simulator(min_maturity_years=1, max_maturity_years=3, yield_history=yh, save_db=False)
    assert len(result) == n


def test_bond_ladder_simulator_no_negative_values():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    yh = _synthetic_yield_history(n=36, rate=0.03)
    result = bond_ladder_simulator(min_maturity_years=1, max_maturity_years=5, yield_history=yh, save_db=False)
    assert (result["Close"] >= 0).all()
