"""Unit tests for simulation math correctness."""

import numpy as np
import numpy_financial as npf


def test_compute_sim_changes_no_leverage():
    """With leverage=1 and no costs, changes should equal underlying changes."""
    from finbot.services.simulation.fund_simulator import _compute_sim_changes

    underlying = np.array([0.0, 0.01, -0.02, 0.005])
    libor = np.zeros(4)

    result = _compute_sim_changes(
        underlying_changes=underlying,
        period_libor_yield_percents=libor,
        leverage_mult=1.0,
        annual_er_pct=0.0,
        percent_daily_spread_cost=0.0,
        fund_swap_pct=0.0,
        periods_per_year=252,
    )
    np.testing.assert_allclose(result, underlying)


def test_compute_sim_changes_with_leverage():
    """With leverage=2, changes should be roughly 2x underlying minus costs."""
    from finbot.services.simulation.fund_simulator import _compute_sim_changes

    underlying = np.array([0.0, 0.01, -0.02])
    libor = np.array([0.05, 0.05, 0.05])  # 5% annual rate

    result = _compute_sim_changes(
        underlying_changes=underlying,
        period_libor_yield_percents=libor,
        leverage_mult=2.0,
        annual_er_pct=0.0,
        percent_daily_spread_cost=0.0,
        fund_swap_pct=0.0,
        periods_per_year=252,
    )
    # 2x leverage with 5% borrowing cost: change = underlying*2 - (0.05/252)*(2-1)
    daily_libor_cost = 0.05 / 252
    expected = underlying * 2 - daily_libor_cost
    np.testing.assert_allclose(result, expected)


def test_bond_pv_calculation():
    """Verify numpy_financial.pv gives correct present value."""
    # $1000 face value, 5% coupon, 10 years, 4% discount rate
    pv = npf.pv(rate=0.04, nper=10, pmt=-50, fv=-1000)
    assert pv > 1000  # Should trade at premium (coupon > discount)
    assert round(pv, 2) == 1081.11


def test_monte_carlo_sim_type_nd():
    """Verify normal distribution sim produces expected shape."""
    from finbot.services.simulation.monte_carlo.sim_types import sim_type_nd

    result = sim_type_nd(sim_periods=252, start_price=100, mu=0.0004, sigma=0.01, n_sims=1, cov_matrix=None)
    assert result.shape == (252,)
    assert result[0] == 100  # Start price preserved (daily_changes[0] = 1)
    assert np.all(np.isfinite(result))
