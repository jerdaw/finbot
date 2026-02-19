# Implementation Plan v6.3.0: E6 Evidence Gate Completion and E4 Deferred Closure

**Created:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Scope:** Complete deferred E4 replay/retry workflow and close E6 comparative decision gate with measured artifacts.

## Current State Summary

- E0-E5 are complete and stable.
- E6-T1 is complete with native Nautilus pilot path + contract-safe fallback.
- E4 core infrastructure is complete, but two deferred closures remained:
  - Snapshot replay workflow + documentation.
  - Batch retry ergonomics + documentation.
- E6 evaluation previously lacked measured side-by-side artifact outputs.

## Unknowns and Assumptions

### Unknowns

- Native Nautilus behavior on broader strategy coverage.
- Operational burden of dual-engine maintenance if promoted beyond pilot.

### Assumptions

- Backtrader remains default engine during this plan.
- New capabilities are opt-in to avoid regressions.
- Decision can remain `Defer` if evidence remains non-comparable.

## Objectives

1. Implement request-level snapshot replay in the contract adapter path.
2. Implement retry ergonomics for batch observability.
3. Publish measurable E6 benchmark artifacts.
4. Refresh evaluation and ADR decision docs from measured outputs.

## Phase Plan

### Phase 1: Contract/API and Runtime Wiring

#### Deliverables

- `BacktestRunRequest.data_snapshot_id` (optional request-level replay pinning).
- `BacktraderAdapter(enable_snapshot_replay=...)` and replay path via `snapshot_registry`.
- Replay precedence:
  - if replay enabled and request snapshot set: load snapshot dataset;
  - otherwise use configured in-memory histories.

#### Validation

- Unit tests for replay success/failure modes.
- Backward compatibility preserved for current callers.

### Phase 2: Batch Retry Ergonomics

#### Deliverables

- `backtest_batch(..., retry_failed=False, max_retry_attempts=1, retry_backoff_seconds=0.0)`.
- Retry policy for transient failures (timeout/resource/network message patterns).
- Attempt tracking in `BatchItemResult` and registry JSON serialization.

#### Validation

- Unit tests for retry success, retry skip, and invalid configuration.
- Existing batch observability tests continue to pass.

### Phase 3: Comparative Evidence Artifact

#### Deliverables

- Script: `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`.
- Artifact outputs:
  - `docs/research/artifacts/e6-benchmark-YYYY-MM-DD.json`
  - `docs/research/artifacts/e6-benchmark-YYYY-MM-DD.md`

#### Validation

- Script executes in repo environment and writes structured outputs.
- Outputs include runtime/memory + core metrics + adapter mode labels.

### Phase 4: Documentation and Decision Refresh

#### Deliverables

- Update `docs/research/nautilus-pilot-evaluation.md` with measured section.
- Update `docs/adr/ADR-011-nautilus-decision.md` with explicit tradeoff table and evidence link.
- Update `docs/planning/backtesting-live-readiness-backlog.md` and `docs/planning/roadmap.md` statuses.
- Add user guides:
  - `docs/user-guides/snapshot-replay.md`
  - `docs/user-guides/batch-observability-and-retries.md`

#### Validation

- All references resolvable and internally consistent.
- Decision state and roadmap/backlog status aligned.

## Risks and Mitigations

- **Risk:** Replay path affects baseline parity.
  - **Mitigation:** replay is opt-in; default path unchanged.
- **Risk:** Retry loops increase runtime.
  - **Mitigation:** retries disabled by default; strict attempt caps.
- **Risk:** Overstating Nautilus readiness.
  - **Mitigation:** mark scenario comparability explicitly in evaluation + ADR.

## Rollout and Rollback

### Rollout

- Ship replay/retry as additive flags with conservative defaults.
- Keep Backtrader default engine.
- Treat benchmark script as research artifact generator, not runtime dependency.

### Rollback

- Disable replay (`enable_snapshot_replay=False`) and retries (`retry_failed=False`) without code removal.
- Revert benchmark/evaluation updates independently from runtime code if needed.

## Success Criteria

- Replay from `data_snapshot_id` works and is tested.
- Retry metadata is persisted and tested.
- E6 benchmark artifacts are published and linked from evaluation/ADR.
- Backlog/roadmap/E6 docs reflect implementation reality.
