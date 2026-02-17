# Fix Remaining Mypy Exclusions - Implementation Plan

**Item:** Priority 5, Item 34
**Status:** In Progress
**Date Started:** 2026-02-17

## Overview

Fix all modules currently excluded from mypy type checking via `ignore_errors=true` in `pyproject.toml`.

## Current State

### Modules with `ignore_errors=true` (5 total):

1. **`finbot.utils.data_collection_utils.fred.correlate_fred_to_price`**
   - Comment: "WIP modules with complex type issues to be fixed incrementally"
   - Likely issues: pandas DataFrame typing, complex data transformations

2. **`finbot.libs.api_manager._utils.api_resource_group`**
   - Comment: "Modules importing not-yet-created files (rate_limiter, retry_strategy)"
   - Likely issues: Import-time type checking, module structure

3. **`finbot.libs.api_manager._utils.api_manager`**
   - Comment: "Modules importing not-yet-created files (rate_limiter, retry_strategy)"
   - Likely issues: Import-time type checking, module structure

4. **`finbot.libs.api_manager._resource_groups.api_resource_groups`**
   - Comment: "Modules importing not-yet-created files (rate_limiter, retry_strategy)"
   - Likely issues: Import-time type checking, module structure

5. **`finbot.cli.commands.update`**
   - Comment: "Modules importing not-yet-created files (rate_limiter, retry_strategy)"
   - Likely issues: Import-time type checking, CLI command typing

## Implementation Strategy

### Phase 1: Assessment (30 min)
1. Run mypy on each module individually to see actual errors
2. Categorize errors by type (missing annotations, Any usage, import issues, etc.)
3. Prioritize fixes by complexity

### Phase 2: Fix Modules (3-5 hours)
For each module:
1. Remove `ignore_errors=true` temporarily
2. Run mypy to see all errors
3. Fix errors systematically:
   - Add missing type annotations
   - Replace `Any` with specific types
   - Add `# type: ignore` comments for unfixable third-party issues
   - Use `TYPE_CHECKING` imports if needed
4. Verify fixes with `uv run mypy <module_path>`
5. Run tests to ensure no regressions

### Phase 3: Verification (30 min)
1. Remove all `ignore_errors=true` overrides from pyproject.toml
2. Run full mypy check: `uv run mypy`
3. Verify no new errors
4. Run full test suite: `uv run pytest tests/`

### Phase 4: Documentation (15 min)
1. Update roadmap.md to mark item 34 complete
2. Document common mypy patterns found and fixed
3. Create completion summary

## Common Mypy Fixes

### 1. Missing Function Annotations
```python
# Before
def process_data(df, threshold):
    return df[df > threshold]

# After
def process_data(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    return df[df > threshold]
```

### 2. Any Types
```python
# Before
from typing import Any
def process(data: Any) -> Any:
    return data.transform()

# After
from typing import TypeVar
T = TypeVar('T')
def process(data: T) -> T:
    return data.transform()
```

### 3. TYPE_CHECKING Imports
```python
# Before
from some_module import HeavyClass  # Causes circular import

# After
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from some_module import HeavyClass
```

### 4. pandas DataFrame typing
```python
# Option 1: Generic DataFrame
import pandas as pd
def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    return df[df['value'] > 0]

# Option 2: pandas-stubs (if available)
from pandas import DataFrame
def filter_data(df: DataFrame) -> DataFrame:
    return df[df['value'] > 0]
```

## Acceptance Criteria

- [ ] All 5 modules have type checking enabled (no `ignore_errors=true`)
- [ ] `uv run mypy` passes with zero errors
- [ ] All tests pass: `uv run pytest tests/`
- [ ] Roadmap.md updated to mark item 34 complete
- [ ] Completion summary document created

## Estimated Timeline

- Phase 1 (Assessment): 30 minutes
- Phase 2 (Fixes): 3-5 hours (30-60 min per module)
- Phase 3 (Verification): 30 minutes
- Phase 4 (Documentation): 15 minutes

**Total:** 4.25-6.25 hours (Medium, fits within 1-2 days estimate)

## Dependencies

- None (standalone task)

## Risks

1. **Third-party library typing:** Some libraries may not have type stubs
   - Mitigation: Use `# type: ignore` comments for specific lines

2. **Complex pandas operations:** DataFrame typing can be tricky
   - Mitigation: Use generic `pd.DataFrame` type, add inline comments

3. **Circular imports:** TYPE_CHECKING imports may be needed
   - Mitigation: Use `if TYPE_CHECKING:` blocks for type-only imports

## Success Metrics

- Zero mypy errors across entire codebase
- All tests passing
- No new `# type: ignore` comments added (use sparingly)
- Improved type safety for future development
