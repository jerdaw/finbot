# Implementation Plan v8.1.0: Priority 5 Tail and E6 Confidence Uplift

**Created:** 2026-02-20
**Status:** Complete (2026-02-20)
**Owner:** Maintainer
**Roadmap Anchors:** Priority 5 item 12, Priority 5 item 42 (deferred), Priority 6 items 71-72 follow-up

## Brief Current State

Finbot is stable and mature after v8.0 closeout:

1. Priority 5 is 43/45 complete.
2. Priority 6 is complete, with ADR-011 decision still `Defer`.
3. GS-02 and GS-03 Nautilus evidence remains proxy-native medium confidence.
4. Strict mypy enforcement is expanded across core/execution/backtesting/libs and multiple utility scopes, with additional legacy utility scope still pending.
5. Priority 7 planning docs contain stale status in places and require synchronization.

## Key Unknowns

1. Whether maintainers want to execute P7.4 history rewrite (force-push risk).
2. Whether branding direction for item 42 is available this cycle.
3. Whether full-native GS-02/GS-03 can be validated on local/CI environments where Nautilus is installed.

## Assumptions

1. Backtrader remains default engine.
2. Nautilus remains pilot/experimental.
3. P7.4 history rewrite stays out of scope for this batch.
4. Item 42 remains deferred until human-approved design assets exist.

## Scope

### In Scope

1. Planning/status reconciliation for roadmap and Priority 7 docs.
2. Bounded strict-mypy continuation in selected low-risk legacy utility modules.
3. GS-02/GS-03 confidence uplift path in Nautilus adapter with explicit fidelity tagging and benchmark/report updates.
4. Manual-media artifact runbook/templates for remaining video/poster work.

### Out of Scope

1. Global strict-mypy enablement for all remaining utilities.
2. Final logo/branding implementation.
3. P7.4 commit history rewrite.

## Phases

## Phase Status Checklist (2026-02-20)

1. [x] Phase 1: Planning reconciliation baseline.
2. [x] Phase 2: Strict-mypy Wave 10 (bounded scope) implemented and validated.
3. [x] Phase 3: Full-native GS-02/GS-03 path + fidelity-aware benchmark refresh completed.
4. [x] Phase 4: Manual artifact enablement docs/templates published.
5. [x] Phase 5: Completion summary published and archive snapshot created.

### Phase 1: Planning Reconciliation Baseline

**Goal:** align planning docs with current repository truth.
**Status:** ✅ Complete (2026-02-20)

Deliverables:

1. `docs/planning/priority-7-status-refresh-2026-02-20.md`
2. Roadmap current-phase update to reference v8.1 execution.
3. Priority-7 implementation plan metadata/status correction.

Validation:

1. Every corrected status row includes evidence path(s).
2. No contradictory completion percentages across core planning docs.

### Phase 2: Strict-Mypy Wave 10 (Bounded)

**Goal:** continue item 12 with narrow legacy utility scope.
**Status:** ✅ Complete (2026-02-20)

Target scopes:

1. `finbot.utils.data_collection_utils.bls.*`
2. `finbot.utils.data_collection_utils.fred.*` (excluding intentionally unimplemented `get_all_fred_datas`)
3. `finbot.utils.data_collection_utils.yfinance.*` (excluding intentionally unimplemented `get_all_yfinance_datas`)
4. `finbot.utils.data_science_utils.data_transformation.interpolators.*`
5. `finbot.utils.data_science_utils.data_transformation.scalers_normalizers.*`

Deliverables:

1. Module-level mypy overrides in `pyproject.toml`.
2. Required signature typing fixes for the selected scopes.
3. Tracker update in `docs/guides/mypy-strict-module-tracker.md`.

Validation:

1. `uv run mypy finbot/` remains clean.
2. Relevant unit tests remain green.

### Phase 3: E6 Follow-up Confidence Uplift

**Goal:** add full-native GS-02/GS-03 pathway with explicit fallback and fidelity labels.
**Status:** ✅ Complete (2026-02-20)

Deliverables:

1. Nautilus adapter attempts full-native DualMomentum and RiskParity path when available.
2. Fallback behavior remains safe and explicit (proxy-native or backtrader fallback).
3. `execution_fidelity` and `adapter_mode` assumptions standardized.
4. Benchmark script confidence derives from fidelity labels.
5. Research/ADR docs updated with fidelity language.

Validation:

1. Unit tests cover fidelity labels, fallback behavior, and benchmark metadata mapping.
2. Existing Nautilus adapter tests remain passing.
3. Full benchmark artifact refresh run completed:
   - `docs/research/artifacts/e6-benchmark-2026-02-20.json`
   - `docs/research/artifacts/e6-benchmark-2026-02-20.md`
4. Outcome: execution fidelity reached `full_native` for GS-02/GS-03, but strategy equivalence remains `false` with low confidence due large metric divergence.

### Phase 4: Manual Artifact Enablement

**Goal:** unblock remaining manual Priority 7 artifacts through process assets.
**Status:** ✅ Complete (2026-02-20)

Deliverables:

1. `docs/guides/media-artifact-production-runbook.md`
2. `docs/templates/poster-outline.md`
3. `docs/templates/video-script-template.md`

Validation:

1. Templates and runbook are linked from status-refresh doc and roadmap references.

### Phase 5: Completion + Archive

**Goal:** close v8.1 with clear evidence.
**Status:** ✅ Complete (2026-02-20)

Deliverables:

1. `docs/planning/archive/IMPLEMENTATION_PLAN_8.1_COMPLETION_SUMMARY.md`
2. Archive copy under `docs/planning/archive/`.

Validation:

1. `uv run ruff check .`
2. `uv run mypy finbot/`
3. `uv run pytest` (full or documented constrained suite)

## Milestones

1. M1: Planning reconciliation complete.
2. M2: Wave 10 strict scope added and green.
3. M3: GS-02/GS-03 fidelity path and benchmark logic merged.
4. M4: Manual-media runbook/templates published.
5. M5: Completion summary and archive published.

## Rollout/Rollback

### Rollout

1. Merge per-phase in small, reviewable commits.
2. Keep heavy benchmark workloads off default PR path.

### Rollback

1. Revert strict override blocks if CI/type stability degrades.
2. Keep full-native GS-02/GS-03 behind graceful fallback if unsupported in runtime.
3. Revert status-only docs updates if evidence mismatch is found.
