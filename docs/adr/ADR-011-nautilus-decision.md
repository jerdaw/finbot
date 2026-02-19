# ADR-011: NautilusTrader Adoption Decision

**Status:** Accepted
**Date:** 2026-02-19
**Deciders:** Project maintainer team
**Epic:** E6 - NautilusTrader Pilot and Decision Gate

## Context

Finbot completed E0-E5 with a stable Backtrader-based engine-agnostic path. During E6, the previous Nautilus adapter skeleton was not contract-compliant and was hardened into a valid pilot path.

Post-E6 phase 2 has now expanded measurable evidence from GS-01 only to GS-01/GS-02/GS-03.

Current evidence mix:

- GS-01: native Nautilus buy-and-hold path (`native_nautilus`) with high-confidence equivalence labeling.
- GS-02/GS-03: deterministic proxy-native Nautilus pilot paths (`native_nautilus_proxy`) with medium-confidence equivalence labeling.
- Backtrader remains parity-gated and stable across all golden strategies.

## Decision

**Chosen option: Defer final Go/No-Go adoption decision (reconfirmed after GS-01/GS-02/GS-03 evidence refresh).**

Backtrader remains default engine. Nautilus remains experimental/pilot.

## Decision Drivers

- Multi-scenario evidence breadth is now substantially better (GS-01/02/03 rows published).
- GS-02/GS-03 evidence uses proxy-native execution assumptions, lowering confidence versus full native lifecycle equivalence.
- Backtrader remains stable, parity-gated, and currently sufficient for roadmap objectives.
- Operational risk from early dual-engine peer support remains higher than validated near-term benefit.

## Measured Evidence Snapshot

From `docs/research/artifacts/e6-benchmark-2026-02-19.json`:

| Engine | Scenario | Mode | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Backtrader | `gs01` | `native_backtrader` | High | 0.4613 | 1.22 | 0.5584 |
| Nautilus pilot | `gs01` | `native_nautilus` | High | 0.2788 | 0.74 | 0.4936 |
| Backtrader | `gs02` | `native_backtrader` | High | 5.5421 | 3.60 | 1.0003 |
| Nautilus pilot | `gs02` | `native_nautilus_proxy` | Medium | 0.5451 | 1.24 | 0.8963 |
| Backtrader | `gs03` | `native_backtrader` | High | 8.7398 | 7.82 | 4.2750 |
| Nautilus pilot | `gs03` | `native_nautilus_proxy` | Medium | 0.9925 | 2.25 | 2.9933 |

Interpretation: evidence breadth is improved and sufficient for a decision refresh, but not sufficient for a migration decision upgrade because GS-02/GS-03 are still medium-confidence proxy-native rows.

## Considered Options

### Option A: Go now (full Nautilus adoption)

Rejected due to medium-confidence proxy-native evidence for two of three golden scenarios.

### Option B: No-Go now (abandon Nautilus)

Rejected because adapter-first architecture still preserves optionality and pilot investment remains useful.

### Option C: Hybrid now (support both as peers)

Rejected because this adds maintenance and CI complexity without decision-grade full-native evidence.

### Option D: Defer (chosen)

Accepted as the highest-information, lowest-risk path under current constraints.

## Tradeoff Matrix

| Criterion | Go Now | No-Go Now | Hybrid Now | Defer (Chosen) |
| --- | --- | --- | --- | --- |
| Delivery risk | High | Low | High | Low |
| Evidence quality | Medium | Medium | Medium | High (for defer rationale) |
| Maint. complexity | Medium | Low | High | Medium |
| Strategic optionality | High | Low | High | High |
| Fits current constraints | Partial | Partial | No | Yes |

## Consequences

### Positive

- Preserves current delivery stability and parity gate posture.
- Converts follow-up work into measurable multi-scenario evidence.
- Avoids premature migration commitments.

### Negative

- Definitive Nautilus adoption remains delayed.
- Additional future work is required for full-native GS-02/GS-03 evidence.

## Follow-up Actions

1. Implement full native (non-proxy) GS-02/GS-03 strategy execution paths.
2. Re-run multi-scenario benchmark artifacts under those paths.
3. Revisit ADR-011 only after full-native confidence improves.

## Post-E6 Follow-up Tracker

- [x] GS-01 like-for-like native benchmark row published (2026-02-19).
- [x] GS-02 comparison row published (2026-02-19, medium-confidence proxy-native).
- [x] GS-03 comparison row published (2026-02-19, medium-confidence proxy-native).
- [x] CI budget tiering implemented for PR-vs-heavy quality gates (2026-02-19).
- [x] Final decision refresh after multi-scenario evidence review (2026-02-19, decision remains Defer).

## Validation Criteria for Future Revisit

- Full native (non-proxy) Nautilus execution succeeds for GS-02 and GS-03.
- Comparable metrics (return/drawdown/trades/runtime/memory) are published with high-confidence labels.
- Operational overhead (install/debug/CI) remains acceptable under sustained usage.

## References

- `docs/research/nautilus-pilot-evaluation.md`
- `docs/research/artifacts/e6-benchmark-2026-02-19.json`
- `docs/planning/archive/IMPLEMENTATION_PLAN_7.1_POST_E6_PHASE2_MULTI_SCENARIO_EVIDENCE.md`
- `finbot/adapters/nautilus/nautilus_adapter.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
