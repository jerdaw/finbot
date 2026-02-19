# Implementation Plan v7.1.0: Post-E6 Phase 2 Multi-Scenario Native Evidence

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Priority 6 items 71-72
**Primary Scope:** GS-02 and GS-03 like-for-like native Nautilus comparisons plus ADR-011 decision refresh.

## Current State Summary

Repository and docs review confirms:

- Priority 6 items 69-70 are complete as of 2026-02-19.
- Current benchmark artifact (`docs/research/artifacts/e6-benchmark-2026-02-19.json`) includes GS-01 only.
- `NautilusAdapter` currently has a native path for:
  - `NoRebalance` (single-symbol buy-and-hold pilot),
  - `Rebalance` mapped to Nautilus EMA cross (pilot-only, not strategy-equivalent).
- GS-02 (`DualMomentum`) and GS-03 (`RiskParity`) are parity-frozen in Backtrader and already covered by CI parity gates.
- ADR-011 remains **Defer**, with explicit follow-up tracker items for GS-02/GS-03 and final decision refresh still open.

## Key Unknowns and Assumptions

### Key Unknowns

1. Whether native Nautilus can represent GS-02 and GS-03 logic at acceptable equivalence confidence without excessive custom strategy complexity.
2. Whether runtime/memory and metric deltas remain stable across repeated GS-02/GS-03 samples.
3. Whether operational overhead (debugging effort, CI friction, environment setup variance) remains acceptable when expanding beyond GS-01.

### Assumptions

1. Backtrader remains default production engine throughout this batch.
2. Existing frozen datasets and windows in `docs/planning/golden-strategies-and-datasets.md` remain unchanged.
3. Evidence quality takes priority over speed: non-equivalent mappings are allowed only if confidence is explicitly downgraded and clearly explained.
4. CI budget tiering from item 70 remains in place; any extra heavy checks stay in `ci-heavy.yml` or manual workflows.

## Next Batch Selection

This batch explicitly targets roadmap items:

1. **71:** E6 follow-up phase 2 - GS-02/GS-03 like-for-like native comparison.
2. **72:** ADR-011 final revisit after multi-scenario evidence.

No additional roadmap items are included to keep scope decision-grade and finishable within available maintainer bandwidth.

## Goals and Non-Goals

### Goals

1. Produce repeatable benchmark rows for GS-02 and GS-03 with explicit equivalence/confidence metadata.
2. Extend pilot tooling and adapter paths only as needed for evidence generation.
3. Refresh evaluation + ADR artifacts so decision state is traceable and auditable.
4. Preserve existing parity and CI guardrails.

### Non-Goals

1. Full Nautilus migration or replacing Backtrader default.
2. Production live-trading readiness claims for Nautilus.
3. Broad strategy onboarding beyond frozen GS-01/GS-02/GS-03.

## Implementation Progress

- [x] Phase 0 complete (preflight, scenario/evidence schema freeze, benchmark contract checks).
- [x] Phase 1 complete (GS-02 implemented with confidence-labeled proxy-native comparability path).
- [x] Phase 2 complete (GS-03 implemented with confidence-labeled proxy-native comparability path).
- [x] Phase 3 complete (evaluation report + ADR-011 refreshed against multi-scenario artifact evidence).
- [x] Phase 4 complete (targeted tests + benchmark run verification + roadmap/backlog status sync).

Implementation note:
- GS-02/GS-03 are delivered as deterministic proxy-native pilot modes (`native_nautilus_proxy`) with explicit medium-confidence labeling; decision remains Defer.

## Delivery Approach (Phased)

## Phase 0: Preflight and Evidence Contract Freeze

**Goal:** Lock inputs and evaluation rules before adding new implementation paths.

**Deliverables**

1. Confirm frozen GS-02/GS-03 symbols, windows, and params from `golden-strategies-and-datasets.md`.
2. Add/confirm benchmark artifact schema fields needed for multi-scenario reporting:
   - `scenario_id`, `strategy_equivalent`, `equivalence_notes`, `confidence`,
   - optional `comparison_limitations` text field for low/medium confidence rows.
3. Document acceptance thresholds for this batch (runtime repeatability, metric completeness, and confidence labeling).

**Dependencies**

- Existing benchmark script and artifacts.
- Golden datasets in repository.

**Validation**

- Dry-run benchmark script still passes for GS-01 unchanged.
- Schema backward compatibility preserved for existing artifact consumers.

## Phase 1: GS-02 Native Comparability Path

**Goal:** Generate the first multi-asset, regime-switching native comparison row.

**Deliverables**

1. Extend `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py` to support a GS-02 scenario definition.
2. Implement the minimum native Nautilus path required to execute GS-02 logic or a transparently non-equivalent proxy.
3. Record assumptions in adapter output:
   - selected strategy mapping,
   - known divergences from Backtrader GS-02 behavior,
   - confidence rating rationale.
4. Add/extend unit tests covering:
   - request validation,
   - mode tagging,
   - equivalence/confidence metadata.

**Dependencies**

- `finbot/adapters/nautilus/nautilus_adapter.py`
- `finbot/services/backtesting/strategies/dual_momentum.py`
- GS-02 frozen data availability (`SPY`, `TLT`)

**Risks**

1. Native platform primitives may not match Backtrader order timing exactly.
2. Strategy state semantics (lookback warmup + rebalance cadence) may drift.

**Mitigations**

1. Use confidence labels and equivalence notes as first-class outputs.
2. Keep scenario-specific mapping logic explicit and test-covered.
3. Require reproducible multi-sample median output before publishing final row.

