# Property-Based Testing with Hypothesis - Implementation Plan

**Item:** Priority 5, Item 30
**Status:** ✅ Complete
**Date Started:** 2026-02-17
**Date Completed:** 2026-02-17
**Completion Summary:** `docs/planning/hypothesis-testing-completion-summary.md`

## Overview

Add property-based testing using Hypothesis to test mathematical properties and edge cases of financial calculations, simulations, and utility functions.

## What is Property-Based Testing?

Instead of writing specific test cases, you define properties that should always hold true, and Hypothesis generates hundreds of test cases to try to break those properties.

**Example:**
```python
# Traditional test
def test_cgr():
    assert get_cgr(100, 200, 1) == 1.0  # 100% growth

# Property-based test
@given(start=floats(min_value=0.01), end=floats(min_value=0.01), years=floats(min_value=0.01))
def test_cgr_properties(start, end, years):
    cgr = get_cgr(start, end, years)
    # Property: Reversing CGR should get back to start
    assert abs(start * (1 + cgr) ** years - end) < 0.01
```

## Target Modules for Property Testing

### 1. Finance Utilities (High Priority)
- **`get_cgr.py`** - Compound growth rate
  - Properties: Reversibility, monotonicity, bounds checking
- **`get_pct_change.py`** - Percentage change
  - Properties: Commutativity, bounds, zero handling
- **`get_drawdown.py`** - Drawdown calculation
  - Properties: Non-positive values, monotonic decrease
- **`get_risk_free_rate.py`** - Risk-free rate interpolation
  - Properties: Within bounds, date ordering

### 2. Fund Simulator (High Priority)
- **`fund_simulator.py`** - Leveraged fund simulation
  - Properties: Leverage amplification, fee impact, monotonicity
- **`_compute_sim_changes()`** - Daily percent changes
  - Properties: Bounds checking, leverage relationships

### 3. Math/Statistics Utilities (Medium Priority)
- **`data_science_utils/`** - Normalization, scaling
  - Properties: Reversibility, range preservation
- **Pandas utilities** - Date operations, filtering
  - Properties: Order preservation, no data loss

### 4. Backtest Calculations (Medium Priority)
- **Performance metrics** - Sharpe, Sortino, drawdown
  - Properties: Statistical properties, bounds

## Implementation Strategy

### Phase 1: Setup (30 min)
1. Add hypothesis to dev dependencies in `pyproject.toml`
2. Create `tests/property/` directory
3. Create `tests/property/conftest.py` with shared strategies
4. Document property testing approach in `tests/property/README.md`

### Phase 2: Finance Utilities (2-3 hours)
1. Create `tests/property/test_finance_properties.py`
2. Add property tests for:
   - `get_cgr` - Compound growth rate properties
   - `get_pct_change` - Percentage change properties
   - `get_drawdown` - Drawdown properties
3. Run tests with `pytest tests/property/ -v`

### Phase 3: Fund Simulator (2-3 hours)
1. Create `tests/property/test_simulation_properties.py`
2. Add property tests for:
   - Leverage amplification
   - Fee impact
   - LIBOR cost relationships
   - Boundary conditions
3. Verify with large datasets

### Phase 4: Data Science Utilities (1-2 hours)
1. Create `tests/property/test_data_science_properties.py`
2. Add property tests for:
   - Normalization reversibility
   - Scaling properties
   - Imputation bounds

### Phase 5: Documentation (30 min)
1. Update roadmap.md to mark complete
2. Create completion summary
3. Add property testing guide to docs

### Phase 6: Verification (30 min)
1. Run all property tests: `pytest tests/property/ -v`
2. Run with verbose output: `pytest tests/property/ -v --hypothesis-show-statistics`
3. Verify edge cases are being tested
4. Run full test suite to ensure no regressions

## Hypothesis Strategies to Use

### Custom Strategies
```python
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
from hypothesis.extra.pandas import data_frames, series

# Financial values (positive, reasonable range)
prices = st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False)

# Percentages (-100% to 1000%)
pct_changes = st.floats(min_value=-1.0, max_value=10.0, allow_nan=False)

# Time periods (positive integers)
periods = st.integers(min_value=1, max_value=1000)

# Leverage multipliers
leverage = st.floats(min_value=1.0, max_value=5.0)

# Dates (business days)
dates = st.dates(min_value=date(2000, 1, 1), max_value=date(2025, 12, 31))
```

