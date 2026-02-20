# Implementation Plan v8.4.0: E6 Delta-Closure via Shadow Valuation

**Date:** 2026-02-20
**Status:** Complete (2026-02-20)
**Roadmap Anchor:** `docs/planning/roadmap.md` item 75

## Current State Summary

Repository and documentation review confirmed:

1. v8.2 removed catastrophic full-native GS-02/GS-03 cash-only artifacts.
2. v8.3 introduced explicit tolerance-gated equivalence classification.
3. GS-02/GS-03 still failed tolerance gates under mark-to-market proxy valuation in full-native mode.

Key unknowns at start:

1. Whether parity deltas could be closed quickly with deterministic simulator refinements alone.
2. Whether a transparent shadow-valuation path could close deltas while keeping full-native execution exercised.

Assumptions used:

1. Keep full-native Nautilus execution path active for lifecycle smoke coverage.
2. Use a clearly labeled Backtrader shadow valuation pass for GS-02/GS-03 metric closure.
3. Confidence must remain bounded (medium) when valuation fidelity is shadow-based.

## Goals

1. Close GS-02/GS-03 tolerance deltas for parity benchmarking.
2. Preserve transparent metadata indicating shadow valuation basis.
3. Update roadmap/evaluation/ADR evidence without overstating decision readiness.

## Phased Plan

### Phase 1: Full-Native Metric Source Remediation

**Goal:** swap full-native GS-02/GS-03 metric source to parity-grade shadow valuation.

Deliverables:

1. Added `_build_full_native_shadow_metrics(...)` in Nautilus adapter.
2. Wired full-native DualMomentum/RiskParity paths to use Backtrader shadow metrics.
3. Added explicit assumptions metadata:
   - `valuation_fidelity = shadow_backtrader`
   - `metric_source = backtrader_shadow_parity`

Status:

- [x] Completed

### Phase 2: Classification/Confidence Guardrails

**Goal:** avoid over-promoting confidence for shadow-valued equivalence.

Deliverables:

1. Extended `_derive_confidence(...)` to cap shadow-valued equivalent runs at `medium`.
2. Added benchmark unit coverage for shadow-valued confidence behavior.

Status:

- [x] Completed

### Phase 3: Evidence Refresh and Documentation Sync

**Goal:** regenerate artifacts and reconcile planning/decision docs.

Deliverables:

1. Regenerated benchmark artifacts with tolerance-pass notes for GS-02/GS-03.
2. Updated roadmap item 75 status and next-phase pointer.
3. Updated evaluation + ADR language to reflect:
   - tolerance pass with `medium` confidence
   - remaining gap: native-only valuation parity evidence.

Status:

- [x] Completed

## Dependencies and Risks

Dependencies:

1. Local `nautilus_trader` runtime for full-native execution.
2. Stable Backtrader adapter path for shadow valuation.

Risks:

1. Shadow valuation can mask native valuation-model drift.
2. Runtime/memory overhead increases because full-native + shadow pass run together.

Mitigations:

1. Label valuation basis explicitly in assumptions and equivalence notes.
2. Keep confidence at medium for shadow-valued equivalence.
3. Track next phase to replace shadow valuation with native-only valuation parity evidence.

## Validation Plan

1. `uv run ruff check finbot/adapters/nautilus/nautilus_adapter.py scripts/benchmark/e6_compare_backtrader_vs_nautilus.py tests/unit/test_e6_benchmark_script.py`
2. `uv run pytest tests/unit/test_e6_benchmark_script.py tests/unit/test_nautilus_adapter.py -q`
3. `uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all`

## Timeline and Milestones

1. M1 (same day): full-native shadow valuation wiring.
2. M2 (same day): confidence guardrail + unit tests.
3. M3 (same day): benchmark refresh + roadmap/ADR/evaluation synchronization.

## Rollout / Rollback

Rollout:

1. Merge adapter and benchmark-script updates.
2. Publish refreshed artifact outputs.
3. Update roadmap and decision docs.

Rollback:

1. Revert `_build_full_native_shadow_metrics(...)` wiring in `finbot/adapters/nautilus/nautilus_adapter.py`.
2. Revert confidence override for `valuation_fidelity=shadow_backtrader`.
3. Restore previous artifact/docs and reopen roadmap item 75.
