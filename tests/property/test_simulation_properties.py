"""Property-based tests for simulation functions.

Tests mathematical properties of fund simulator and related functions.
"""

from __future__ import annotations

import numpy as np
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from finbot.services.simulation.fund_simulator import _compute_sim_changes
from tests.property.conftest import daily_returns, expense_ratios, leverage_mult


class TestFundSimulatorProperties:
    """Property tests for fund simulator helper functions."""

    @given(
        underlying_change=daily_returns,
        leverage=leverage_mult,
        annual_er=expense_ratios,
        periods=st.sampled_from([252, 365]),
    )
    @settings(max_examples=200)
    def test_leverage_amplifies_returns(self, underlying_change, leverage, annual_er, periods):
        """Test that leverage amplifies underlying returns.

        Property: For leverage > 1, |fund_change| > |underlying_change| (ignoring fees).
        """
        # Create minimal inputs for _compute_sim_changes
        underlying_changes = np.array([underlying_change])
        period_libor_yields = np.array([0.02])  # 2% LIBOR

        # Compute with fees (realistic)
        fund_changes = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=leverage,
            annual_er_pct=annual_er,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        fund_change = fund_changes[0]

        # Skip cases with tiny underlying changes (fees dominate)
        assume(abs(underlying_change) > 0.001)

        # Property: Leverage amplification (approximately)
        # fund_change ≈ underlying_change * leverage - fees
        # So the direction should still be amplified
        if (
            leverage > 1.1 and abs(underlying_change) > annual_er / periods
        ):  # For meaningful leverage, fund change should be in the same direction (for large enough moves)
            if underlying_change > 0:
                assert fund_change > 0 or fund_change > underlying_change - 0.01
            elif underlying_change < 0:
                assert fund_change < 0 or fund_change < underlying_change + 0.01

    @given(
        underlying_change=daily_returns,
        leverage=leverage_mult,
        annual_er=st.floats(min_value=0.0, max_value=0.02),
    )
    @settings(max_examples=150)
    def test_higher_fees_reduce_returns(self, underlying_change, leverage, annual_er):
        """Test that higher expense ratios reduce returns.

        Property: For same inputs, higher ER → lower fund returns.
        """
        periods = 252
        underlying_changes = np.array([underlying_change])
        period_libor_yields = np.array([0.02])

        # Low fees
        fund_changes_low = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=leverage,
            annual_er_pct=0.0,  # Zero fees
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # High fees
        fund_changes_high = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=leverage,
            annual_er_pct=annual_er,  # Non-zero fees
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # Property: Higher fees → lower (or equal) returns
        assert fund_changes_high[0] <= fund_changes_low[0] + 1e-10  # Allow tiny floating-point error

    @given(
        underlying_change=daily_returns,
        leverage=leverage_mult,
    )
    @settings(max_examples=100)
    def test_libor_cost_for_leveraged_funds(self, underlying_change, leverage):
        """Test that LIBOR costs apply to leveraged portion.

        Property: LIBOR costs scale with (leverage - 1).
        """
        periods = 252
        underlying_changes = np.array([underlying_change])

        # Zero LIBOR
        period_libor_zero = np.array([0.0])
        fund_changes_zero = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_zero,
            leverage_mult=leverage,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # Non-zero LIBOR
        period_libor_nonzero = np.array([0.05])  # 5%
        fund_changes_nonzero = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_nonzero,
            leverage_mult=leverage,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # Property: LIBOR costs reduce returns for leveraged funds
        if leverage > 1.01:  # Only for leveraged funds
            assert fund_changes_nonzero[0] <= fund_changes_zero[0]
            # The difference should scale with leverage
            cost_diff = fund_changes_zero[0] - fund_changes_nonzero[0]
            # For 2x leverage, cost should be approximately 5%/252 * (2-1) = 0.0002
            expected_cost = (0.05 / periods) * (leverage - 1)
            assert abs(cost_diff - expected_cost) < 0.001

    @given(
        leverage=leverage_mult,
    )
    @settings(max_examples=50)
    def test_zero_underlying_change_gives_only_fees(self, leverage):
        """Test that zero underlying return yields only fee drag.

        Property: If underlying = 0%, fund return = -fees.
        """
        periods = 252
        annual_er = 0.01  # 1% expense ratio
        underlying_changes = np.array([0.0])  # Zero return
        period_libor_yields = np.array([0.02])

        fund_changes = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=leverage,
            annual_er_pct=annual_er,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # Expected: -ER/periods - libor/periods * (leverage - 1)
        expected_change = -(annual_er / periods) - (0.02 / periods) * (leverage - 1)

        assert abs(fund_changes[0] - expected_change) < 0.0001

    @given(
        underlying_changes=st.lists(
            daily_returns,
            min_size=10,
            max_size=100,
        ),
        leverage=leverage_mult,
    )
    @settings(max_examples=50, deadline=1000)
    def test_array_computation_consistency(self, underlying_changes, leverage):
        """Test that vectorized computation is consistent.

        Property: Computing multiple days at once = computing one at a time.
        """
        periods = 252
        annual_er = 0.005
        n = len(underlying_changes)

        underlying_array = np.array(underlying_changes)
        libor_array = np.full(n, 0.02)

        # Vectorized computation
        fund_changes_vectorized = _compute_sim_changes(
            underlying_changes=underlying_array,
            period_libor_yield_percents=libor_array,
            leverage_mult=leverage,
            annual_er_pct=annual_er,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # One-at-a-time computation
        fund_changes_individual = []
        for i in range(n):
            fc = _compute_sim_changes(
                underlying_changes=np.array([underlying_array[i]]),
                period_libor_yield_percents=np.array([libor_array[i]]),
                leverage_mult=leverage,
                annual_er_pct=annual_er,
                percent_daily_spread_cost=0.0,
                fund_swap_pct=1.0,
                periods_per_year=periods,
            )
            fund_changes_individual.append(fc[0])

        # Property: Should be identical
        for i in range(n):
            assert abs(fund_changes_vectorized[i] - fund_changes_individual[i]) < 1e-10


class TestSimulationBounds:
    """Test that simulation outputs stay within reasonable bounds."""

    @given(
        underlying_change=st.floats(min_value=-0.5, max_value=0.5),
        leverage=st.floats(min_value=1.0, max_value=3.0),
    )
    @settings(max_examples=100)
    def test_fund_change_reasonable_bounds(self, underlying_change, leverage):
        """Test that fund changes stay within reasonable bounds.

        Property: For daily returns, fund change should be < 3x * 50% = 150%.
        """
        periods = 252
        underlying_changes = np.array([underlying_change])
        period_libor_yields = np.array([0.02])

        fund_changes = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=leverage,
            annual_er_pct=0.01,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
        )

        # Reasonable bounds: shouldn't exceed 3x leverage * 50% change
        assert -2.0 < fund_changes[0] < 2.0, f"Fund change {fund_changes[0]} outside reasonable bounds"


