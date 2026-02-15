# ADR-005: Adapter-First Backtesting and Live-Readiness Strategy

## Status

Accepted

## Date

2026-02-14

## Context

Finbot currently delivers most value through backtesting and simulation, not live execution.
The platform scope is broader than a trading engine and includes:

- Data collection and quality monitoring
- Financial simulators and optimizers
- Health economics modeling
- Dashboard and CLI workflows

A full immediate migration to a new trading engine would introduce high risk and cost while not directly improving current primary workflows. At the same time, the codebase needs a path to future live-trading support.

## Decision

Adopt an adapter-first architecture and phase-gated rollout:

1. Keep existing Backtrader-based flows as production baseline.
2. Introduce internal contracts for market data, execution, portfolio state, and run results.
3. Implement a Backtrader adapter behind those contracts first.
4. Validate parity using golden strategies, frozen datasets, and explicit metric tolerances.
5. Pilot NautilusTrader later in a constrained paper-trading scope (single strategy/market) before any broad migration decision.

## Alternatives Considered

### A) Keep current architecture unchanged

- Pros: No migration risk or engineering lift.
- Cons: Engine lock-in, weak path to future live execution.
- Decision: Rejected (insufficient long-term flexibility).

### B) Full migration to NautilusTrader now

- Pros: Potential execution/live parity benefits.
- Cons: High rewrite risk, uncertain ROI for current backtesting-first priorities.
- Decision: Rejected (timing/risk mismatch).

### C) Adapter-first internal contracts, with later pilot

- Pros: Maintains current output velocity while de-risking future engine changes.
- Cons: Adds short-term architecture work.
- Decision: Accepted.

## Consequences

### Positive

- Reduced migration risk through phased validation.
- Better reproducibility and comparison via canonical result schemas.
- Clear go/no-go criteria for future engine decisions.

### Negative

- Additional near-term platform work before immediate feature wins.
- Temporary complexity while old and adapter paths coexist.

## Phase Gates

1. **Contract Gate:** Core interfaces typed, tested, and documented.
2. **Parity Gate:** Adapter and legacy path remain within tolerance for golden strategies.
3. **Fidelity Gate:** Cost model and event correctness assumptions are explicit/tested.
4. **Pilot Gate:** Nautilus pilot demonstrates quantified benefit before migration expansion.

## Success Metrics

- Zero regression in current CLI backtesting workflows.
- Golden strategy parity checks pass in CI.
- Reproducible runs from metadata + dataset snapshot.
- Decision memo for execution-engine direction grounded in pilot data.
