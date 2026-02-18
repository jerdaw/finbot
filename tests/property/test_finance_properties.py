"""Property-based tests for finance utility functions.

Tests mathematical properties and invariants of financial calculations
using Hypothesis for generative testing.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from finbot.utils.finance_utils.get_cgr import get_cgr
from finbot.utils.finance_utils.get_pct_change import get_pct_change
from tests.property.conftest import pct_changes, prices, small_prices, years


class TestCGRProperties:
    """Property tests for compound growth rate (CGR) calculation."""

    @given(start=small_prices, end=small_prices, years_=years)
    @settings(max_examples=200)
    def test_cgr_reversibility(self, start, end, years_):
        """Test that CGR calculation is reversible.

        Property: Applying CGR to start value for N years should yield end value.
        """
        # Skip cases where ratio is extreme (numerical instability)
        assume(0.001 < end / start < 1000)
        assume(years_ > 0.1)  # Avoid very small time periods (numerical precision issues)
        # Exclude extreme-ratio + short-period combinations: computing (near-zero)^fraction
        # causes catastrophic floating-point cancellation (e.g. 99% drop in 0.125 years)
        assume(not (end / start < 0.1 and years_ < 0.25))

        cgr = get_cgr(start, end, years_)

        # Apply CGR to start value
        calculated_end = start * (1 + cgr) ** years_

        # Check reversibility (allow small floating-point error)
        relative_error = abs(calculated_end - end) / end
        assert relative_error < 0.01, f"CGR reversibility failed: {relative_error}"

    @given(value=small_prices, years_=years)
    @settings(max_examples=100)
    def test_cgr_identity_no_growth(self, value, years_):
        """Test that zero growth (start == end) gives CGR of 0.

        Property: CGR(x, x, t) = 0 for any x and t.
        """
        assume(years_ > 0.1)  # Avoid very small time periods (numerical precision issues)

        cgr = get_cgr(value, value, years_)

        assert abs(cgr) < 0.0001, f"Expected CGR ≈ 0, got {cgr}"

    @given(start=small_prices, factor=st.floats(min_value=1.01, max_value=3.0), years_=years)
    @settings(max_examples=100)
    def test_cgr_positive_for_growth(self, start, factor, years_):
        """Test that CGR is positive when end > start.

        Property: If end > start, then CGR > 0.
        """
        assume(years_ > 0.1)  # Avoid very small time periods (numerical precision issues)
        end = start * factor

        cgr = get_cgr(start, end, years_)

        assert cgr > 0, f"Expected positive CGR for growth, got {cgr}"

    @given(start=small_prices, factor=st.floats(min_value=0.1, max_value=0.99), years_=years)
    @settings(max_examples=100)
    def test_cgr_negative_for_decline(self, start, factor, years_):
        """Test that CGR is negative when end < start.

        Property: If end < start, then CGR < 0.
        """
        assume(years_ > 0.1)  # Avoid very small time periods (numerical precision issues)
        end = start * factor

        cgr = get_cgr(start, end, years_)

        assert cgr < 0, f"Expected negative CGR for decline, got {cgr}"


class TestPctChangeProperties:
    """Property tests for percentage change calculation."""

    @given(old=prices, new=prices)
    @settings(max_examples=200)
    def test_pct_change_reversibility(self, old, new):
        """Test that percentage change is reversible.

        Property: old * (1 + pct_change) = new.
        """
        # Skip extreme ratios that cause numerical issues
        assume(0.001 < new / old < 1000)

        pct = get_pct_change(old, new)

        # Apply percentage change to old value
        calculated_new = old * (1 + pct)

        # Check reversibility
        relative_error = abs(calculated_new - new) / new
        assert relative_error < 0.001, f"Pct change reversibility failed: {relative_error}"

    @given(value=prices)
    @settings(max_examples=100)
    def test_pct_change_identity_zero(self, value):
        """Test that no change (old == new) gives 0% change.

        Property: pct_change(x, x) = 0.
        """
        pct = get_pct_change(value, value)

        assert abs(pct) < 0.0001, f"Expected 0% change, got {pct}"

    @given(old=prices, new=prices)
    @settings(max_examples=200)
    def test_pct_change_sign_matches_direction(self, old, new):
        """Test that sign of pct change matches direction of change.

        Property: If new > old, pct > 0; if new < old, pct < 0.
        """
        # Skip cases that are too close (floating-point equality)
        assume(abs(new - old) / old > 0.001)

        pct = get_pct_change(old, new)

        if new > old:
            assert pct > 0, f"Expected positive change, got {pct}"
        elif new < old:
            assert pct < 0, f"Expected negative change, got {pct}"

    @given(old=prices, new=prices)
    @settings(max_examples=100)
    def test_pct_change_bounds(self, old, new):
        """Test that percentage change has reasonable bounds.

        Property: pct_change > -1.0 (can't lose more than 100%).
        """
        pct = get_pct_change(old, new)

        # Can't lose more than 100%
        assert pct >= -1.0, f"Percentage change {pct} < -100%"

    @given(value=prices, pct=pct_changes)
    @settings(max_examples=200)
    def test_pct_change_inverse_relationship(self, value, pct):
        """Test inverse relationship between forward and reverse changes.

        Property: If going from A to B is +X%, then going from B to A is roughly -X/(1+X) %.
        """
        # Skip extreme values
        assume(pct > -0.99)  # Avoid near-total loss
        assume(abs(pct) < 5.0)  # Avoid extreme gains

        new_value = value * (1 + pct)
        pct_back = get_pct_change(new_value, value)

        # The relationship: pct_back ≈ -pct / (1 + pct)
        expected_pct_back = -pct / (1 + pct)

        assert abs(pct_back - expected_pct_back) < 0.01, (
            f"Inverse pct failed: {pct_back} vs expected {expected_pct_back}"
        )


class TestDrawdownProperties:
    """Property tests for drawdown calculation."""

    @pytest.mark.skip(reason="Drawdown function location needs verification")
    @given(prices_list=st.lists(prices, min_size=10, max_size=100))
    def test_drawdown_non_positive(self, prices_list):
        """Test that drawdown is always non-positive.

        Property: Drawdown ≤ 0 (it's a loss measure).
        """
        # This is a placeholder - actual implementation depends on
        # the specific drawdown function signature
        pass


class TestFinancialInvariants:
    """General financial calculation invariants."""

    @given(
        price=small_prices,
        pct1=st.floats(min_value=-0.5, max_value=1.0),
        pct2=st.floats(min_value=-0.5, max_value=1.0),
    )
    @settings(max_examples=150)
    def test_compound_returns_commutativity(self, price, pct1, pct2):
        """Test that order of returns affects final value (NOT commutative).

        Property: price * (1+r1) * (1+r2) = price * (1+r2) * (1+r1)
        Returns ARE commutative for multiplication.
        """
        # Apply returns in order 1-2
        result_12 = price * (1 + pct1) * (1 + pct2)

        # Apply returns in order 2-1
        result_21 = price * (1 + pct2) * (1 + pct1)

        # Multiplication is commutative
        assert abs(result_12 - result_21) < 0.01

    @given(
        start=small_prices,
        r1=st.floats(min_value=-0.3, max_value=0.5),
        r2=st.floats(min_value=-0.3, max_value=0.5),
    )
    @settings(max_examples=100)
    def test_compounding_vs_simple_returns(self, start, r1, r2):
        """Test relationship between compound and arithmetic average returns.

        Property: Compound return ≠ sum of returns (due to compounding).
        """
        # Skip cases where returns are near zero
        assume(abs(r1) > 0.01 or abs(r2) > 0.01)
        # Skip cases where returns are too similar (geometric ≈ arithmetic)
        assume(abs(r1 - r2) > 0.02)

        # Compound returns
        final = start * (1 + r1) * (1 + r2)
        _ = (final - start) / start

        # Simple arithmetic average
        simple_avg = (r1 + r2) / 2

        # For non-zero returns, compound ≠ arithmetic average
        # (This property documents that compounding matters)
        if r1 != 0 and r2 != 0:
            # The geometric mean is different from arithmetic mean
            geometric_factor = np.sqrt((1 + r1) * (1 + r2))
            arithmetic_factor = 1 + simple_avg

            # They should be different (returns are sufficiently different due to assume)
            assert abs(geometric_factor - arithmetic_factor) > 0.00001

    @given(value=prices, multiplier=st.floats(min_value=0.5, max_value=2.0))
    @settings(max_examples=100)
    def test_percentage_change_scales_linearly(self, value, multiplier):
        """Test that percentage change is scale-invariant.

        Property: pct_change(k*x, k*y) = pct_change(x, y) for any k > 0.
        """
        new_value = value * 1.5  # Some arbitrary new value

        pct1 = get_pct_change(value, new_value)
        pct2 = get_pct_change(value * multiplier, new_value * multiplier)

        # Percentage change should be the same regardless of scale
        assert abs(pct1 - pct2) < 0.001, f"Scale invariance failed: {pct1} vs {pct2}"
