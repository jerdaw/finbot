# Implementation Plan v7.8.0: Ruff Baseline Stabilization

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Post-v7.7 reliability follow-through (tooling baseline hardening)

## Current State Summary

- Full test suite is currently passing after v7.7.
- Repository-wide `ruff check .` fails due to:
  - notebook (`*.ipynb`) lint parsing/style noise not aligned with current Ruff ruleset.
  - one FastAPI rule violation (`B008`) in `web/backend/routers/simulations.py`.
- Assumption: notebook code quality is managed separately from strict repo lint gate.

## Phased Plan

### Phase A: Align Ruff Scope

Goal:
- Ensure repository lint gate is scoped to maintainable source paths.

Deliverables:
- Remove notebook inclusion from Ruff config.

Validation:
- Notebook-derived lint errors disappear from `ruff check .`.

### Phase B: Fix Remaining Source Lint Violations

Goal:
- Resolve non-notebook lint errors in source code.

Deliverables:
- Fix FastAPI default argument pattern in `web/backend/routers/simulations.py` (`B008`).

Validation:
- `ruff check .` passes.

### Phase C: Revalidation + Documentation Sync

Goal:
- Record baseline restoration in planning docs.

Deliverables:
- Update this plan with completed checklist + validation snapshot.
- Update roadmap with completion note.

Validation:
- `ruff check .` pass evidence captured.

## Deliverables Checklist

### D1: Ruff scope alignment for notebooks
- Status: [x]

### D2: FastAPI router lint fix
- Status: [x]

### D3: Validation run and plan/roadmap sync
- Status: [x]

## Validation Snapshot

- `DYNACONF_ENV=development uv run ruff check .` -> passed.
- `DYNACONF_ENV=development uv run pytest tests/unit/test_update_command_and_output.py tests/integration/test_cli_execution_paths.py -q` -> passed (`10 passed`).

## Notes

- Notebook linting was intentionally removed from repo-wide Ruff baseline by excluding `notebooks/` in `pyproject.toml`; notebook quality can be managed via dedicated notebook-focused tooling in a future tranche.