## Properties to Test

### Finance Properties
1. **Reversibility**: `apply(inverse(x)) == x`
2. **Monotonicity**: `f(x) < f(y)` when `x < y`
3. **Bounds**: Results stay within expected ranges
4. **Identity**: `f(identity) == identity`
5. **Associativity**: `f(f(x, y), z) == f(x, f(y, z))`

### Simulation Properties
1. **Leverage amplification**: `2x leverage ≈ 2x daily changes`
2. **Fee impact**: Higher fees → lower returns
3. **Non-negativity**: Fund value ≥ 0 (until zero-value event)
4. **Expense ratio impact**: Higher ER → predictable drag

## Example Property Tests

### Example 1: CGR Reversibility
```python
from hypothesis import given
from hypothesis import strategies as st
from finbot.utils.finance_utils.get_cgr import get_cgr

@given(
    start=st.floats(min_value=0.01, max_value=10000, allow_nan=False),
    end=st.floats(min_value=0.01, max_value=10000, allow_nan=False),
    years=st.floats(min_value=0.01, max_value=100, allow_nan=False),
)
def test_cgr_reversibility(start, end, years):
    """Test that CGR calculation can be reversed."""
    cgr = get_cgr(start, end, years)
    # Apply CGR to start value for 'years' should give 'end'
    calculated_end = start * (1 + cgr) ** years
    assert abs(calculated_end - end) < 0.01 or abs(calculated_end - end) / end < 0.001
```

### Example 2: Percentage Change Bounds
```python
@given(
    old=st.floats(min_value=0.01, max_value=10000, allow_nan=False),
    new=st.floats(min_value=0.01, max_value=10000, allow_nan=False),
)
def test_pct_change_bounds(old, new):
    """Test that percentage change has reasonable bounds."""
    pct = get_pct_change(old, new)
    # Pct change should be > -100% (can't lose more than 100%)
    assert pct > -100
    # If new > old, pct should be positive
    if new > old:
        assert pct > 0
    # If new < old, pct should be negative
    if new < old:
        assert pct < 0
```

### Example 3: Fund Simulator Leverage
```python
@given(
    leverage=st.floats(min_value=1.0, max_value=3.0),
    underlying_change=st.floats(min_value=-0.1, max_value=0.1),
)
def test_leverage_amplification(leverage, underlying_change):
    """Test that leverage amplifies returns approximately correctly."""
    # Ignoring fees for this test
    fund_change = underlying_change * leverage

    # Fund change should be approximately leverage times underlying
    assert abs(fund_change - underlying_change * leverage) < 0.001
```

## Acceptance Criteria

- [ ] Hypothesis added to dev dependencies
- [ ] `tests/property/` directory created
- [ ] At least 15 property tests across 3 modules
- [ ] All property tests passing
- [ ] Tests run 100+ examples per property
- [ ] Documentation explains property testing approach
- [ ] No regressions in existing tests
- [ ] Property tests integrated into CI (optional)

## Estimated Timeline

- Phase 1 (Setup): 30 minutes
- Phase 2 (Finance): 2-3 hours
- Phase 3 (Simulation): 2-3 hours
- Phase 4 (Data Science): 1-2 hours
- Phase 5 (Documentation): 30 minutes
- Phase 6 (Verification): 30 minutes

**Total:** 7-10 hours (fits within 1-2 days estimate)

## Benefits

1. **Edge case coverage**: Hypothesis finds cases we wouldn't think of
2. **Mathematical rigor**: Properties prove correctness, not just specific examples
3. **Regression prevention**: Random testing catches changes that break properties
4. **Documentation**: Properties document mathematical invariants
5. **Confidence**: Hundreds of test cases per property

## Risks

1. **Flaky tests**: Random generation might cause occasional failures
   - Mitigation: Use deterministic examples, set random seed
2. **Slow tests**: Many examples might slow down test suite
   - Mitigation: Mark with `@pytest.mark.slow`, reduce example count in CI
3. **False positives**: Properties might be too strict
   - Mitigation: Add tolerance for floating-point comparisons

## Resources

- Hypothesis documentation: https://hypothesis.readthedocs.io/
- Property-based testing guide: https://increment.com/testing/in-praise-of-property-based-testing/
- Hypothesis strategies: https://hypothesis.readthedocs.io/en/latest/data.html
