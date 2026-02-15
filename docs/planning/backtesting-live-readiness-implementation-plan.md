# Backtesting and Live-Readiness Implementation Plan

**Created:** 2026-02-14
**Last Updated:** 2026-02-14
**Status:** Active
**Horizon:** 12 months
**Primary Goal:** Keep current backtesting production flow while preparing low-risk migration options for future live trading.
**Current Phase:** Phase 2 (Backtrader Adapter and Parity Harness) - In progress
**Handoff Note:** `docs/planning/backtesting-live-readiness-handoff-2026-02-14.md`

## Sprint 1 Status (as of 2026-02-14)

- [x] ADR for adapter-first architecture (`docs/adr/ADR-005-adapter-first-backtesting-live-readiness.md`)
- [x] Golden strategies and frozen datasets (`docs/planning/golden-strategies-and-datasets.md`)
- [x] Parity tolerance specification (`docs/planning/parity-tolerance-spec.md`)
- [x] Contract package scaffold (`finbot/core/contracts/`)
- [x] Initial contract tests (`tests/unit/test_core_contracts.py`)
- [x] Baseline benchmark report (`docs/research/backtesting-baseline-report.md`)
- [x] Canonical schema helpers and payload serialization (`finbot/core/contracts/schemas.py`, `finbot/core/contracts/serialization.py`)
- [x] Schema versioning policy and legacy migration path (`docs/guidelines/backtesting-contract-schema-versioning.md`, `finbot/core/contracts/versioning.py`)

## Sprint 2 Status (as of 2026-02-14)

- [x] Backtrader adapter skeleton (`finbot/services/backtesting/adapters/backtrader_adapter.py`)
- [ ] A/B parity harness for one golden strategy
- [ ] CI parity gate for one golden strategy
- [ ] Migration status report draft refresh after adapter parity run

## Decision Summary

1. Keep the current Backtrader-based stack as production baseline.
2. Build internal contracts and adapters so engines are swappable.
3. Run a scoped NautilusTrader pilot later for execution-path validation only.
4. Do not do a full-platform rewrite unless pilot evidence clearly supports it.

## Target Outcomes

- Improve backtesting quality and reproducibility now.
- Preserve existing CLI/service behavior while introducing adapters.
- Establish paper/live-readiness interfaces without committing to full migration.
- Enable objective go/no-go decision for NautilusTrader (or alternatives).

## Scope and Non-Goals

### In Scope

- Contract-first architecture for data, strategy execution, orders/fills, portfolio state, and results.
- Backtrader adapter with parity harness and regression gates.
- Backtesting fidelity upgrades (slippage/fees/corporate actions/calendar correctness).
- Experiment reproducibility and observability improvements.
- Paper-trading readiness interfaces.
- One-strategy NautilusTrader pilot.

### Out of Scope (for this plan window)

- Full replacement of Backtrader engine.
- Multi-venue live deployment to production.
- Broad strategy rewrites unless required by contract migration.

## Phase Plan (12 Months)

## Phase 0 (Weeks 1-2): Baseline and Architecture Decision

### Deliverables

- ADR documenting:
  - No rewrite now.
  - Adapter architecture strategy.
  - Live-readiness objectives and decision gates.
- Baseline metrics report from current engine:
  - Runtime, failure rate, KPI outputs, and reproducibility characteristics.
- Three "golden strategies" selected for migration validation:
  - One simple, one medium complexity, one complex multi-asset.
- Explicit parity tolerance definitions for migrated paths.

### Exit Criteria

- ADR approved.
- Baseline report published.
- Golden dataset + strategy list frozen.

## Phase 1 (Weeks 3-8): Contract-First Core

### Deliverables

- New contract package: `finbot/core/contracts/`
  - Market data contracts.
  - Order/fill/execution contracts.
  - Portfolio/account state contracts.
  - Backtest result schema contract.
- Canonical event schema definitions:
  - Bars, quotes, trades, corporate actions, fees/slippage inputs.
- Schema versioning rules and migration compatibility policy.
- Initial contract test suite in `tests/unit/`.

### Exit Criteria

- Contracts are type-checked, documented, and covered by tests.
- Result schema can represent current backtest outputs without loss.

## Phase 2 (Weeks 9-16): Backtrader Adapter and Parity Harness

### Deliverables

- `BacktraderAdapter` in `finbot/services/backtesting/adapters/`.
- Existing entry points remain functional:
  - `finbot/services/backtesting/run_backtest.py`
  - `finbot/services/backtesting/backtest_batch.py`
