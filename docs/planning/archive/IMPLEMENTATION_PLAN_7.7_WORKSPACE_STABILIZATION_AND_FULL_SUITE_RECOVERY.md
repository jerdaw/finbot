# Implementation Plan v7.7.0: Workspace Stabilization and Full-Suite Recovery

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Priority 5 reliability follow-through (post-item 9 quality gate hardening)

## Current State Summary

- Coverage target uplift to 60% is complete, but unfiltered local `pytest tests/` is unstable in this workspace.
- Primary blockers observed:
  - large number of `*sync-conflict*` file artifacts polluting discovery/lint.
  - missing `hypothesis` dependency for `tests/property`.
  - compatibility regressions against existing tests (`retry_strategy` constants/keys and regime-adaptive integration expectations).
- Assumption: `*sync-conflict*` files are merge/sync artifacts and should not remain in canonical source tree.

## Phased Plan

### Phase A: Workspace Cleanup

Goal:
- Remove artifact files that should not be collected as source/tests.

Deliverables:
- Delete all `*sync-conflict*` files from repository tree.
- Recheck file discovery to confirm cleanup.

Validation:
- `find` query for `*sync-conflict*` returns zero results.

### Phase B: Test Environment Recovery

Goal:
- Ensure all declared test suites can import required dependencies.

Deliverables:
- Add `hypothesis` to dev dependency group in `pyproject.toml`.
- Sync environment.

Validation:
- Property-test collection no longer fails on missing module.

### Phase C: Compatibility Regression Fixes

Goal:
- Restore behavior expected by currently committed tests.

Deliverables:
- Extend `finbot/utils/request_utils/retry_strategy.py` with explicit conservative/default/aggressive retry profiles using canonical keys.
- Register `RegimeAdaptive` in backtrader adapter strategy registry.
- Upgrade `segment_by_regime` to support optional `equity_curve` metrics output.

Validation:
- Previously failing test files pass.

### Phase D: Final Revalidation + Documentation Sync

Goal:
- Reconfirm full local quality/test baseline and update roadmap/plan checkoffs.

Deliverables:
- Run lint/tests for key touched files and full `pytest tests/` path.
- Update `docs/planning/roadmap.md` and this plan with completion notes.

Validation:
- Full `pytest tests/` collection and execution pass in local workspace.

## Deliverables Checklist

### D1: Remove sync-conflict artifacts
- Status: [x]

### D2: Add missing test dependency (`hypothesis`)
- Status: [x]

### D3: Fix retry/regime compatibility regressions
- Status: [x]

### D4: Revalidate and sync docs/roadmap
- Status: [x]

## Validation Snapshot

- `find . -type f -name '*sync-conflict*' | wc -l` -> `0`
- `uv sync` -> installed `hypothesis` in dev environment
- `DYNACONF_ENV=development uv run pytest tests/unit/test_request_utils_compat.py tests/unit/test_coverage_boost.py tests/unit/test_regime_adaptive.py -q` -> passed (`50 passed`)
- `DYNACONF_ENV=development uv run pytest tests/ -q` -> passed (`1191 passed, 11 skipped`)
- `DYNACONF_ENV=development uv run ruff check finbot/services/backtesting/regime.py finbot/services/backtesting/adapters/backtrader_adapter.py finbot/utils/request_utils/retry_strategy.py tests/unit/test_request_utils_compat.py tests/unit/test_coverage_boost.py tests/unit/test_regime_adaptive.py` -> passed

## Notes

- Repository-wide `ruff check .` still reports many notebook/web lint issues outside this stabilization tranche; these are pre-existing quality debt and not blockers for test-suite correctness.
