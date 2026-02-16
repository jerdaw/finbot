# Backtesting and Live-Readiness Backlog

**Created:** 2026-02-14
**Status:** In progress
**Plan Source:** `docs/planning/backtesting-live-readiness-implementation-plan.md`
**Handoff:** `docs/planning/backtesting-live-readiness-handoff-2026-02-14.md`

## Estimation Scale

- `S` = 1-2 days
- `M` = 3-5 days
- `L` = 1-2 weeks

## Epic E0: Baseline and Decision Framing (Weeks 1-2)

### E0-T1 (S) Create ADR for adapter-first strategy

- Output: `docs/adr/ADR-005-adapter-first-backtesting-live-readiness.md`
- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Decision, alternatives, and phase gates documented.
  - Explicit "no full rewrite now" rationale captured.

### E0-T2 (M) Capture baseline benchmark/report pack

- Output: `docs/research/backtesting-baseline-report.md`
- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Runtime, failure modes, key KPI outputs captured.
  - Reproducibility limits documented.

### E0-T3 (S) Select golden strategies and frozen datasets

- Output: `docs/planning/golden-strategies-and-datasets.md`
- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - 3 strategies selected (simple/medium/complex).
  - Input datasets and date windows frozen.

### E0-T4 (S) Define parity tolerances

- Output: `docs/planning/parity-tolerance-spec.md`
- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Metric tolerances documented with pass/fail rules.

## Epic E1: Contracts and Schema Layer (Weeks 3-8)

### E1-T1 (M) Create `finbot/core/contracts/` skeleton

- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Typed contracts for market data, execution, portfolio state, and results.
  - Public module exports defined.

### E1-T2 (M) Define canonical event/result schemas

- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Bar/quote/trade/corporate action and fee model inputs specified.
  - Backtest result schema can represent current outputs.

### E1-T3 (S) Add schema versioning policy

- Status: ✅ Complete (2026-02-14)
- Acceptance:
  - Version field + compatibility policy documented.
  - One migration test for backward compatibility.

### E1-T4 (M) Add contract test suite

- Status: ✅ Complete (2026-02-14, initial version)
- Acceptance:
  - Contract tests in `tests/unit/` cover core interfaces.
  - CI runs contract tests by default.

## Epic E2: Backtrader Adapter and Parity Harness (Weeks 9-16)

### E2-T1 (L) Implement Backtrader adapter

- Output: `finbot/services/backtesting/adapters/backtrader_adapter.py`
- Status: ✅ Complete (2026-02-14, initial contract-backed implementation)
- Acceptance:
  - Existing runner entry points continue to work.
  - Adapter supports golden strategy set.

### E2-T2 (M) Build A/B harness

- Output: `tests/integration/test_backtest_parity_ab.py`
- Status: ✅ Complete (2026-02-16, GS-01 passing with 100% parity)
- Acceptance:
  - Old and adapter paths can run on same inputs.
  - Output diffs are machine-readable.

### E2-T3 (M) Add golden-master parity tests

- Acceptance:
  - All golden strategies covered.
  - Parity checks use tolerance spec from E0-T4.

### E2-T4 (S) Wire CI parity gate

- Acceptance:
  - Parity regressions fail CI.

## Epic E3: Fidelity Improvements (Weeks 17-26)

### E3-T1 (M) Cost model expansion

- Acceptance:
  - Commission/spread/slippage/borrow are parameterized.
  - Unit tests for each component.

### E3-T2 (M) Corporate action + calendar correctness

- Acceptance:
  - Split/dividend handling validated.
  - Session/calendar behavior tested.

### E3-T3 (M) Walk-forward + regime evaluation

- Acceptance:
  - Walk-forward helper API added.
  - Regime segmented metrics generated.

## Epic E4: Reproducibility and Observability (Weeks 27-36)

### E4-T1 (M) Experiment registry and metadata hashes

- Acceptance:
  - Runs store immutable metadata + config hash + seed.

### E4-T2 (M) Snapshot-based reproducibility mode

- Acceptance:
  - Runs can be replayed from dataset snapshot reference.

### E4-T3 (M) Batch observability instrumentation

- Acceptance:
  - Status/retry/failure taxonomy visible and queryable.

### E4-T4 (S) Dashboard experiment comparison page

- Acceptance:
  - Experiment cohorts can be compared by assumptions and results.

## Epic E5: Live-Readiness Without Production Live (Weeks 37-44)

### E5-T1 (M) Broker-neutral execution contracts

- Acceptance:
  - Shared strategy contract works for backtest and paper modes.

### E5-T2 (M) Order lifecycle and latency hooks

- Acceptance:
  - States: new/partial/filled/canceled/rejected are supported.
  - Latency simulation hooks included.

### E5-T3 (M) Risk controls interface

- Acceptance:
  - Position/exposure/drawdown/kill-switch rules integrated.

### E5-T4 (M) State checkpoint and recovery

- Acceptance:
  - Strategy and portfolio state can be checkpointed and restored.

## Epic E6: NautilusTrader Pilot and Decision Gate (Weeks 45-52)

### E6-T1 (M) Single-strategy pilot adapter

- Acceptance:
  - One strategy runs in paper mode via Nautilus path.

### E6-T2 (S) Comparative evaluation report

- Output: `docs/research/nautilus-pilot-evaluation.md`
- Acceptance:
  - Fill realism, latency fit, ops complexity, integration cost compared.

### E6-T3 (S) Go/No-Go recommendation memo

- Output: `docs/adr/ADR-006-live-execution-engine-decision.md`
- Acceptance:
  - Decision and rationale recorded with quantified tradeoffs.

## Dependencies

- E1 depends on E0.
- E2 depends on E1.
- E3 depends on E2 baseline parity.
- E4 can start after E1 but should align with E2 output schemas.
- E5 depends on E1 contracts and E2 adapter maturity.
- E6 depends on E5 interfaces.

## Sprint 1 Backlog (Immediate)

1. `E0-T1` Create ADR-005.
2. `E0-T3` Select golden strategies + frozen datasets.
3. `E0-T4` Define parity tolerance spec.
4. `E1-T1` Create `finbot/core/contracts/` skeleton.
5. `E1-T4` Add initial contract tests.

## Sprint 2 Backlog (Immediate)

1. [x] `E2-T1` Backtrader adapter skeleton.
2. [x] `E2-T2` A/B parity harness for one strategy (GS-01 passing with 100% parity).
3. [ ] `E2-T4` CI parity gate for one golden strategy.
4. [x] `E0-T2` Publish first baseline report draft.

## Progress Tracking

- `E0`: Complete
- `E1`: Complete
- `E2`: In progress (`E2-T1` complete; `E2-T2`, `E2-T3`, `E2-T4` pending)
- `E3`: Not started
- `E4`: Not started
- `E5`: Not started
- `E6`: Not started
