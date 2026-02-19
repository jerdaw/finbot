# Implementation Plan v7.5.0: Coverage Lift for Low-Coverage Simulation and Utility Modules

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19, partial progression toward item 9)
**Roadmap Anchors:** Priority 5 item 9 (partial progression)

## Current State Summary

- Repository coverage baseline after v7.4: 54.51%.
- CI coverage gate at completion: 50%.
- Item 9 target remains 60%+ with more module-level coverage still needed.

## Scope for v7.5

1. Add deterministic tests for low-coverage simulation modules and helpers.
2. Add tests for request utility compatibility shims introduced in v7.3.
3. Re-run quality gates and full coverage measurement.
4. Update roadmap and this plan with completed checkoffs and measured outcomes.

## Deliverables

### D1: Request utils coverage
- `tests/unit/test_request_utils_compat.py`
- Status: [x]

### D2: Bond ladder internals coverage
- `tests/unit/test_bond_ladder_components.py`
- Status: [x]

### D3: Index simulator orchestration coverage
- `tests/unit/test_index_simulators.py`
- Status: [x]

### D4: Overnight LIBOR approximation coverage
- `tests/unit/test_approximate_overnight_libor.py`
- Status: [x]

### D5: Validation + docs sync
- `docs/planning/roadmap.md`
- this plan file
- Status: [x]

## Validation Snapshot

- `DYNACONF_ENV=development uv run pytest tests/unit/test_request_utils_compat.py tests/unit/test_bond_ladder_components.py tests/unit/test_index_simulators.py tests/unit/test_approximate_overnight_libor.py -v` -> passed (`11 passed`)
- `DYNACONF_ENV=development uv run mypy finbot/` -> passed
- `DYNACONF_ENV=development uv run pytest tests/ -v --cov=finbot --cov-fail-under=50` -> passed (`713 passed, 2 skipped`, `56.05%` coverage)

## Remaining Gap

- Priority 5 item 9 remains open because the 60%+ target has not yet been reached (current: 56.05%).
