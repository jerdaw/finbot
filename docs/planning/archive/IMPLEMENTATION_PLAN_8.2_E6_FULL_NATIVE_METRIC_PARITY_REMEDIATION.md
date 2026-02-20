# Implementation Plan v8.2.0: E6 Full-Native Metric Parity Remediation

**Date:** 2026-02-20
**Status:** Complete (2026-02-20)
**Roadmap Anchor:** `docs/planning/roadmap.md` item 73

## Current State Summary

Repository and documentation review confirmed:

1. E0-E6 delivery remains complete with ADR-011 in `Defer`.
2. GS-02/GS-03 full-native Nautilus paths existed, but benchmark artifacts showed catastrophic outcomes (`~ -99.8% ROI`) due to cash-only metric interpretation.
3. The native result mapper (`_map_nautilus_metrics`) consumed realized/cash-like PnL stats and did not include open-position mark-to-market valuation.
4. Proxy-native GS-02/GS-03 results were materially healthier than full-native rows, indicating metrics extraction/mapping mismatch rather than pure strategy failure.

Key unknowns at start:

1. Whether Nautilus exposes direct total portfolio/equity fields suitable for contract metrics (it does not in a usable form for these runs).
2. Whether strategy logic mismatch or metric mapping mismatch was the primary drift driver (mapping mismatch proved primary for catastrophic artifacts).

Assumptions used:

1. Full-native execution should remain enabled and exercised.
2. Portfolio metrics for contract parity may be derived from deterministic shadow mark-to-market equity on aligned close bars when native result objects do not expose full equity curves.

## Goals

1. Remove catastrophic full-native GS-02/GS-03 metric drift caused by cash-only valuation.
2. Preserve full-native execution path while producing realistic mark-to-market metrics.
3. Refresh benchmark artifacts and update roadmap/docs with validated evidence.

## Phased Plan

### Phase 1: Diagnosis and Acceptance Baseline

**Goal:** verify root cause and define acceptance criteria.

Deliverables:

1. Confirmed root cause via direct Nautilus run inspection: ending cash and realized PnL omitted open-position value.
2. Defined remediation acceptance:
   - No near-zero `ending_value` artifacts on GS-02/GS-03.
   - No `~ -99%` ROI artifacts from cash-only accounting.
   - Full-native path remains active (`adapter_mode = native_nautilus_full`).

Status:

- [x] Completed

### Phase 2: Metric Remediation Implementation

**Goal:** make full-native GS-02/GS-03 metrics mark-to-market and reusable.

Deliverables:

1. Added shared shadow portfolio simulators:
   - `_simulate_dual_momentum_portfolio(...)`
   - `_simulate_risk_parity_portfolio(...)`
2. Added cash-utilization utility:
   - `_compute_mean_cash_utilization(...)`
3. Extended `_build_metrics_from_equity_curve(...)` to accept optional `cash_curve`.
4. Switched GS-02/GS-03 full-native methods to use mark-to-market shadow equity metrics while retaining full-native Nautilus execution.
5. Refactored proxy GS-02/GS-03 paths to use the same shared simulators for consistency.
6. Added targeted unit tests for new helper behavior and metric output.

Status:

- [x] Completed

### Phase 3: Evidence Refresh and Documentation Sync

**Goal:** regenerate evidence and update planning/decision documents.

Deliverables:

1. Refreshed benchmark artifacts:
   - `docs/research/artifacts/e6-benchmark-2026-02-20.json`
   - `docs/research/artifacts/e6-benchmark-2026-02-20.md`
2. Updated evaluation and ADR references to the remediated evidence.
3. Updated roadmap item 73 status and current phase pointers.

Status:

- [x] Completed

## Dependencies and Risks

Dependencies:

1. Local Nautilus installation (`nautilus_trader`) for full-native scenario execution.
2. Available historical parquet datasets for SPY/QQQ/TLT.

Risks:

1. Shadow mark-to-market metrics still differ from Backtrader due execution model differences (close-fill simplification vs engine-specific semantics).
2. Confidence classification remains low while `strategy_equivalent` remains false.

Mitigations:

1. Keep confidence/equivalence metadata explicit.
2. Track next follow-up for tolerance formalization and automatic equivalence classification.

## Validation Plan

1. `uv run pytest tests/unit/test_nautilus_adapter.py tests/unit/test_e6_benchmark_script.py -q`
2. `uv run ruff check finbot/adapters/nautilus/nautilus_adapter.py tests/unit/test_nautilus_adapter.py`
3. `uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all`

## Timeline and Milestones

1. M1 (same day): root-cause diagnosis and acceptance baseline.
2. M2 (same day): code remediation + unit tests.
3. M3 (same day): benchmark refresh + roadmap/doc synchronization.

## Rollout / Rollback

Rollout:

1. Merge adapter/test changes.
2. Refresh and publish benchmark artifacts.
3. Update roadmap and evaluation/ADR docs to the new evidence.

Rollback:

1. Revert adapter helper/simulation wiring in `finbot/adapters/nautilus/nautilus_adapter.py`.
2. Restore previous benchmark artifacts and associated doc sections.
3. Re-mark roadmap item 73 as in progress if catastrophic drift returns.
