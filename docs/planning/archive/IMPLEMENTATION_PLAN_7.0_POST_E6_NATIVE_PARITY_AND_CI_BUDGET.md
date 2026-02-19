# Implementation Plan v7.0.0: Post-E6 Native Parity and CI Budget Optimization

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented and archived 2026-02-19)
**Roadmap Anchors:** Priority 6 items 69-70
**Scope:** Establish like-for-like native Nautilus evidence for GS-01 and reduce CI free-tier usage without weakening core gates.

## Current State Summary

- E0-E6 current cycle is complete with ADR-011 decision set to **Defer**.
- Backtrader remains default engine with full golden parity gating.
- Nautilus has native execution for pilot scope but prior benchmark evidence was not fully comparable on strategy logic.
- CI currently runs multiple expensive jobs on every PR/push, including matrix testing and non-blocking scans.

## Key Unknowns and Assumptions

### Unknowns

- Native Nautilus comparability quality beyond single-symbol GS-01.
- CI minute savings after tiering under real PR cadence.

### Assumptions

- Backtrader remains default until ADR-011 is revisited with broader native evidence.
- This batch targets only roadmap items 69-70.
- Heavy quality checks may be shifted from PR to scheduled/manual workflows as long as core PR gates remain strict.

## Objectives

1. Add a native Nautilus path for GS-01-style NoRebalance with explicit equivalence metadata.
2. Produce benchmark artifacts that include machine-readable comparability confidence fields.
3. Split CI into tiered workflows:
   - PR core gate (fast, blocking).
   - heavy scheduled/manual gate (broad, expensive).
4. Sync roadmap/backlog/evaluation/ADR docs to the new post-E6 execution state.

## Phase Plan

## Phase 1: Native Comparability Wiring

### Deliverables

- Extend `NautilusAdapter` validation to support `NoRebalance` (single symbol) in native mode.
- Add a native long-only buy-and-hold strategy path for `NoRebalance`.
- Preserve existing `Rebalance` pilot mapping path and fallback semantics.

### Validation

- Unit tests cover:
  - accepted native `NoRebalance`,
  - rejection for unsupported/multi-symbol `NoRebalance`,
  - existing fallback behavior unchanged.

## Phase 2: Benchmark Artifact Upgrade

### Deliverables

- Update benchmark script to support scenario selection:
  - `gs01` (like-for-like NoRebalance),
  - `legacy_pilot` (historical rebalance->EMA mapping for reference).
- Include comparability metadata in artifacts:
  - `scenario_id`,
  - `strategy_equivalent`,
  - `equivalence_notes`,
  - `confidence`.

### Validation

- Script runs from repo and writes JSON/Markdown artifacts under `docs/research/artifacts/`.
- Markdown table includes equivalence and confidence columns.

## Phase 3: CI Tiering for Free-Tier Budget

### Deliverables

- Keep `.github/workflows/ci.yml` as PR/main fast gate:
  - `ruff` lint/format,
  - `mypy`,
  - Python 3.13 tests with coverage threshold,
  - golden parity gate.
- Add `.github/workflows/ci-heavy.yml`:
  - Python matrix tests,
  - bandit + pip-audit,
  - docstring coverage,
  - full parity suite.
- Add workflow concurrency cancellation to reduce duplicate runs.

### Validation

- Workflow syntax validates.
- Core PR checks still block regressions.
- Heavy checks remain available via schedule/manual and on `main`.

## Phase 4: Decision Artifact Refresh

### Deliverables

- Update:
  - `docs/research/nautilus-pilot-evaluation.md`,
  - `docs/adr/ADR-011-nautilus-decision.md`,
  - `docs/planning/roadmap.md`,
  - `docs/planning/backtesting-live-readiness-backlog.md`.
- Add this plan to roadmap execution document references.

### Validation

- Cross-document consistency for:
  - current phase wording,
  - status of items 69-70,
  - evidence artifact links.

## Major Dependencies and Risks

### Dependencies

- Existing Nautilus package availability in local/CI environments.
- Existing golden dataset files and parity harness.

### Risks

- Native `NoRebalance` path may still diverge under some market data shapes.
- CI split could obscure regressions if heavy jobs are not monitored.

### Mitigations

- Explicit confidence/equivalence fields in benchmark outputs.
- Keep parity gate as a required core job.
- Keep heavy workflow on schedule + manual + `main` push.

## Timeline / Milestones (5 Working Days)

1. Day 1: Phase 1 complete (adapter + tests).
2. Day 2: Phase 2 complete (artifact schema + benchmark run).
3. Day 3: Phase 3 complete (tiered workflows).
4. Day 4-5: Phase 4 complete (docs synchronization and status closure).

## Rollout and Rollback

### Rollout

- Ship as additive:
  - new native `NoRebalance` pilot path,
  - upgraded benchmark metadata,
  - tiered CI workflows.

### Rollback

- Disable new Nautilus native mode by forcing fallback if needed.
- Revert `ci-heavy.yml` + restore prior `ci.yml` shape if gate coverage is reduced unexpectedly.
- Keep evidence artifacts but annotate superseded outputs rather than deleting.

## Public Interface Notes

- No breaking API changes for CLI or existing backtest runner calls.
- `NautilusAdapter` native capability expands to include single-symbol `NoRebalance`.

## Completion Criteria

- Roadmap items 69-70 moved from not started to complete/in-progress with linked evidence.
- GS-01 native benchmark artifact includes confidence/equivalence fields.
- PR CI path is measurably lighter while retaining required quality gates.
