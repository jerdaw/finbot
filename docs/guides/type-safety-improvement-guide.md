# Type Safety Improvement Guide

**Created:** 2026-02-10
**Status:** Active
**Purpose:** Guide gradual improvement of type safety across the finbot codebase

---

## Current State

**Mypy Configuration:** Stricter settings enabled as of 2026-02-10
- `check_untyped_defs = true` - Check function bodies even without type hints
- `warn_redundant_casts = true` - Warn about unnecessary type casts
- `warn_unused_ignores = true` - Warn about unused `# type: ignore` comments
- `warn_unreachable = true` - Warn about unreachable code
- `no_implicit_optional = true` - Don't treat `None` default as `Optional`
- `strict_optional = true` - Strict checking of `Optional` types

**Current Errors:** 125 errors in 41 files (out of 243 source files checked)

**Type Stubs Installed:**
- ✅ `types-psutil` - psutil type stubs
- ✅ `types-python-dateutil` - python-dateutil type stubs
- ✅ `types-requests` - requests type stubs
- ✅ `pandas-stubs` - pandas type stubs
- ✅ `types-tqdm` - tqdm type stubs
- ✅ `types-beautifulsoup4` - beautifulsoup4 type stubs
- ✅ `google-api-python-client-stubs` - Google API client type stubs
- ✅ `types-seaborn` - seaborn type stubs

**Third-Party Overrides** (ignore missing imports for libraries without stubs):
- sklearn, scipy, statsmodels, yfinance, pandas_datareader, backtrader, plotly

---

## Error Categories

### Category 1: Missing Type Annotations (Priority: Medium)
**Count:** ~30 errors
**Example:** `Need type annotation for "as_dict"`, `Need type annotation for "new_columns_order"`

**Fix Approach:**
```python
# Before
my_dict = {}

# After
my_dict: dict[str, list] = {}
```

**Files to prioritize:**
- Public API functions in `finbot/services/`
- Utility functions in `finbot/utils/finance_utils/`
- Core simulation logic in `finbot/services/simulation/`

### Category 2: Backtrader Type Issues (Priority: Low)
**Count:** ~20 errors
**Example:** `"tuple[str]" has no attribute "returns"`, `"None" has no attribute "addstrategy"`

**Root Cause:** Backtrader library has no type stubs and uses dynamic attribute access

**Fix Approach:**
- Add `# type: ignore[attr-defined]` comments for Backtrader-specific code
- Consider creating stub file for common Backtrader classes in `typings/backtrader/`
- Not urgent since Backtrader code is well-tested

### Category 3: Pandas Type Inference Issues (Priority: Low)
**Count:** ~25 errors
**Example:** `No overload variant of "__setitem__" of "Series" matches argument types`, `Invalid index type`

**Root Cause:** pandas-stubs is overly strict about type inference

**Fix Approach:**
- Use `# type: ignore[call-overload]` for known-safe pandas operations
- Cast types explicitly when needed: `cast(pd.Series[float], series)`
- Not critical since pandas operations are well-tested

### Category 4: Optional Type Issues (Priority: High)
**Count:** ~15 errors
**Example:** `No overload variant of "max" matches argument types "Timestamp", "None"`

**Root Cause:** `no_implicit_optional = true` now enforces explicit `Optional` handling

**Fix Approach:**
```python
# Before
def func(start: pd.Timestamp, end: pd.Timestamp = None):
    return max(start, end)  # Error!

# After - Option 1: Make Optional explicit
def func(start: pd.Timestamp, end: pd.Timestamp | None = None):
    if end is None:
        return start
    return max(start, end)

# After - Option 2: Use default
def func(start: pd.Timestamp, end: pd.Timestamp | None = None):
    return max(start, end or start)
```

**Files to prioritize:**
- `finbot/services/backtesting/backtest_runner.py` (10+ errors)
- Date handling utilities in `finbot/utils/datetime_utils/`

### Category 5: Return Type Mismatches (Priority: Medium)
**Count:** ~20 errors
**Example:** `Incompatible return value type`, `Incompatible types in assignment`

**Fix Approach:**
- Add explicit return type annotations
- Fix type inconsistencies in function logic
- Use `cast()` when type is known but mypy can't infer it

### Category 6: CLI Type Issues (Priority: High - Bugs)
**Count:** ~5 errors
**Example:** `Module has no attribute "DCAOptimizer"`, `Unexpected keyword argument`

**Root Cause:** CLI was recently added and hasn't been fully tested

**Fix Approach:**
- Fix import errors in CLI commands
- Align CLI with actual function signatures
- Add CLI integration tests

---

## Gradual Improvement Strategy

### Phase 1: Fix Bugs and High-Priority Issues (1-2 hours)
Focus on errors that indicate actual bugs or will cause runtime failures:

1. **Fix CLI integration issues** (Priority: Urgent)
   - `finbot/cli/commands/optimize.py` - Fix `DCAOptimizer` import
   - `finbot/cli/commands/backtest.py` - Fix `compute_stats` signature mismatch
   - Add basic CLI smoke tests

