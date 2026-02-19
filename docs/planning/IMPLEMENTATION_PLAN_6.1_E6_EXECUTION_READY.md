# Implementation Plan v6.1.0: E6 Execution Readiness

**Created:** 2026-02-19
**Scope:** E6 pilot execution path hardening + deferred E4 integration closure

## Current State Summary

- E0-E5 are complete.
- E6 planning artifacts existed, but the Nautilus adapter implementation was a skeleton with contract drift.
- Two E4 integrations were still deferred:
  - Snapshot wiring in adapter run path.
  - Batch observability wiring in `backtest_batch`.
- Current repo includes local in-progress Nautilus artifacts and lockfile changes.

## Key Unknowns and Assumptions

### Unknowns
- Native Nautilus execution behavior in this environment.
- Quantitative parity/performance deltas for a true Nautilus run path.

### Assumptions
- Backtrader remains the default production-grade engine.
- E6 pilot can ship as a contract-compliant adapter path with explicit fallback semantics.
- Decision gate can proceed with a defer outcome if native Nautilus evidence is incomplete.

## Goals

1. Fix contract-level correctness for `NautilusAdapter`.
2. Close E4 integration gaps needed for reproducibility and observability.
3. Add tests proving new behavior.
4. Sync roadmap/backlog/evaluation/ADR docs with implementation reality.

## Phase Plan

## Phase 1: Contract Alignment (Complete in this batch)

### Deliverables
- `finbot/adapters/nautilus/nautilus_adapter.py`
  - Implement `run(request)` to satisfy `BacktestEngine`.
  - Provide backward-compatible `run_backtest()` alias.
  - Enforce pilot scope validation (rebalance-only).
  - Return canonical `BacktestRunResult` and `BacktestRunMetadata`.
  - Emit explicit fallback warnings instead of raising `NotImplementedError`.

### Validation
- Unit tests for adapter run path, alias, and validation failures.

## Phase 2: Reproducibility + Observability Integration (Complete in this batch)

### Deliverables
- `finbot/services/backtesting/adapters/backtrader_adapter.py`
  - Add optional `snapshot_registry` + `auto_snapshot`.
  - Auto-create and attach deterministic `data_snapshot_id` when enabled.
- `finbot/services/backtesting/backtest_batch.py`
  - Add optional `track_batch` + `batch_registry`.
  - Track batch lifecycle/status and item-level outcomes in `BatchRegistry`.
  - Preserve old behavior when observability mode is disabled.

### Validation
- Unit test for snapshot ID auto-attachment.
- Unit tests for partial/all-fail batch observability flows.

## Phase 3: Documentation and Decision Gate Alignment (Complete in this batch)

### Deliverables
- Update E6 evaluation report with evidence from implemented pilot path.
- Finalize ADR-011 as **Defer** pending native Nautilus execution evidence.
- Update roadmap/backlog/README status and cross-references.

### Validation
- Internal consistency across:
  - `docs/planning/backtesting-live-readiness-backlog.md`
  - `docs/planning/roadmap.md`
  - `docs/research/nautilus-pilot-evaluation.md`
  - `docs/adr/ADR-011-nautilus-decision.md`
  - `README.md`

## Major Dependencies and Risks

### Dependencies
- Existing Backtrader adapter contract stability.
- Snapshot and batch registry modules.

### Risks
- False confidence from fallback path being mistaken for native Nautilus readiness.
- Behavior changes in `backtest_batch` when observability mode is enabled.

### Mitigations
- Explicit `adapter_mode` artifacts/assumptions in run output.
- Keep default backtest batch execution semantics unchanged unless tracking is explicitly enabled.

## Milestones

1. Contract-correct Nautilus pilot adapter.
2. Snapshot auto-capture integrated and tested.
3. Batch observability integrated and tested.
4. Decision and status docs synchronized.

## Rollout / Rollback

### Rollout
- Ship as additive behavior:
  - `NautilusAdapter` pilot mode.
  - Optional snapshot and batch tracking toggles.

### Rollback
- Disable use of `NautilusAdapter` in runtime selection if needed.
- Keep `track_batch=False` and `auto_snapshot=False` defaults to avoid regressions.
- Revert only adapter/batch integration commits if issues arise; no contract rollback required.

## Public Interface Additions

- `NautilusAdapter.run(request)` (canonical interface).
- `NautilusAdapter.run_backtest(request)` (compatibility shim).
- `BacktraderAdapter(..., snapshot_registry=None, auto_snapshot=False)`.
- `backtest_batch(..., track_batch=False, batch_registry=None)`.

## Test Coverage Added

- `tests/unit/test_nautilus_adapter.py`
- `tests/unit/test_backtest_batch_observability.py`
- `tests/unit/test_backtrader_adapter.py` (snapshot integration case)
- `tests/unit/test_imports.py` (Nautilus adapter import smoke)
