# NautilusTrader Pilot Evaluation

**Date:** 2026-02-20
**Status:** Updated with native-only valuation evidence (item 76 in progress)
**Epic:** E6-T2 (Comparative Evaluation Report)

## Executive Summary

The pilot adapter remains contract-compliant and test-covered, with benchmark evidence across GS-01, GS-02, and GS-03.

**Recommendation:** **Defer** final adoption decision.

**Key Finding:** GS-01 remains high-confidence and stable. GS-02/GS-03 now use native-only valuation (`native_mark_to_market`) in full-native mode, but currently fail tolerance gates (`equivalent=no`, `confidence=low`).

## 1. Scope Completed in This Slice

- Maintained `NautilusAdapter.run(request)` contract compliance.
- Kept strategy coverage for evaluation scenarios:
  - `NoRebalance` native buy-and-hold path.
  - `DualMomentum` and `RiskParity` full-native-first execution with proxy fallback.
- Implemented native-only valuation extraction for GS-02/GS-03 full-native runs.
- Added synchronized multi-symbol bar sampling in full-native GS-02/GS-03 valuation flow.
- Preserved explicit metadata for confidence/equivalence, adapter mode, and fidelity tagging.

## 2. Comparison Status: Backtrader vs Nautilus

### 2.1 Evidence Available

- **Backtrader path:** fully operational, parity-gated, baseline-stable.
- **Nautilus GS-01:** native path with high-confidence equivalence labeling.
- **Nautilus GS-02/GS-03:** full-native execution with native-only valuation extraction and tolerance-gated classification (currently failing thresholds).
- **Artifacts:** single multi-scenario JSON/Markdown output containing all three golden scenarios.

### 2.2 Evidence Gaps Remaining (for final adoption)

- Native-only GS-02/GS-03 parity closure within established tolerance gates.
- Additional evidence that execution/strategy semantics can converge without shadow valuation dependency.
- Broader operational data for sustained CI/debug burden at larger strategy coverage.

## 3. Measured Output (Current State)

Benchmarks were generated with:

```bash
uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all
```

Artifact outputs:
- `docs/research/artifacts/e6-benchmark-2026-02-20.json`
- `docs/research/artifacts/e6-benchmark-2026-02-20.md`

| Engine | Scenario ID | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Backtrader | `gs01` | `native_backtrader` | Yes | High | 0.4622 | 1.22 | 0.5584 | 0.2478 | -0.3350 | 155840.34 |
| Nautilus pilot | `gs01` | `native_nautilus` | Yes | High | 0.2775 | 0.74 | 0.4936 | 0.2226 | -0.3406 | 149356.30 |
| Backtrader | `gs02` | `native_backtrader` | Yes | High | 5.6195 | 3.60 | 1.0003 | 0.0441 | -0.2725 | 200027.71 |
| Nautilus pilot | `gs02` | `native_nautilus_full` | No | Low | 22.5765 | 5.65 | 0.8963 | 0.0405 | -0.3407 | 189627.74 |
| Backtrader | `gs03` | `native_backtrader` | Yes | High | 8.6989 | 7.81 | 4.2750 | 0.1090 | -0.2932 | 527504.83 |
| Nautilus pilot | `gs03` | `native_nautilus_full` | No | Low | 18.3425 | 9.40 | 2.9933 | 0.0898 | -0.3130 | 399328.43 |

Interpretation:
- Coverage breadth remains complete for the three frozen scenarios.
- Native-only valuation extraction is now active for GS-02/GS-03 full-native rows.
- GS-02/GS-03 currently fail tolerance gates, so confidence remains low and adoption posture is unchanged.

## 4. Operational Readiness Assessment

### Ready now

- Contract-level adapter API stability.
- Multi-scenario benchmark harness with confidence/equivalence metadata.
- Native-only valuation extraction path for full-native GS-02/GS-03 rows.

### Not ready

- Production-native Nautilus parity claims for GS-02/GS-03.
- Migration recommendation to replace Backtrader as default engine.

## 5. Recommendation

**Decision input to ADR-011:** **Defer**.

Rationale: native-only valuation dependency has been removed, but GS-02/GS-03 still miss parity thresholds under established tolerance gates.

## 6. Next Evidence Required for Go/No-Go Upgrade

1. Reduce GS-02/GS-03 native-only ROI/drawdown/ending-value deltas to pass tolerance gates.
2. Re-run benchmark artifacts with native-only valuation and upgraded confidence only after tolerance pass.
3. Extend operational overhead assessment over sustained CI/debug cycles.

## References

- `finbot/adapters/nautilus/nautilus_adapter.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
- `tests/unit/test_nautilus_adapter.py`
- `tests/unit/test_e6_benchmark_script.py`
- `docs/research/artifacts/e6-benchmark-2026-02-20.json`
- `docs/adr/ADR-011-nautilus-decision.md`
