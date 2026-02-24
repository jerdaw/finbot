# ADR-011: NautilusTrader Adoption Decision

**Status:** Accepted
**Date:** 2026-02-19
**Last Updated:** 2026-02-23
**Deciders:** Project maintainer team
**Epic:** E6 - NautilusTrader Pilot and Decision Gate

## Context

Finbot completed E0-E5 with a stable Backtrader-based engine-agnostic path. During E6, the Nautilus adapter was hardened into a contract-compliant pilot path.

Post-E6 follow-up now includes GS-01/GS-02/GS-03 benchmark evidence with tolerance-gated classification and fidelity labels.

Current evidence mix:

- GS-01: native Nautilus buy-and-hold path (`native_nautilus`) with high-confidence equivalence labeling.
- GS-02/GS-03: full-native execution with native-only valuation extraction (`valuation_fidelity=native_mark_to_market`), currently non-equivalent and low confidence under tolerance gates.
- Backtrader remains parity-gated and stable across all golden strategies.

## Vision Alignment (2026-02-23)

Finbot's primary mission is testfol.io-style portfolio backtesting. Backtrader is confirmed as the primary engine for this workflow — it is mature, stable, and parity-gated across all golden strategies.

Nautilus remains available as an experimental adapter for future live-trading use cases if/when the project scope expands. Chasing native-only valuation parity for GS-02/GS-03 is not aligned with the current project direction and is formally deferred.

## Decision

**Chosen option: Defer final Go/No-Go adoption decision (reconfirmed after native-only valuation evidence refresh). Formally deferred as of 2026-02-23 per vision alignment.**

Backtrader remains default engine. Nautilus remains experimental/pilot.

## Decision Drivers

- Multi-scenario evidence breadth is strong (GS-01/02/03 rows continuously published).
- Native-only valuation dependency replacement is implemented for GS-02/GS-03.
- GS-02/GS-03 currently fail established tolerance thresholds under native-only valuation, so adoption confidence remains low.
- Backtrader remains stable, parity-gated, and sufficient for current roadmap objectives.
- Operational risk from early dual-engine peer support remains higher than validated near-term benefit.

## Measured Evidence Snapshot

From `docs/research/artifacts/e6-benchmark-2026-02-20.json` (generated 2026-02-20, `--samples 3 --scenario all`):

| Engine | Scenario | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| Backtrader | `gs01` | `native_backtrader` | Yes | High | 0.4622 | 1.22 | 0.5584 |
| Nautilus pilot | `gs01` | `native_nautilus` | Yes | High | 0.2775 | 0.74 | 0.4936 |
| Backtrader | `gs02` | `native_backtrader` | Yes | High | 5.6195 | 3.60 | 1.0003 |
| Nautilus pilot | `gs02` | `native_nautilus_full` | No | Low | 22.5765 | 5.65 | 0.8963 |
| Backtrader | `gs03` | `native_backtrader` | Yes | High | 8.6989 | 7.81 | 4.2750 |
| Nautilus pilot | `gs03` | `native_nautilus_full` | No | Low | 18.3425 | 9.40 | 2.9933 |

Interpretation: native-only valuation extraction is operational, but GS-02/GS-03 economic parity remains outside tolerance.

## Considered Options

### Option A: Go now (full Nautilus adoption)

Rejected because GS-02/GS-03 remain non-equivalent under native-only valuation evidence.

### Option B: No-Go now (abandon Nautilus)

Rejected because adapter-first architecture still preserves optionality and pilot investment remains useful.

### Option C: Hybrid now (support both as peers)

Rejected because this adds maintenance and CI complexity without decision-grade multi-scenario native parity.

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
- Keeps follow-up work measurable with explicit tolerance outputs.
- Avoids premature migration commitments.

### Negative

- Definitive Nautilus adoption remains delayed.
- Additional remediation is still required to close GS-02/GS-03 native-only parity gaps.

## Follow-up Actions

1. Reduce GS-02/GS-03 native-only deltas (ROI/drawdown/ending value) to pass tolerance gates.
2. Re-run multi-scenario benchmark artifacts after each remediation wave and re-evaluate confidence.
3. Revisit ADR-011 only after native-only valuation parity evidence materially improves.

## Post-E6 Follow-up Tracker

- [x] GS-01 like-for-like native benchmark row published (2026-02-19).
- [x] GS-02 comparison row published (2026-02-20).
- [x] GS-03 comparison row published (2026-02-20).
- [x] Full-native GS-02/GS-03 strategy paths implemented with proxy fallback + fidelity tags (2026-02-20).
- [x] GS-02/GS-03 tolerance-gated equivalence classification automated in benchmark artifacts (2026-02-20).
- [x] GS-02/GS-03 native-only valuation extraction path implemented (`native_mark_to_market`) (2026-02-20).
- [~] GS-02/GS-03 native-only tolerance closure achieved — **formally deferred (2026-02-23)**. Backtrader confirmed as primary engine for portfolio backtesting; native-only parity is not required for current project direction. Nautilus adapter preserved for future live-trading exploration.
- [x] CI budget tiering implemented for PR-vs-heavy quality gates (2026-02-19).
- [x] Final decision refresh after multi-scenario evidence review (decision remains Defer).

## Validation Criteria for Future Revisit

- Full-native Nautilus execution for GS-02/GS-03 is operational and economically equivalent within agreed tolerance using native-only valuation.
- Comparable metrics (return/drawdown/trades/runtime/memory) are published with improved confidence labels.
- Operational overhead (install/debug/CI) remains acceptable under sustained usage.

## References

- `docs/research/nautilus-pilot-evaluation.md`
- `docs/research/artifacts/e6-benchmark-2026-02-20.json`
- `docs/planning/IMPLEMENTATION_PLAN_8.5_E6_NATIVE_ONLY_VALUATION_PARITY_CLOSURE.md`
- `finbot/adapters/nautilus/nautilus_adapter.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