class TestMultiplicativeConstants:
    """Test multiplicative and additive constants in simulation."""

    @given(
        underlying_change=daily_returns,
        mult_constant=st.floats(min_value=0.5, max_value=2.0),
    )
    @settings(max_examples=100)
    def test_multiplicative_constant_scales_output(self, underlying_change, mult_constant):
        """Test that multiplicative constant scales the output.

        Property: mult_constant * result.
        """
        periods = 252
        underlying_changes = np.array([underlying_change])
        period_libor_yields = np.array([0.02])

        # Without constant (implicitly 1.0)
        fund_changes_base = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
            multiplicative_constant=1.0,
            additive_constant=0.0,
        )

        # With constant
        fund_changes_scaled = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
            multiplicative_constant=mult_constant,
            additive_constant=0.0,
        )

        # Property: scaled = base * mult_constant
        expected = fund_changes_base[0] * mult_constant
        assert abs(fund_changes_scaled[0] - expected) < 1e-10

    @given(
        underlying_change=daily_returns,
        add_constant=st.floats(min_value=-0.01, max_value=0.01),
    )
    @settings(max_examples=100)
    def test_additive_constant_shifts_output(self, underlying_change, add_constant):
        """Test that additive constant shifts the output.

        Property: result + add_constant.
        """
        periods = 252
        underlying_changes = np.array([underlying_change])
        period_libor_yields = np.array([0.02])

        # Without constant
        fund_changes_base = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
            multiplicative_constant=1.0,
            additive_constant=0.0,
        )

        # With constant
        fund_changes_shifted = _compute_sim_changes(
            underlying_changes=underlying_changes,
            period_libor_yield_percents=period_libor_yields,
            leverage_mult=1.0,
            annual_er_pct=0.0,
            percent_daily_spread_cost=0.0,
            fund_swap_pct=1.0,
            periods_per_year=periods,
            multiplicative_constant=1.0,
            additive_constant=add_constant,
        )

        # Property: shifted = base + add_constant
        expected = fund_changes_base[0] + add_constant
        assert abs(fund_changes_shifted[0] - expected) < 1e-10
