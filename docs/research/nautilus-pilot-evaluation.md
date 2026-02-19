# NautilusTrader Pilot Evaluation

**Date:** 2026-02-19
**Status:** Completed for current pilot scope (fallback-mode evidence)
**Epic:** E6-T2 (Comparative Evaluation Report)

## Executive Summary

This evaluation confirms that the pilot adapter path is now contract-compliant and test-covered, but it is still running through an explicit Backtrader fallback mode rather than native Nautilus execution.

**Recommendation:** **Defer** final adoption decision until native Nautilus execution is implemented and benchmarked.

**Key Finding:** We eliminated contract and integration blockers (adapter interface drift, snapshot and batch observability gaps), but we do not yet have native Nautilus performance/fidelity evidence.

## 1. Scope Completed in This Pilot Slice

- Implemented `NautilusAdapter.run(request)` to satisfy `BacktestEngine`.
- Added canonical metadata/result mapping and pilot validation rules.
- Added explicit warning-tagged fallback behavior instead of `NotImplementedError`.
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
- Native Nautilus integration remains the major complexity item.

## 3. Comparison Status: Backtrader vs Nautilus

This report is intentionally split by evidence strength.

### 3.1 Evidence Available (High confidence)

- **Backtrader path:** fully operational and parity-gated.
- **Nautilus pilot adapter contract:** operational and test-covered.
- **Reproducibility and batch tracking foundations:** now integrated for better future evaluation quality.

### 3.2 Evidence Not Yet Available (Blocking final decision)

- Native Nautilus engine execution with project strategies and frozen datasets.
- True performance/runtime/memory comparison with equivalent strategy logic.
- Native fill/latency behavior comparison against current simulator + Backtrader baseline.

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

Not reported for native Nautilus in this cycle because execution path is fallback-based.

## 5. Operational Readiness Assessment

### Ready now

- Contract-level adapter API stability.
- Reproducibility and observability primitives needed for a fair next evaluation pass.

### Not ready

- Native Nautilus production or parity claims.
- Migration recommendation to replace Backtrader.

## 6. Recommendation

**Decision input to ADR-011:** **Defer**.

Proceed with a narrow follow-up slice that implements native Nautilus execution for one frozen strategy/dataset pair, then rerun this report with true runtime/fidelity numbers.

## 7. Next Evidence Required for Go/No-Go

1. Native Nautilus run success for one golden scenario.
2. Side-by-side metric deltas against Backtrader on identical inputs.
3. Runtime/memory benchmark under repeatable conditions.
4. Documented operational complexity (install, debug, CI impact).

## References

- `finbot/adapters/nautilus/nautilus_adapter.py`
- `finbot/services/backtesting/adapters/backtrader_adapter.py`
- `finbot/services/backtesting/backtest_batch.py`
- `tests/unit/test_nautilus_adapter.py`
- `tests/unit/test_backtrader_adapter.py`
- `tests/unit/test_backtest_batch_observability.py`
- `docs/adr/ADR-011-nautilus-decision.md`