- A/B harness for old path vs adapter path on identical inputs.
- Golden-master tests for the three golden strategies.

### Exit Criteria

- Adapter path outputs are within defined tolerance on all golden cases.
- No regression in current CLI backtesting workflows.

## Phase 3 (Weeks 17-26): Backtesting Fidelity Upgrades

### Deliverables

- Explicit cost model components:
  - Commission.
  - Spread.
  - Slippage.
  - Borrow/funding costs.
  - Optional market impact tiers.
- Event correctness hardening:
  - Splits/dividends handling.
  - Trading calendar/session control.
  - Missing-data policies.
- Walk-forward and regime-segment evaluation support.
- Unified stats path via shared metrics contract.

### Exit Criteria

- Fidelity assumptions are parameterized and test-covered.
- Robustness runs available in CI for golden strategies.

## Phase 4 (Weeks 27-36): Research Reproducibility and Observability

### Deliverables

- Experiment registry:
  - Immutable run metadata.
  - Parameter/config hash.
  - Artifact links.
- Reproducibility mode:
  - Data snapshot pinning.
  - Seed capture.
  - Environment/version metadata.
- Batch execution observability:
  - Per-run status.
  - Retry outcomes.
  - Failure taxonomy.
- Dashboard support for experiment cohort comparisons.

### Exit Criteria

- Any published result can be rerun from metadata + snapshot.

## Phase 5 (Weeks 37-44): Live-Readiness Interfaces (No Production Live Trading)

### Deliverables

- Broker-neutral execution interfaces.
- Paper-trading simulator aligned to the same strategy contracts.
- Order lifecycle model:
  - New, partial fill, filled, canceled, rejected.
- Risk control interfaces:
  - Position/exposure limits.
  - Drawdown stop.
  - Kill switch.
- Checkpoint/recovery primitives for strategy and portfolio state.

### Exit Criteria

- Strategies can run backtest and paper modes using shared contracts.

## Phase 6 (Weeks 45-52): NautilusTrader Pilot and Decision Gate

### Deliverables

- One-strategy Nautilus adapter prototype (single market/timeframe, paper mode).
- Comparative evaluation:
  - Fill realism.
  - Latency model fit.
  - Ops/maintenance complexity.
  - Integration burden with existing platform.
- Migration cost/risk estimate and recommendation memo.

### Exit Criteria

- Formal go/no-go decision recorded.
- No full migration without clear quantified advantage.

## Parallel Workstreams

### 1) Architecture and Contracts

- Owner: Core platform engineering.
- KPI: Engine swappability without strategy rewrites.

### 2) Backtest Quality

- Owner: Quant/research engineering.
- KPI: Reduced expected backtest-to-live performance gap.

### 3) Data and Reproducibility

- Owner: Data/platform engineering.
- KPI: Deterministic reruns and auditability.

### 4) DevEx and CI Gates

- Owner: Platform engineering.
- KPI: Regression prevention and faster safe iteration.

## Repository Implementation Targets

- Add contracts: `finbot/core/contracts/`
- Add adapters: `finbot/services/backtesting/adapters/`
- Preserve public runner flows in current backtesting service modules.
- Add reproducibility helpers under `finbot/utils/`.
- Add parity and regression tests under `tests/unit/` and `tests/integration/`.
- Track architectural decisions in `docs/adr/`.
- Add docs pages in `docs_site/` for contracts and reproducibility model.

## Definitions of Done (Milestone Level)

- Contracts are typed, documented, and covered by contract tests.
- Existing CLI flows remain stable.
- Golden strategy parity checks pass in CI.
- Reproducibility checks pass from metadata + snapshot only.
- Contract/parity regressions block merges.

## Risks and Controls

- Risk: abstraction drift.
  - Control: contract tests + ADR-required interface change process.
- Risk: hidden behavior changes during adapter rollout.
  - Control: golden-master parity + side-by-side reports.
- Risk: overbuilding for future live trading.
  - Control: strict phase gates and pilot-limited scope.
- Risk: operational complexity growth.
  - Control: single production engine until pilot demonstrates clear net benefit.

## Immediate Execution Plan (Next 2 Sprints)

## Sprint 1

1. Create ADR for adapter-first architecture and decision gates.
2. Define contract modules and result schema.
3. Add first contract tests.
4. Select golden strategies and lock baseline datasets.

## Sprint 2

1. Implement Backtrader adapter skeleton.
2. Wire A/B parity harness.
3. Add first CI parity gate for one golden strategy.
4. Publish first migration status report with baseline comparisons.
