# Stricter Mypy Settings Implementation Plan

**Roadmap Item:** Priority 5, Item 12
**Current mypy Configuration:** Basic type checking with `check_untyped_defs = false`
**Target:** Enable `disallow_untyped_defs = true` and other strict settings incrementally
**Status:** Not Started
**Date Created:** 2026-02-17

## Overview

Gradually enable stricter mypy settings to improve type safety across the codebase. This will catch more potential bugs at development time and improve code quality through better type annotations.

## Current mypy Configuration

From `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_calls = false
disallow_untyped_defs = false       # ← Currently disabled
disallow_incomplete_defs = false    # ← Currently disabled
check_untyped_defs = false          # ← Currently disabled
disallow_untyped_decorators = false # ← Currently disabled
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

**Known Issues:**
- 37 type errors currently exist (tracked separately from exclusions)
- 0 internal module exclusions (recently fixed in Item 34)
- Only `nautilus_trader` has `ignore_errors = true` (third-party library)

## Strategy: Incremental Strictness

We'll enable strict settings one at a time, module by module, to avoid overwhelming error counts.

### Phase 1: Module-by-Module Annotation Audit
**Duration:** 2-3 days
**Goal:** Identify which modules are already well-typed and which need work

1. **Audit current type coverage**
   - Run `mypy --strict finbot/` to see baseline errors
   - Categorize modules by error count:
     - ✅ Already strict-compliant (0 errors)
     - 🟡 Fixable (1-5 errors)
     - 🔴 Needs work (6+ errors)

2. **Create type coverage map**
   - Document in this plan which modules are ready for strict mode
   - Identify common patterns of missing annotations

### Phase 2: Enable `check_untyped_defs` ✅ ALREADY COMPLETE
**Duration:** Already done
**Goal:** Check existing type hints for consistency without requiring new ones
**Status:** ✅ Complete (already enabled in pyproject.toml line 235)

**Current configuration:**
```toml
check_untyped_defs = true  # ✅ Already enabled
```

This setting is already active and has been validating existing type hints for correctness.
No additional work needed for this phase.

### Phase 3: Annotate Well-Isolated Modules
**Duration:** 3-4 days
**Goal:** Add type annotations to modules that are easy wins

Target modules (likely candidates based on structure):
- `finbot/core/contracts/` (already has many type hints)
- `finbot/constants/` (simple constant definitions)
- `finbot/exceptions.py` (simple exception classes)
- `finbot/utils/dict_utils/` (small utility modules)
- `finbot/utils/json_utils/` (small utility modules)

For each module:
1. Add type annotations to all function signatures
2. Add return type hints
3. Enable `disallow_untyped_defs` for that module only using inline config:
   ```python
   # mypy: disallow-untyped-defs
   ```
4. Run mypy and fix any errors
5. Run tests to ensure correctness

### Phase 4: Annotate Core Utilities
**Duration:** 3-5 days
**Goal:** Add annotations to high-value utility modules

Target modules:
- `finbot/utils/datetime_utils/` (high-value, well-tested)
- `finbot/utils/file_utils/` (high-value, well-tested)
- `finbot/utils/finance_utils/` (high-value, well-tested)
- `finbot/utils/pandas_utils/` (complex but important)
- `finbot/config/` (config layer)

Same process as Phase 3 for each module.

### Phase 5: Annotate Services
**Duration:** 4-6 days
**Goal:** Add annotations to service-layer modules

Target modules:
- `finbot/services/backtesting/` (critical backtesting engine)
- `finbot/services/simulation/` (fund/index simulators)
- `finbot/services/health_economics/` (health economics tools)
- `finbot/services/optimization/` (DCA/rebalance optimizers)
- `finbot/services/data_quality/` (data quality tools)

This phase is more complex due to:
- Interaction with Backtrader (third-party, poorly typed)
- Complex business logic
- pandas DataFrames (dynamic typing challenges)

### Phase 6: Enable Global Strict Settings
**Duration:** 2-3 days
**Goal:** Enable strict settings globally in pyproject.toml

Once most modules are annotated:

1. **Enable disallow_untyped_defs globally:**
   ```toml
   disallow_untyped_defs = true
   ```

2. **Enable additional strict settings:**
   ```toml
   disallow_incomplete_defs = true
   disallow_untyped_calls = true
   disallow_untyped_decorators = true
   ```

3. **Add per-module exclusions** for any remaining problem modules:
   ```toml
   [[tool.mypy.overrides]]
   module = "finbot.dashboard.*"
   disallow_untyped_defs = false
   ```

4. **Document excluded modules** with issue tracking for future fixes

### Phase 7: Final Cleanup
**Duration:** 1-2 days
**Goal:** Polish and documentation

1. **Fix any remaining `# type: ignore` comments**
   - Add explanations for any that remain
   - File issues for future cleanup