2. **Fix Optional type issues in core logic** (Priority: High)
   - `finbot/services/backtesting/backtest_runner.py` - Fix `start`/`end`/`duration` Optional handling
   - `finbot/utils/datetime_utils/` - Fix date comparison with None

3. **Add missing type annotations to public APIs** (Priority: High)
   - `finbot/services/simulation/fund_simulator.py`
   - `finbot/services/optimization/dca_optimizer.py` (partially done)
   - `finbot/services/backtesting/compute_stats.py`

### Phase 2: Improve Core Services (2-3 hours)
Focus on services layer where type safety has highest impact:

1. Add type annotations to all public functions in:
   - `finbot/services/simulation/` (fund_simulator, bond_ladder, monte_carlo)
   - `finbot/services/backtesting/` (strategies, runners, analyzers)
   - `finbot/services/optimization/` (dca_optimizer, rebalance_optimizer)

2. Fix return type mismatches in:
   - `finbot/utils/finance_utils/get_periods_per_year.py`
   - `finbot/services/backtesting/avg_stepped_results.py`
   - `finbot/utils/data_science_utils/` (scalers, imputation)

### Phase 3: Utility Layer (3-4 hours)
Gradual improvement as utilities are touched:

1. Add type annotations to finance utilities:
   - `finbot/utils/finance_utils/` (20 files)
   - Focus on: get_cgr, get_drawdown, get_risk_free_rate, merge_price_histories

2. Add type annotations to pandas utilities:
   - `finbot/utils/pandas_utils/` (30 files)
   - Focus on: save_dataframe, load_dataframe, filter_by_date

3. Add type annotations to datetime utilities:
   - `finbot/utils/datetime_utils/` (25 files)
   - Focus on: get_us_business_dates, get_duration, validate_start_end_dates

### Phase 4: Suppress Known-Safe Errors (1 hour)
Add `# type: ignore` comments for errors that are known-safe:

1. **Backtrader dynamic attributes** - Add `# type: ignore[attr-defined]`
2. **Pandas type inference** - Add `# type: ignore[call-overload]` for known-safe operations
3. **Data science utilities** - Add `# type: ignore[assignment]` for sklearn-style APIs

### Phase 5: Advanced Type Safety (Future)
More advanced improvements for long-term maintainability:

1. Enable stricter settings:
   - `disallow_untyped_defs = true` (require type hints on all functions)
   - `disallow_any_generics = true` (require explicit generic types)
   - `warn_return_any = true` (warn when function returns Any)

2. Create custom type stubs:
   - `typings/backtrader/` - Stub file for Backtrader classes
   - `typings/quantstats/` - Stub file for quantstats if needed

3. Add generic types where beneficial:
   - `TypeVar` for generic collection functions
   - `Protocol` for duck-typed interfaces
   - `Literal` for string literal types

---

## Best Practices

### When Adding Type Hints

1. **Start with return types** - Most valuable for understanding function behavior
   ```python
   def get_cgr(start_value: float, end_value: float, n_periods: float) -> float:
   ```

2. **Use `from __future__ import annotations`** - Enables forward references and cleaner syntax
   ```python
   from __future__ import annotations

   def process(data: pd.DataFrame) -> pd.Series:  # No quotes needed
   ```

3. **Use union types with `|`** - Python 3.10+ syntax (we target 3.11+)
   ```python
   def func(data: pd.Series | pd.DataFrame | None = None) -> float | None:
   ```

4. **Be explicit about Optional** - Don't rely on None default
   ```python
   # Good
   def func(start: pd.Timestamp | None = None) -> None:

   # Bad (no_implicit_optional will catch this)
   def func(start: pd.Timestamp = None) -> None:
   ```

5. **Use generic types for collections**
   ```python
   # Good
   def process(items: list[str]) -> dict[str, int]:

   # Bad
   def process(items: list) -> dict:
   ```

### When to Use `# type: ignore`

Use `# type: ignore` sparingly and only when:
1. The error is a false positive (mypy/stub limitation)
2. The code is known-safe through testing
3. Fixing it would require significant refactoring

Always add a comment explaining why:
```python
# type: ignore[attr-defined]  # Backtrader uses dynamic attribute access
```

### CI Integration

Current CI runs mypy on every push. As errors are fixed:
1. Track progress: "Fixed 10 type errors in finance_utils"
2. Don't introduce new errors in modified files
3. Eventually add `--strict` flag to mypy in CI

---

## Progress Tracking

**Baseline (2026-02-10):** 125 errors in 41 files

**Goal:** Reduce to <50 errors in 6 months, <20 errors in 12 months

**Update this section as progress is made:**

| Date | Errors | Files | Notes |
|------|--------|-------|-------|
| 2026-02-10 | 125 | 41 | Initial baseline after adding strict config |
| TBD | TBD | TBD | After Phase 1 fixes |

---

## References

- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 604 - Union Operator](https://www.python.org/dev/peps/pep-0604/)
- [pandas-stubs Issues](https://github.com/pandas-dev/pandas-stubs/issues)
- [Backtrader Documentation](https://www.backtrader.com/docu/)
