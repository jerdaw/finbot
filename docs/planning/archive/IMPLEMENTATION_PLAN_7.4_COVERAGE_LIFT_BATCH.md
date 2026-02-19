# Implementation Plan v7.4.0: Coverage Lift Batch (Priority 5 Item 9)

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19, partial progress toward item 9 target)
**Roadmap Anchors:** Priority 5 items 9 (partial), 10, 22 follow-through

## Current State Summary

- Priority 5 item 9 (coverage 60%+) remains open.
- Item 10 and 22 have been completed in v7.3.
- Remaining item 9 sub-gaps called out in roadmap include tests for:
  - `backtest_batch` (parallel execution and aggregation)
  - `rebalance_optimizer`
  - `bond_ladder_simulator`

## Scope for v7.4

1. Add targeted tests for `backtest_batch` non-observability path and core helper behavior.
2. Add tests for `rebalance_optimizer` service module behaviors.
3. Add deterministic tests for `bond_ladder_simulator` orchestration paths.
4. Run lint/type/tests and update roadmap + plan checkoffs.

## Deliverables

### D1: backtest_batch test expansion
- `tests/unit/test_backtest_batch_core.py`
- Status: [x]

### D2: rebalance_optimizer tests
- `tests/unit/test_rebalance_optimizer_module.py`
- Status: [x]

### D3: bond ladder simulator tests
- `tests/unit/test_bond_ladder_simulator.py`
- Status: [x]

### D4: verification + docs sync
- `docs/planning/roadmap.md`
- this plan file status/checkoffs
- `.github/workflows/ci.yml` and `.github/workflows/ci-heavy.yml` coverage threshold updates
- Status: [x]

## Validation Commands

- `uv run ruff check ...`
- `DYNACONF_ENV=development uv run mypy finbot/`
- `DYNACONF_ENV=development uv run pytest <new test files> -v`

## Validation Snapshot

- `DYNACONF_ENV=development uv run pytest tests/unit/test_backtest_batch_core.py tests/unit/test_rebalance_optimizer_module.py tests/unit/test_bond_ladder_simulator.py -v` -> passed (`8 passed`)
- `DYNACONF_ENV=development uv run mypy finbot/` -> passed
- `uv run ruff check ...` on touched files -> passed
- `DYNACONF_ENV=development uv run pytest tests/ -v --cov=finbot --cov-fail-under=45` -> passed (`702 passed, 2 skipped`, `54.51%` coverage)

## Remaining Gap

- Priority 5 item 9 is still open overall because:
  - 60%+ repository coverage target is not yet reached/confirmed in CI threshold.
  - bond ladder **end-to-end** coverage with full yield-history workflow remains pending.
