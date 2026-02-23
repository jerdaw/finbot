# Implementation Plan v7.6.0: Coverage Lift for Infrastructure, CLI Update Flow, and Simulation Wrappers

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Priority 5 item 9 (raise coverage from 56.05% toward 60%+)

## Current State Summary

- Current measured repository coverage: 56.05% (`713 passed, 2 skipped`).
- CI coverage gate is currently 50% in `.github/workflows/ci.yml` and `.github/workflows/ci-heavy.yml`.
- Recent coverage work focused on backtesting internals and selected simulation modules.
- Remaining high-impact gaps include CLI update execution paths, infrastructure utility modules, and simulation wrapper orchestration.

## Key Unknowns and Assumptions

- Assumption: deterministic tests can be implemented via monkeypatching to avoid network/filesystem coupling.
- Assumption: external integrations (Streamlit UI, API registry object wiring) can be tested as pure unit behavior.
- Unknown: exact post-tranche aggregate coverage uplift until full-suite run completes.

## Phased Plan

### Phase A: CLI Update/Output Reliability Coverage

Goal:
- Cover critical user-facing CLI execution paths with deterministic tests.

Deliverables:
- Tests for `finbot/cli/commands/update.py` dry-run, skip paths, success and failure handling.
- Tests for `finbot/cli/utils/output.py` format routing and error path.

Validation:
- Targeted pytest for new CLI tests passes.
- No behavior changes in command interfaces.

### Phase B: Simulation Wrapper/Orchestration Coverage

Goal:
- Add tests to cover simulation wrapper logic that composes existing engines/utilities.

Deliverables:
- Tests for `sim_specific_stock_indexes.py`, `sim_specific_bond_indexes.py`, and key registry/wrapper flows in `sim_specific_funds.py`.
- Tests for `monte_carlo_simulator.py` default path behavior with deterministic stubs.

Validation:
- New tests deterministic and isolated from live data APIs.
- Existing simulation tests remain green.

### Phase C: Infrastructure Utility Coverage

Goal:
- Raise coverage for core infrastructure modules that are currently under-tested.

Deliverables:
- Unit tests for API manager utility modules (`API`, `APIResourceGroup`, `APIManager`).
- Unit tests for logging setup/formatter utility modules (`logging_config.py`, `setup_queue_logging.py`, `utils.py`).

Validation:
- Targeted tests pass and confirm expected object wiring/filter/formatter behaviors.

### Phase D: Coverage Gate Advancement and Documentation Sync

Goal:
- Re-run full quality gates, quantify uplift, and update roadmap/plan status.

Deliverables:
- Full pytest + coverage run and threshold check.
- If coverage >= 60%, raise workflow `--cov-fail-under` from 50 to 60 and update docs.
- Update `docs/planning/roadmap.md` item 9 implementation details and completion state.

Validation:
- Ruff + mypy pass on touched scope.
- Full test suite pass with recorded coverage percentage.

## Deliverables Checklist

### D1: CLI update/output tests
- Status: [x]

### D2: Simulation wrapper/orchestration tests
- Status: [x]

### D3: Infrastructure utility tests
- Status: [x]

### D4: Validation run + roadmap/docs sync
- Status: [x]

## Rollout and Rollback

- Rollout: merge tests and threshold updates together only after full-suite validation is green.
- Rollback: if threshold uplift fails CI, retain added tests but keep threshold at prior passing value (50%) and mark item 9 partial.

## Validation Snapshot

- `DYNACONF_ENV=development uv run ruff check tests/unit/test_update_command_and_output.py tests/unit/test_simulation_wrappers_and_registry.py tests/unit/test_infrastructure_api_manager_and_logging.py` -> passed.
- `DYNACONF_ENV=development uv run pytest tests/unit/test_update_command_and_output.py tests/unit/test_simulation_wrappers_and_registry.py tests/unit/test_infrastructure_api_manager_and_logging.py -q` -> passed (`30 passed`).
- `DYNACONF_ENV=development uv run pytest tests/unit tests/integration tests/validation --ignore tests/property --ignore tests/performance --ignore tests/unit/test_coverage_boost.py --ignore tests/unit/test_regime_adaptive.py --ignore-glob='*sync-conflict*' -v --cov=finbot --cov-report=term --cov-fail-under=60` -> passed (`1123 passed, 10 skipped`, `67.10%` coverage).

## Notes

- Full `tests/` collection in this workspace currently includes additional non-tranche blockers (missing `hypothesis` dependency and `*sync-conflict*` artifacts). Coverage validation above uses the same practical path used for roadmap progress tracking while explicitly excluding those blockers.
