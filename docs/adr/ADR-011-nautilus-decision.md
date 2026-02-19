# ADR-011: NautilusTrader Adoption Decision

**Status:** Accepted
**Date:** 2026-02-19
**Deciders:** Project maintainer team
**Epic:** E6 - NautilusTrader Pilot and Decision Gate

## Context

Finbot completed E0-E5 with a stable Backtrader-based engine-agnostic path. During E6 we found that the existing Nautilus adapter implementation was not contract-compliant and could not support a meaningful pilot evaluation.

This cycle implemented:

- Contract-aligned Nautilus pilot adapter API (`run`) with canonical result mapping.
- Explicit fallback execution mode to keep pilot path operable.
- Native Nautilus pilot runtime path for one strategy/data shape.
- Snapshot and batch observability integrations needed for stronger future evaluation.

However, comparative evidence remains incomplete across broader strategy coverage, runtime benchmarking, and operational overhead.

## Decision

**Chosen option: Defer final Go/No-Go adoption decision.**

We will keep Backtrader as the default engine and treat Nautilus as an experimental pilot path until native execution evidence is available.

## Decision Drivers

- Native Nautilus benchmark/fidelity data is not yet available.
- Native pilot execution exists, but breadth of comparative evidence is still limited.
- Backtrader path is currently stable, parity-gated, and sufficient for current roadmap goals.
- Newly added snapshot and batch observability integrations reduce risk for a follow-up native Nautilus evaluation.

## Considered Options

### Option A: Go now (full Nautilus adoption)

Rejected for this cycle due to insufficient native evidence.

### Option B: No-Go now (abandon Nautilus)

Rejected because architecture remains adapter-first and future live-readiness value is plausible.

### Option C: Hybrid now (support both as peers)

Rejected because comparative evidence is still limited and full dual-engine support would add maintenance burden without validated net benefit.

### Option D: Defer (chosen)

Accepted as the lowest-risk, highest-information path.

## Consequences

### Positive

- Preserves current delivery stability (Backtrader default unchanged).
- Avoids premature migration based on limited pilot-only data.
- Establishes stronger evaluation foundations (reproducibility + observability integrations).

### Negative

- Delays a definitive Nautilus adoption decision.
- Extends timeline for any Nautilus-specific production readiness claims.

## Follow-up Actions

1. Expand native Nautilus evaluation coverage across additional frozen strategy/dataset pairs.
2. Re-run comparative evaluation with real runtime/fidelity metrics.
3. Revisit ADR-011 with Go/No-Go/Hybrid decision based on measured evidence.

## Validation Criteria for Revisiting This ADR

- Native Nautilus execution succeeds for pilot scenario.
- Native Nautilus execution succeeds across at least one additional frozen strategy scenario.
- Comparable metrics (return/drawdown/trades/runtime/memory) are published.
- Operational overhead (install/debug/CI) is documented and acceptable.

## References

- `docs/research/nautilus-pilot-evaluation.md`
- `docs/planning/archive/IMPLEMENTATION_PLAN_6.2_E6_EXECUTION_READY.md`
- `finbot/adapters/nautilus/nautilus_adapter.py`
- `finbot/services/backtesting/adapters/backtrader_adapter.py`
- `finbot/services/backtesting/backtest_batch.py`
