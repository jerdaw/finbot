# NautilusTrader Pilot Evaluation

**Date:** 2026-02-19
**Status:** Updated with GS-01/GS-02/GS-03 multi-scenario benchmark evidence
**Epic:** E6-T2 (Comparative Evaluation Report)

## Executive Summary

The pilot adapter is contract-compliant and test-covered, with broadened benchmark evidence across GS-01, GS-02, and GS-03.

**Recommendation:** **Defer** final adoption decision.

**Key Finding:** GS-01 has high-confidence native evidence. GS-02/GS-03 now have medium-confidence proxy-native comparability evidence, which improves breadth but is still not sufficient for a full Go decision.

## 1. Scope Completed in This Slice

- Maintained `NautilusAdapter.run(request)` contract compliance.
- Expanded strategy coverage for evaluation scenarios:
  - `NoRebalance` native buy-and-hold path.
  - `DualMomentum` and `RiskParity` deterministic proxy-native pilot paths.
- Added explicit metadata for confidence/equivalence and adapter mode tagging.
- Expanded benchmark harness to run `gs01`, `gs02`, `gs03`, and `all` scenario bundles.
- Added unit coverage for new adapter validations and benchmark scenario wiring.

## 2. Comparison Status: Backtrader vs Nautilus

### 2.1 Evidence Available

- **Backtrader path:** fully operational, parity-gated, and baseline-stable.
- **Nautilus GS-01:** native path with high-confidence equivalence labeling.
- **Nautilus GS-02/GS-03:** proxy-native paths with medium-confidence equivalence labeling.
- **Artifacts:** single multi-scenario JSON/Markdown output containing all three golden scenarios.

### 2.2 Evidence Gaps Remaining (for final adoption)

- Full native Nautilus order-lifecycle parity for GS-02/GS-03 (current mode is proxy-native, not full exchange/order-flow modeling).
- Broader operational data for sustained CI/debug burden at larger strategy coverage.

## 3. Measured Output (Current State)

Benchmarks were generated with:

```bash
uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario all
```

Artifact outputs:
- `docs/research/artifacts/e6-benchmark-2026-02-19.json`
- `docs/research/artifacts/e6-benchmark-2026-02-19.md`

| Engine | Scenario ID | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Backtrader | `gs01` | `native_backtrader` | Yes | High | 0.4613 | 1.22 | 0.5584 | 0.2478 | -0.3350 | 155840.34 |
| Nautilus pilot | `gs01` | `native_nautilus` | Yes | High | 0.2788 | 0.74 | 0.4936 | 0.2226 | -0.3406 | 149356.30 |
| Backtrader | `gs02` | `native_backtrader` | Yes | High | 5.5421 | 3.60 | 1.0003 | 0.0441 | -0.2725 | 200027.71 |
| Nautilus pilot | `gs02` | `native_nautilus_proxy` | Yes | Medium | 0.5451 | 1.24 | 0.8963 | 0.0405 | -0.3407 | 189627.72 |
| Backtrader | `gs03` | `native_backtrader` | Yes | High | 8.7398 | 7.82 | 4.2750 | 0.1090 | -0.2932 | 527504.83 |
| Nautilus pilot | `gs03` | `native_nautilus_proxy` | Yes | Medium | 0.9925 | 2.25 | 2.9933 | 0.0898 | -0.3130 | 399328.53 |

Interpretation:
- Coverage breadth improved from one to three frozen scenarios.
- GS-02/GS-03 deltas remain notable and confidence is medium due proxy-native execution assumptions.
- Evidence is improved and decision-grade for “continue defer” posture, not for full migration.

## 4. Operational Readiness Assessment

### Ready now

- Contract-level adapter API stability.
- Multi-scenario benchmark harness and confidence-labeled artifacts.

### Not ready

- Production-native Nautilus parity claims for GS-02/GS-03.
- Migration recommendation to replace Backtrader as default engine.

## 5. Recommendation

**Decision input to ADR-011:** **Defer**.

Rationale: multi-scenario evidence is now available, but GS-02/GS-03 are medium-confidence proxy-native rows and do not yet justify a full Go/Hybrid adoption state.

## 6. Next Evidence Required for Go/No-Go Upgrade

1. Full native (non-proxy) GS-02 and GS-03 strategy execution with documented order lifecycle behavior.
2. Repeatable side-by-side deltas under the same execution semantics.
3. Operational overhead assessment over sustained CI/debug cycles.

## References

- `finbot/adapters/nautilus/nautilus_adapter.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
- `tests/unit/test_nautilus_adapter.py`
- `tests/unit/test_e6_benchmark_script.py`
- `docs/research/artifacts/e6-benchmark-2026-02-19.json`
- `docs/adr/ADR-011-nautilus-decision.md`