2. **Update documentation:**
   - Add type checking guidelines to CONTRIBUTING.md
   - Document common typing patterns in docs/guides/

3. **Update CI configuration:**
   - Ensure CI runs with strict mypy settings
   - Add mypy coverage reporting if available

## Estimated Timeline

| Phase | Duration | Cumulative Time |
|-------|----------|-----------------|
| Phase 1: Audit | 2-3 days | 2-3 days |
| Phase 2: check_untyped_defs | 1-2 days | 3-5 days |
| Phase 3: Well-isolated modules | 3-4 days | 6-9 days |
| Phase 4: Core utilities | 3-5 days | 9-14 days |
| Phase 5: Services | 4-6 days | 13-20 days |
| Phase 6: Global strict | 2-3 days | 15-23 days |
| Phase 7: Cleanup | 1-2 days | 16-25 days |

**Total: 16-25 days** (roughly 3-5 weeks)

**Note:** Original estimate was "1-2 weeks" but this was optimistic. A more realistic incremental approach takes 3-5 weeks.

## Success Criteria

- [ ] Phase 1: Type coverage audit complete
- [ ] Phase 2: `check_untyped_defs = true` enabled globally
- [ ] Phase 3: Well-isolated modules fully annotated
- [ ] Phase 4: Core utilities fully annotated
- [ ] Phase 5: Service layer annotated (or excluded with tracking)
- [ ] Phase 6: `disallow_untyped_defs = true` enabled globally
- [ ] Phase 7: Documentation updated, CI passing
- [ ] All tests passing (no regressions)
- [ ] mypy errors reduced to <10 (excluding third-party libraries)

## Common Typing Patterns

### pandas DataFrames
```python
from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from pandas import DataFrame

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    ...
```

### Optional parameters
```python
from typing import Optional

def get_data(symbol: str, start_date: Optional[str] = None) -> pd.DataFrame:
    ...
```

### Union types
```python
from typing import Union
from pathlib import Path

def load_file(path: Union[str, Path]) -> str:
    ...
```

### Generic types
```python
from typing import Dict, List, Tuple

def get_mapping() -> Dict[str, List[int]]:
    ...
```

### Backtrader compatibility
```python
# Backtrader classes are poorly typed, use Any or Protocol
from typing import Any, Protocol

class BacktraderStrategy(Protocol):
    def __init__(self) -> None: ...
    def next(self) -> None: ...

def run_backtest(strategy: Any) -> Dict[str, float]:  # Use Any for BT objects
    ...
```

## Risks and Mitigations

### Risk 1: Overwhelming error count
**Mitigation:** Incremental phase-by-phase approach with per-module `# mypy: disallow-untyped-defs`

### Risk 2: Backtrader/third-party library issues
**Mitigation:** Use `# type: ignore` or `cast()` for third-party objects, document exclusions

### Risk 3: pandas DataFrame typing complexity
**Mitigation:** Use `pd.DataFrame` type hint without column-level typing (too complex for diminishing returns)

### Risk 4: Breaking existing functionality
**Mitigation:** Run full test suite after each module annotation, ensure all 866 tests pass

### Risk 5: Time overrun
**Mitigation:** Can pause after any phase and document progress. Partial progress still valuable.

## Deferred Considerations

- **Column-level DataFrame typing:** Too complex, diminishing returns (use `pandas-stubs` if needed later)
- **Protocol-based duck typing:** Defer to future refinement
- **Generics for container types:** Can add incrementally as modules are annotated
- **Type stubs for Backtrader:** Would require separate project, not worth effort

## Notes

- Existing 37 mypy errors (separate from exclusions) should be tracked and fixed in parallel
- Some modules may need exclusions permanently (dashboard, scrapers with complex HTML parsing)
- Type annotations improve IDE autocomplete and catch bugs early
- This is a quality investment that pays dividends in maintainability

## Files to Track

### New/Modified
- `pyproject.toml` (mypy config changes)
- Module files with added type annotations (100+ files estimated)
- `docs/guides/type-checking-guidelines.md` (new)
- `CONTRIBUTING.md` (updated with typing guidelines)

### Monitoring
- CI logs (mypy error counts)
- Test suite (ensure no regressions)
- Coverage reports (no drop in test coverage)

## References

- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 -- Type Hints](https://peps.python.org/pep-0484/)
- [typing module documentation](https://docs.python.org/3/library/typing.html)
- [Real Python: Python Type Checking Guide](https://realpython.com/python-type-checking/)