**Validation**

- GS-02 benchmark rows generated for both engines.
- Artifact includes explicit confidence and equivalence notes.
- Existing GS-01 benchmark path remains green.

## Phase 2: GS-03 Native Comparability Path

**Goal:** Generate multi-asset volatility-weighted comparison evidence for GS-03.

**Deliverables**

1. Extend benchmark script scenario catalog with GS-03.
2. Implement minimum native path for GS-03 risk-parity-like behavior or explicit proxy mode.
3. Add tests focused on:
   - multi-symbol validation,
   - volatility-window/rebalance parameter handling,
   - metadata correctness for strategy-equivalent vs proxy mode.

**Dependencies**

- `finbot/services/backtesting/strategies/risk_parity.py`
- GS-03 frozen data availability (`SPY`, `QQQ`, `TLT`)

**Risks**

1. Volatility estimation differences can materially move weights and trades.
2. Higher complexity may increase debug time and reduce confidence.

**Mitigations**

1. Keep deterministic parameter mapping and document all computation differences.
2. Fail closed: if native run is unstable, publish row as low-confidence proxy instead of overstating equivalence.

**Validation**

- GS-03 rows published in JSON + Markdown artifacts.
- Metrics (`roi`, `cagr`, `max_drawdown`, `ending_value`, runtime, memory) populated for both engines.
- Unit/integration tests pass for expanded scenarios.

## Phase 3: Evaluation Report and ADR-011 Refresh

**Goal:** Convert multi-scenario results into a decision-grade recommendation.

**Deliverables**

1. Update `docs/research/nautilus-pilot-evaluation.md` with GS-01/GS-02/GS-03 table and confidence commentary.
2. Refresh `docs/adr/ADR-011-nautilus-decision.md`:
   - revisit option matrix,
   - resolve follow-up tracker checkboxes,
   - set explicit decision state (`Go`, `No-Go`, `Hybrid`, or `Defer`) with rationale tied to measured evidence.
3. Synchronize roadmap/backlog status and references.

**Dependencies**

- Completed artifact outputs from Phases 1-2.

**Risks**

1. Evidence can remain mixed and not support a confident final change in decision state.

**Mitigations**

1. Permit decision to remain **Defer** if evidence still fails coverage/quality criteria; document exactly what remains missing.

**Validation**

- ADR decision statement and tracker are internally consistent.
- Evaluation report references latest artifact filenames and dates.
- Roadmap items 71-72 status reflect implemented reality.

## Phase 4: Hardening and CI/Operational Validation

**Goal:** Ensure new evidence tooling is reproducible and does not destabilize core workflows.

**Deliverables**

1. Add lightweight regression tests for new benchmark scenario wiring where practical.
2. Run targeted test suite (unit + integration parity + benchmark smoke).
3. Confirm CI workflow boundaries remain aligned:
   - core checks in `ci.yml`,
   - heavy/expanded checks in `ci-heavy.yml`.
4. Record run commands and reproducibility notes in docs.

**Validation**

- Local/CI command set produces consistent artifacts.
- No regression in existing golden parity tests.

## Milestones and Timeline (High-Level)

Planned cadence assumes one primary maintainer with normal project load.

1. **Milestone M1 (by 2026-02-20):** Phase 0 complete (frozen criteria + schema guardrails).
2. **Milestone M2 (by 2026-02-23):** GS-02 implemented and benchmarked (Phase 1).
3. **Milestone M3 (by 2026-02-25):** GS-03 implemented and benchmarked (Phase 2).
4. **Milestone M4 (by 2026-02-26):** Evaluation + ADR refresh complete (Phase 3).
5. **Milestone M5 (by 2026-02-27):** Hardening/validation and roadmap closure update complete (Phase 4).

Total target duration: ~5-7 working days.

## Progress Validation Framework

Progress is considered valid only when all are true:

1. Benchmark artifacts include rows for `gs01`, `gs02`, and `gs03`.
2. Each row has explicit `strategy_equivalent` and `confidence` labeling.
3. Expanded tests pass without weakening existing parity tolerances.
4. ADR-011 decision section references current measured evidence (with artifact date).
5. Roadmap/backlog/evaluation/ADR documents are cross-consistent on status.

## Rollout and Rollback

### Rollout Strategy

1. Ship adapter/benchmark changes incrementally per scenario (GS-02 first, then GS-03).
2. Publish artifacts after each scenario is stable, then refresh decision docs.
3. Keep Backtrader default unchanged during and after rollout unless ADR explicitly changes that.

### Rollback Strategy

1. If new native scenario path is unstable, disable that scenario’s native mode and preserve fallback behavior.
2. Revert benchmark scenario additions selectively without removing previously valid GS-01 evidence.
3. If ADR refresh is inconclusive, keep decision as **Defer** and document residual blockers instead of forcing a premature choice.

## Resource and Constraint Alignment

1. Uses existing architecture: adapter-first contracts, frozen datasets, parity gates, and tiered CI.
2. Avoids high-cost scope expansion (no full engine migration, no broad strategy onboarding).
3. Keeps changes concentrated in pilot adapter, benchmark script, tests, and decision artifacts.
4. Maintains free-tier CI budget posture by preserving existing core/heavy workflow split.

## Blocking Conditions Requiring User Input

None currently blocking. Questions are deferred unless one of these occurs:

1. Required frozen dataset files are missing/corrupt.
2. Nautilus native runtime cannot execute GS-02/GS-03 at all in current environment.
3. Decision preference conflicts with evidence (for example, user wants forced Go/No-Go despite low-confidence outputs).
