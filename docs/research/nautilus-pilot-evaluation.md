# NautilusTrader Pilot Evaluation

**Date:** 2026-02-19
**Status:** Updated with post-E6 follow-up GS-01 like-for-like benchmark evidence
**Epic:** E6-T2 (Comparative Evaluation Report)

## Executive Summary

This evaluation confirms that the pilot adapter path is now contract-compliant and test-covered, and that native Nautilus execution is wired for a narrow pilot scenario with explicit fallback protection.

**Recommendation:** **Defer** final adoption decision until broader like-for-like strategy benchmarking is completed.

**Key Finding:** We eliminated contract and integration blockers and now have one like-for-like native GS-01 comparison. Evidence quality improved, but coverage breadth is still insufficient for final engine adoption.

## 1. Scope Completed in This Pilot Slice

- Implemented `NautilusAdapter.run(request)` to satisfy `BacktestEngine`.
- Added canonical metadata/result mapping and pilot validation rules.
- Added explicit warning-tagged fallback behavior instead of `NotImplementedError`.
- Implemented native Nautilus runtime wiring for one pilot scenario (engine, bars, strategy, result mapping).
- Added unit tests for adapter behavior.
- Closed deferred E4 integrations relevant to pilot evidence quality:
  - Snapshot capture wiring in `BacktraderAdapter`.
  - Batch observability wiring in `backtest_batch` (opt-in mode).

## 2. Integration Effort and Complexity

### 2.1 Time Breakdown (current batch)

| Phase | Actual |
| --- | --- |
| Contract alignment + adapter hardening | ~2.5h |
| Snapshot integration + tests | ~1.0h |
| Batch observability integration + tests | ~1.5h |
| Documentation and decision artifacts | ~1.0h |
| **Total** | **~6.0h** |

### 2.2 Complexity Notes

- Most difficult issue: contract drift in pre-existing Nautilus skeleton (method and dataclass shape mismatches).
- Snapshot/batch integrations were straightforward once exact registry paths were confirmed.
- Ongoing complexity is now comparative validation breadth (strategy coverage, parity benchmarking, and operations profiling).

## 3. Comparison Status: Backtrader vs Nautilus

This report is intentionally split by evidence strength.

### 3.1 Evidence Available (High confidence)

- **Backtrader path:** fully operational and parity-gated.
- **Nautilus pilot adapter contract:** operational and test-covered.
- **Nautilus native pilot path:** operational for a one-symbol pilot scenario.
- **Like-for-like GS-01 comparison:** available via native `NoRebalance` buy-and-hold mapping with confidence-tagged artifact output.
- **Reproducibility and batch tracking foundations:** now integrated for better future evaluation quality.

### 3.2 Evidence Not Yet Available (Blocking final decision)

- Equivalent native comparisons for GS-02 and GS-03.
- Native fill/latency behavior comparison against current simulator + Backtrader baseline at broader strategy scope.

## 4. Measured Pilot Output (Current State)

### 4.1 Contract/Integration Metrics

| Metric | Result |
| --- | --- |
| Adapter method compliance (`run`) | ✅ |
| Canonical metadata/result construction | ✅ |
| Rebalance-only pilot validation | ✅ |
| Fallback warnings/artifact tagging | ✅ |
| Snapshot auto-attachment support | ✅ |
| Batch lifecycle/error tracking in `backtest_batch` | ✅ |

### 4.2 Quantitative Performance/Fidelity Metrics

Benchmarks were generated with:

```bash
uv run python scripts/benchmark/e6_compare_backtrader_vs_nautilus.py --samples 3 --scenario gs01
```

Artifact outputs:
- `docs/research/artifacts/e6-benchmark-2026-02-19.json`
- `docs/research/artifacts/e6-benchmark-2026-02-19.md`

| Engine | Scenario | Scenario ID | Samples | Mode | Equivalent | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value | Confidence |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Backtrader | SPY 2019-2020 buy-and-hold | `gs01` | 3 | `native_backtrader` | Yes | 0.4689 | 1.22 | 0.5584 | 0.2478 | -0.3350 | 155840.34 | High |
| Nautilus pilot | SPY 2019-2020 native run | `gs01` | 3 | `native_nautilus` | Yes | 0.2802 | 0.74 | 0.4936 | 0.2226 | -0.3406 | 149356.30 | High |

Interpretation:
- Runtime and memory numbers are measured and reproducible.
- Scenario is now strategy-equivalent for GS-01 (single-symbol buy-and-hold), improving decision evidence quality.
- Remaining metric deltas indicate implementation differences that still require wider scenario coverage before changing ADR-011.

## 5. Operational Readiness Assessment

### Ready now

- Contract-level adapter API stability.
- Reproducibility and observability primitives needed for a fair next evaluation pass.

### Not ready

- Native Nautilus production or parity claims.
- Migration recommendation to replace Backtrader.

## 6. Recommendation

**Decision input to ADR-011:** **Defer**.

Proceed with a follow-up slice that expands strategy/dataset coverage and publishes repeatable runtime/fidelity comparisons.

## 7. Next Evidence Required for Go/No-Go

1. Repeatable native Nautilus run success for GS-02 and GS-03.
2. Side-by-side metric deltas and tolerance interpretation across all golden scenarios.
3. Runtime/memory benchmark under repeatable conditions for each golden scenario.
4. Documented operational complexity (install, debug, CI impact) for expanded coverage.

## References

- `finbot/adapters/nautilus/nautilus_adapter.py`
- `finbot/services/backtesting/adapters/backtrader_adapter.py`
- `finbot/services/backtesting/backtest_batch.py`
- `tests/unit/test_nautilus_adapter.py`
- `tests/unit/test_backtrader_adapter.py`
- `tests/unit/test_backtest_batch_observability.py`
- `docs/research/artifacts/e6-benchmark-2026-02-19.json`
- `docs/adr/ADR-011-nautilus-decision.md`
