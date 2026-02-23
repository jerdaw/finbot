# Implementation Plan v8.5.0: E6 Native-Only Valuation Parity Closure

**Date:** 2026-02-20
**Status:** In Progress
**Roadmap Anchor:** `docs/planning/roadmap.md` item 76

## Current State Summary

Repository/documentation review and latest benchmark evidence show:

1. E0-E6 core delivery remains complete and stable; Backtrader remains parity-gated default.
2. v8.4 closed GS-02/GS-03 tolerance gates using `shadow_backtrader` valuation fidelity.
3. Native-only valuation extraction is now implemented for GS-02/GS-03 full-native Nautilus runs.
4. Latest native-only artifact (`docs/research/artifacts/e6-benchmark-2026-02-20.json`, generated 2026-02-20T04:41:18Z) reports:
   - `gs02`: `equivalent=no`, `confidence=low`
   - `gs03`: `equivalent=no`, `confidence=low`

Key unknowns and assumptions:

1. Unknown: residual GS-02/GS-03 drift appears dominated by execution/strategy-semantic differences, not valuation extraction alone.
2. Assumption: native valuation source should remain transparent (`valuation_fidelity=native_mark_to_market`) and must not regress to shadow metrics for item-76 closure.
3. Assumption: tolerance thresholds from v8.3/v8.4 remain authoritative unless explicitly revised via governance decision.

## Goals

1. Replace shadow valuation dependency with native-only valuation extraction for full-native GS-02/GS-03 paths.
2. Preserve reproducible benchmark evidence and explicit confidence/equivalence metadata.
3. Drive GS-02/GS-03 back within tolerance under native-only valuation before declaring item 76 complete.

## Non-Goals

1. Changing tolerance thresholds to force closure without technical parity improvements.
2. Declaring ADR-011 adoption upgrade before native-only tolerance pass is achieved.

## Phased Plan

### Phase 1: Baseline and Design Alignment

**Goal:** confirm source-of-truth constraints, current drift profile, and closure criteria.

Deliverables:

- [x] Re-reviewed roadmap, archived plans, benchmark harness, adapter implementation, and evaluation/ADR docs.
- [x] Confirmed item-76 closure condition: native-only valuation plus tolerance pass.

Dependencies/Risks:

1. Dependency on reproducible benchmark harness data and scenario definitions.
2. Risk of conflating valuation extraction drift with execution semantics drift.

Validation:

- [x] Baseline artifact inspected and deltas classified by tolerance gate output.

### Phase 2: Native-Only Valuation Path Implementation

**Goal:** remove full-native GS-02/GS-03 dependence on Backtrader shadow metrics.

Deliverables:

- [x] Replaced `_build_full_native_shadow_metrics(...)` wiring for GS-02/GS-03 full-native paths.
- [x] Added native mark-to-market valuation metadata:
  - `valuation_fidelity=native_mark_to_market`
  - `metric_source=nautilus_portfolio_total_pnl_primary_bar`
- [x] Retained deterministic non-shadow fallback only for missing valuation samples.

Dependencies/Risks:

1. Dependency on Nautilus portfolio PnL API behavior consistency.
2. Risk of incorrect cross-symbol bar alignment causing signal skew.

Validation:

- [x] `uv run ruff check finbot/adapters/nautilus/nautilus_adapter.py`
- [x] `uv run pytest tests/unit/test_nautilus_adapter.py -q`

### Phase 3: Native Strategy Semantics Convergence (Wave 1)

**Goal:** reduce native-only drift without reintroducing shadow valuation.

Deliverables:

- [x] Added synchronized multi-symbol bar sampling for full-native GS-02/GS-03 paths.
- [x] Added Backtrader-like period gating adjustments and volatility computation alignment attempts.
- [x] Preserved explicit fidelity metadata and tolerance-gated classification flow.

Dependencies/Risks:

1. Risk that deeper engine execution semantics still diverge from Backtrader despite local logic alignment.
2. Risk that further changes increase complexity without tolerance improvement.

Validation:

- [x] Adapter unit tests remain green after convergence changes.

### Phase 4: Evidence Refresh and Decision Sync

**Goal:** publish current measured state and update planning/decision docs.

Deliverables:

- [x] Regenerated benchmark artifacts (`--samples 3 --scenario all`) with native-only valuation path.
- [x] Updated roadmap item-76 status and active plan reference.
- [ ] Update evaluation + ADR narrative to reflect current native-only non-equivalence state.
- [ ] Achieve tolerance-pass native-only GS-02/GS-03 evidence (closure condition for item 76).

Dependencies/Risks:

1. Risk of long benchmark runtime slowing iteration.
2. Risk of documentation drift if artifact numbers are updated without roadmap/ADR sync.

Validation:

- [x] `uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all`

### Phase 5: Closure / Roll-Forward Decision

**Goal:** either close item 76 or formally roll forward unresolved parity work.

Deliverables:

- [ ] If tolerance pass achieved: mark roadmap item 76 complete and update ADR decision posture.
- [ ] If tolerance still fails: keep item 76 open, publish residual risk/next-step remediation scope.

## High-Level Timeline and Milestones

1. **M1 (2026-02-20):** native-only valuation extraction implemented.
2. **M2 (2026-02-20):** synchronization and parity-convergence wave 1 implemented.
3. **M3 (2026-02-20):** refreshed native-only artifact published.
4. **M4 (next cycle):** full tolerance closure or explicit roll-forward to next remediation item.

## Rollout / Rollback

Rollout:

1. Keep native-only valuation code path active in full-native GS-02/GS-03 runs.
2. Continue benchmark publication using tolerance-gated classification.
3. Maintain roadmap/ADR/evaluation sync per artifact refresh.

Rollback:

1. Re-enable shadow valuation wiring only if native valuation extraction is operationally broken (not for parity convenience).
2. Restore `valuation_fidelity=shadow_backtrader` tags if rollback is required.
3. Reopen remediation item and document rationale in roadmap + ADR.
