# Implementation Plan v8.3.0: E6 Equivalence-Tolerance Formalization

**Date:** 2026-02-20
**Status:** Complete (2026-02-20)
**Roadmap Anchor:** `docs/planning/roadmap.md` item 74

## Current State Summary

Repository and documentation review confirmed:

1. Item 73 remediation removed catastrophic GS-02/GS-03 cash-only artifacts and restored realistic full-native mark-to-market metrics.
2. Benchmark confidence/equivalence labels were still predominantly assumption-driven for GS-02/GS-03.
3. ADR/evaluation posture remained `Defer`, but lacked explicit numeric tolerance gates in the benchmark classifier for GS-02/GS-03.

Key unknowns at start:

1. Whether current remediated GS-02/GS-03 medians would pass practical first-pass tolerances (they did not).
2. Which metrics should be tolerance-gated first for decision-grade comparability without overfitting.

Assumptions used:

1. GS-02/GS-03 tolerance gates should be explicit and deterministic in the benchmark script.
2. Confidence should remain automation-derived from measured equivalence plus execution fidelity.

## Goals

1. Define explicit numeric tolerances for GS-02/GS-03 parity classification.
2. Automate GS-02/GS-03 equivalence/confidence classification from measured median deltas.
3. Refresh benchmark artifacts and synchronize roadmap/evaluation/ADR evidence.

## Phased Plan

### Phase 1: Tolerance Model and Classification Wiring

**Goal:** embed deterministic tolerance gates into benchmark summarization.

Deliverables:

1. Added `EquivalenceTolerance` model in benchmark harness.
2. Added scenario tolerance profiles for `gs02` and `gs03`.
3. Implemented delta evaluation helpers (`roi_abs`, `cagr_abs`, `max_drawdown_abs`, `ending_value_relative`).
4. Added post-summary tolerance application that rewrites Nautilus `strategy_equivalent`, `confidence`, and equivalence notes.

Status:

- [x] Completed

### Phase 2: Verification and Artifact Refresh

**Goal:** verify behavior and regenerate authoritative outputs.

Deliverables:

1. Added/updated unit tests for tolerance evaluation and classification application.
2. Ran targeted lint and tests.
3. Regenerated E6 benchmark artifacts with tolerance-gated notes.

Status:

- [x] Completed

### Phase 3: Documentation and Roadmap Synchronization

**Goal:** publish updated decision/evaluation context and progress tracking.

Deliverables:

1. Updated `docs/research/nautilus-pilot-evaluation.md` with tolerance-gated interpretation and refreshed metrics table.
2. Updated `docs/adr/ADR-011-nautilus-decision.md` with refreshed evidence snapshot and follow-up tracker entry.
3. Updated roadmap status/checklist entries for item 74 and current phase pointers.

Status:

- [x] Completed

## Dependencies and Risks

Dependencies:

1. Local `nautilus_trader` runtime for full-native benchmark execution.
2. Historical parquet datasets for SPY/QQQ/TLT.

Risks:

1. Tolerance thresholds may be too permissive or too strict relative to long-run decision needs.
2. Passing/failing thresholds alone does not isolate root-cause drift drivers.

Mitigations:

1. Keep tolerance values explicit and version-controlled in the benchmark script.
2. Preserve detailed equivalence notes that include per-metric deltas and failed checks.

## Validation Plan

1. `uv run ruff check scripts/benchmark/e6_compare_backtrader_vs_nautilus.py tests/unit/test_e6_benchmark_script.py`
2. `uv run pytest tests/unit/test_e6_benchmark_script.py tests/unit/test_nautilus_adapter.py -q`
3. `uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all`

## Timeline and Milestones

1. M1 (same day): tolerance model committed and classification wired.
2. M2 (same day): tests/lint green and artifacts regenerated.
3. M3 (same day): roadmap, evaluation, and ADR synchronized.

## Rollout / Rollback

Rollout:

1. Merge benchmark-script tolerance logic and associated unit tests.
2. Publish refreshed JSON/Markdown artifacts.
3. Update roadmap + decision/evaluation docs.

Rollback:

1. Revert tolerance-gated classification helpers in `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`.
2. Restore prior artifacts and documentation references.
3. Reopen roadmap item 74 as in progress.
