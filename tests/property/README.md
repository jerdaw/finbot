# Property-Based Tests

This directory contains property-based tests using [Hypothesis](https://hypothesis.readthedocs.io/), a Python library for generative testing.

## What is Property-Based Testing?

Instead of writing specific test cases with hardcoded values, property-based testing defines **properties** (invariants) that should always hold true, and Hypothesis automatically generates hundreds of test cases to verify those properties.

**Traditional Test:**
```python
def test_pct_change():
    assert get_pct_change(100, 150) == 0.5  # 50% increase
```

**Property-Based Test:**
```python
@given(old=prices, new=prices)
def test_pct_change_reversibility(old, new):
    pct = get_pct_change(old, new)
    calculated_new = old * (1 + pct)
    assert abs(calculated_new - new) < 0.01
```

The property-based version tests **reversibility** with hundreds of randomly generated price pairs, catching edge cases we might not think of.

## Benefits

1. **Edge Case Discovery**: Hypothesis finds unusual inputs that break assumptions
2. **Mathematical Rigor**: Properties prove correctness beyond specific examples
3. **Regression Prevention**: Random testing catches subtle bugs
4. **Living Documentation**: Properties document mathematical invariants
5. **High Coverage**: Hundreds of examples per test

## Running Property Tests

```bash
# Run all property tests
uv run pytest tests/property/ -v

# Run with statistics
uv run pytest tests/property/ -v --hypothesis-show-statistics

# Run specific test file
uv run pytest tests/property/test_finance_properties.py -v

# Run with more examples (slower, more thorough)
uv run pytest tests/property/ -v --hypothesis-max-examples=1000
```

## Test Organization

### `conftest.py`
Shared Hypothesis strategies for generating test data:
- `prices` - Realistic stock/fund prices ($0.01 to $10,000)
- `daily_returns` - Daily return percentages (-20% to +20%)
- `pct_changes` - General percentage changes (-99% to +1000%)
- `leverage_mult` - Leverage multipliers (1x to 3x)
- `trading_periods` - Trading days (1 to 2,520 days)
- `price_series_strategy()` - Generate price time series
- `returns_series_strategy()` - Generate returns time series

### `test_finance_properties.py`
Properties for finance utility functions:
- Compound growth rate (CGR) properties
- Percentage change properties
- Drawdown properties
- Risk metrics properties

### `test_simulation_properties.py`
Properties for simulation functions:
- Fund simulator leverage amplification
- Fee and expense ratio impact
- LIBOR cost relationships
- Boundary conditions

### `test_data_science_properties.py`
Properties for data processing utilities:
- Normalization reversibility
- Scaling range preservation
- Imputation bounds

## Common Properties Tested

### 1. Reversibility
If you apply a function and then its inverse, you get back the original value:
```python
assert inverse(f(x)) ≈ x
```

### 2. Monotonicity
If input increases, output increases (or stays same):
```python
if x < y: assert f(x) <= f(y)
```

### 3. Bounds
Results stay within expected ranges:
```python
assert min_value <= f(x) <= max_value
```

### 4. Identity
Special inputs produce predictable outputs:
```python
assert f(0) == 0
assert f(1) == 1
```

### 5. Commutativity
Order doesn't matter:
```python
assert f(x, y) == f(y, x)
```

### 6. Associativity
Grouping doesn't matter:
```python
assert f(f(x, y), z) == f(x, f(y, z))
```

## Example Properties

### CGR Reversibility
```python
@given(start=prices, end=prices, years=years)
def test_cgr_reversibility(start, end, years):
    """Applying CGR to start value should yield end value."""
    cgr = get_cgr(start, end, years)
    calculated_end = start * (1 + cgr) ** years
    # Allow small floating-point error
    assert abs(calculated_end - end) / end < 0.001
```

### Percentage Change Bounds
```python
@given(old=prices, new=prices)
def test_pct_change_bounds(old, new):
    """Percentage change should have reasonable bounds."""
    pct = get_pct_change(old, new)
    # Can't lose more than 100%
    assert pct > -1.0
    # If new > old, change should be positive
    if new > old:
        assert pct > 0
```

### Leverage Amplification
```python
@given(leverage=leverage_mult, change=daily_returns)
def test_leverage_amplifies_returns(leverage, change):
    """Leveraged fund should amplify underlying returns."""
    # Simplified: ignoring fees
    fund_change = change * leverage
    assert abs(fund_change) > abs(change) or leverage == 1.0
```

## Writing New Property Tests

1. **Identify the property**: What mathematical invariant should hold?
2. **Choose strategies**: Use strategies from `conftest.py` or create new ones
3. **Write the test**: Use `@given` decorator with strategies
4. **Add tolerance**: Use `abs(x - y) < epsilon` for floating-point comparisons
5. **Document**: Explain what property is being tested

### Template
```python
from hypothesis import given
from tests.property.conftest import prices, years

@given(x=prices, y=years)
def test_my_property(x, y):
    """Brief description of what property is tested."""
    result = my_function(x, y)

    # Assert the property
    assert some_invariant_about(result)

    # Or check relationships
    assert result > 0  # Non-negativity
    assert result < x * y  # Upper bound
```

## Debugging Failing Properties

When Hypothesis finds a failing case, it will:
1. Print the failing example
2. Try to **shrink** it to a minimal failing case
3. Save it in `.hypothesis/` for replay

```bash
# Example output
Falsifying example: test_cgr_reversibility(
    start=1.0,
    end=0.01,
    years=100.0,
)
```

To debug:
1. Run the specific failing example manually
2. Add `print()` statements to understand what's happening
3. Adjust the property or function to handle the edge case
4. Verify the fix with `pytest tests/property/ -v`

## Configuration

Hypothesis settings can be configured per-test or globally:

```python
from hypothesis import settings, Phase

@settings(
    max_examples=500,  # Run more examples
    deadline=None,  # No time limit per example
    phases=[Phase.generate],  # Skip shrinking (faster)
)
@given(x=prices)
def test_expensive_property(x):
    # ...
```

## Markers

Property tests can be marked for selective execution:

```bash
# Run only fast property tests
pytest tests/property/ -m "not slow"

# Run all including slow
pytest tests/property/
```

## See Also

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Guide](https://increment.com/testing/in-praise-of-property-based-testing/)
- [Hypothesis Strategies Reference](https://hypothesis.readthedocs.io/en/latest/data.html)
