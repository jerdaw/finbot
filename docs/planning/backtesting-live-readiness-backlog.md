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

- Status: ✅ Complete (2026-02-16, all golden strategies passing with 100% parity)
- Acceptance:
  - All golden strategies covered.
  - Parity checks use tolerance spec from E0-T4.

### E2-T4 (S) Wire CI parity gate

- Status: ✅ Complete (2026-02-16, dedicated parity-gate job in CI)
- Acceptance:
  - Parity regressions fail CI.

## Epic E3: Fidelity Improvements (Weeks 17-26)

### E3-T1 (M) Cost model expansion

- Status: ✅ Complete (2026-02-16, full integration delivered)
- Completed:
  - [x] Cost model contracts created (CostModel, CostEvent, CostSummary, CostType)
  - [x] Default cost models implemented (Zero* models)
  - [x] Advanced cost models implemented (Flat, Percentage, Fixed, Sqrt)
  - [x] Comprehensive unit tests (36 tests, all passing)
  - [x] Parity maintained (all 3 golden strategies still 100%)
  - [x] Example notebook demonstrating usage
  - [x] Integration into BacktestRunResult schema (costs field added, optional)
  - [x] Cost tracking in adapter (TradeTracker analyzer captures all trades)
  - [x] Full cost breakdown in results (CostSummary with per-trade events)
  - [x] Cost serialization/deserialization (JSON-compatible)
  - [x] Integration tests (5 tests verifying end-to-end cost tracking)
- Acceptance:
  - Commission/spread/slippage/borrow are parameterized. ✅
  - Unit tests for each component. ✅
  - Cost events tracked in BacktestRunResult. ✅
  - Cost metrics included in result summary. ✅
  - All 3 golden strategy parity tests pass with defaults. ✅

### E3-T2 (M) Corporate action + calendar correctness

- Status: ✅ Complete (All steps delivered)
- Completed:
  - [x] Backtrader uses adjusted prices (Adj Close) by default
  - [x] OHLC prices adjusted proportionally to maintain relationships
  - [x] Original prices preserved as Close_Unadjusted for reference
  - [x] 3 unit tests verifying adjusted price behavior
  - [x] Parity maintained (all 3 golden strategies 100% parity)
  - [x] 6 corporate action tests with synthetic data
  - [x] Test stock splits (2:1, 3:1, 1:5 reverse)
  - [x] Test dividend payments (single, multiple)
  - [x] Test combined split + dividend scenarios
  - [x] Missing data policy enum (FORWARD_FILL, DROP, ERROR, INTERPOLATE, BACKFILL)
  - [x] Missing data policy integration into BacktraderAdapter
  - [x] 11 comprehensive missing data policy tests
  - [x] Policy application before validation
  - [x] Edge case handling (gaps at start/end)
  - [x] Comprehensive user guide (corporate-actions-and-data-quality.md)
  - [x] Practical Jupyter notebook with examples
  - [x] 467 tests passing total
- Skipped:
  - Trading calendar validation (Step 3 - YFinance already filters to trading days)
- Acceptance:
  - Backtrader uses adjusted prices. ✅
  - Split/dividend handling validated. ✅
  - Missing data policies implemented and tested. ✅
  - Documentation complete with examples. ✅

### E3-T3 (M) Walk-forward + regime evaluation

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] Walk-forward models (WalkForwardConfig, WalkForwardWindow, WalkForwardResult)
  - [x] Regime detection models (MarketRegime, RegimeConfig, RegimePeriod, RegimeMetrics)
  - [x] Walk-forward implementation (generate_windows, run_walk_forward)
  - [x] Regime detection implementation (SimpleRegimeDetector, segment_by_regime)
  - [x] 9 walk-forward tests
  - [x] 11 regime detection tests
  - [x] Comprehensive user guide with examples
  - [x] 489 tests passing total (up from 467)
  - [x] 100% parity maintained
- Acceptance:
  - Walk-forward helper API added. ✅
  - Regime segmented metrics generated. ✅

## Epic E4: Reproducibility and Observability (Weeks 27-36)

### E4-T1 (M) Experiment registry and metadata hashes

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] ExperimentRegistry class with save/load/query/delete
  - [x] Year/month organized JSON file storage
  - [x] Query by strategy, date range, config hash
  - [x] 14 unit tests (all passing)
  - [x] 509 tests passing total (up from 489)
  - [x] Implementation plan documented
- Acceptance:
  - Runs store immutable metadata + config hash + seed. ✅
  - File-based registry with query capabilities. ✅

### E4-T2 (M) Snapshot-based reproducibility mode

- Status: 🟡 Partially Complete (2026-02-19) - Adapter integration delivered, replay/docs still deferred
- Completed:
  - [x] DataSnapshot contract with content-addressable hashing
  - [x] DataSnapshotRegistry with create/load/list/delete operations
  - [x] Content-based deduplication (same data → same snapshot ID)
  - [x] Snapshot utilities (cleanup_orphaned_snapshots, get_snapshot_stats)
  - [x] 21 comprehensive unit tests (all passing)
  - [x] 530 tests passing total (up from 509)
  - [x] Implementation plan documented
- Completed in follow-up:
  - [x] BacktraderAdapter integration (`auto_snapshot`, `snapshot_registry`)
  - [x] Unit test coverage for snapshot attachment
- Deferred (Future work):
  - [ ] Replay functionality using snapshots
  - [ ] Integration tests for replay reproducibility
  - [ ] User guide documentation
- Acceptance:
  - Snapshot infrastructure complete and tested. ✅
  - Can create/load/manage snapshots manually. ✅
  - Runs can be replayed from dataset snapshot reference. ⬜ (Deferred to avoid breaking parity)

**Note:** Snapshot infrastructure and adapter wiring are now complete; replay and
end-to-end reproducibility workflows remain the next follow-up scope.

### E4-T3 (M) Batch observability instrumentation

- Status: 🟡 Partially Complete (2026-02-19) - `backtest_batch` integration delivered, retries/docs deferred
- Completed:
  - [x] Batch observability contracts (BatchRun, BatchStatus, ErrorCategory, BatchItemResult)
  - [x] BatchRegistry with create/update/list/query/complete operations
  - [x] Error categorization from exceptions (intelligent pattern matching)
  - [x] Status lifecycle tracking (PENDING → RUNNING → COMPLETED/PARTIAL/FAILED)
  - [x] Error taxonomy and aggregation
  - [x] Performance metrics (duration, throughput, success rate)
  - [x] 39 comprehensive unit tests (23 registry + 16 categorizer, all passing)
  - [x] 569 tests passing total (up from 530)
  - [x] Implementation plan documented
- Completed in follow-up:
  - [x] Integration with `backtest_batch` via optional `track_batch` mode
  - [x] Unit tests for partial-failure and all-failure lifecycle tracking
- Deferred (Future work):
  - [ ] Retry utilities for failed items
  - [ ] User guide documentation
- Acceptance:
  - Status tracking infrastructure complete and tested. ✅
  - Error taxonomy and categorization functional. ✅
  - Can track batches manually with full observability. ✅
  - Status/retry/failure taxonomy visible and queryable. ✅

**Note:** Batch observability infrastructure is complete and now integrated with
`backtest_batch` behind an opt-in flag; retry ergonomics and user docs are pending.

### E4-T4 (S) Dashboard experiment comparison page

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] Dashboard page (pages/7_experiments.py)
  - [x] Experiment selection with filters (strategy, limit)
  - [x] Assumptions comparison table (shows only differences)
  - [x] Metrics comparison table with highlighting (green=best, red=worst)
  - [x] Visual comparison with interactive bar charts
  - [x] Export to CSV functionality
  - [x] Comparison utilities (build, format, highlight, plot, export)
  - [x] 14 comprehensive unit tests (all passing)
  - [x] 583 tests passing total (up from 569)
  - [x] Implementation plan documented
- Acceptance:
  - Experiment cohorts can be compared by assumptions and results. ✅
  - Side-by-side metric visualization. ✅
  - Export functionality. ✅

## Epic E5: Live-Readiness Without Production Live (Weeks 37-44)

### E5-T1 (M) Broker-neutral execution contracts

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] Order lifecycle contracts (OrderStatus, RejectionReason, OrderExecution, Order)
  - [x] Order validator with comprehensive validation logic
  - [x] Execution simulator for paper trading with slippage/commission
  - [x] Order registry with date-organized JSON storage
  - [x] 21 comprehensive unit tests (all passing)
  - [x] 598 tests passing total (up from 583)
  - [x] Integration into contracts package
- Acceptance:
  - Shared strategy contract works for backtest and paper modes. ✅

### E5-T2 (M) Order lifecycle and latency hooks

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] Order lifecycle states fully implemented in E5-T1 (NEW → SUBMITTED → FILLED/REJECTED/CANCELLED)
  - [x] Latency configuration contracts (LatencyConfig with submission/fill/cancel latencies)
  - [x] Pre-configured profiles (INSTANT, FAST, NORMAL, SLOW)
  - [x] Pending action queue for time-based processing
  - [x] Submission latency (orders delayed before SUBMITTED status)
  - [x] Fill latency (random between min/max, realistic simulation)
  - [x] Cancellation latency (delayed cancellation processing)
  - [x] 17 comprehensive latency tests (all passing)
  - [x] 615 tests passing total (up from 598, +17 tests)
  - [x] Integration into contracts package
  - [x] Backward compatible (defaults to LATENCY_INSTANT)
- Acceptance:
  - States: new/partial/filled/canceled/rejected are supported. ✅
  - Latency simulation hooks included. ✅

### E5-T3 (M) Risk controls interface

- Status: ✅ Complete (2026-02-16)
- Completed:
  - [x] Risk control contracts (RiskConfig, RiskViolation, RiskRuleType)
  - [x] Risk rules: PositionLimitRule, ExposureLimitRule, DrawdownLimitRule
  - [x] RiskChecker with comprehensive checking logic
  - [x] Position limits (max shares, max value per symbol)
  - [x] Exposure limits (gross and net as % of capital)
  - [x] Drawdown protection (daily and total from peak)
  - [x] Kill-switch (emergency trading halt)
  - [x] Risk state tracking (peak value, daily start value)
  - [x] ExecutionSimulator integration (optional risk_config parameter)
  - [x] Updated rejection reasons (4 new risk-specific reasons)
  - [x] 14 comprehensive risk control tests (all passing)
  - [x] 629 tests passing total (up from 615, +14 tests)
  - [x] Fully backward compatible (risk controls are optional)
- Acceptance:
  - Position/exposure/drawdown/kill-switch rules integrated. ✅

### E5-T4 (M) State checkpoint and recovery

- Acceptance:
  - Strategy and portfolio state can be checkpointed and restored.

## Epic E6: NautilusTrader Pilot and Decision Gate (Weeks 45-52)

### E6-T1 (M) Single-strategy pilot adapter

- Status: ✅ Complete (2026-02-19) - Native Nautilus one-strategy pilot path implemented with contract-safe fallback
- Completed:
  - [x] Adapter method alignment (`run` contract + `run_backtest` alias)
  - [x] Canonical metadata/result mapping
  - [x] Rebalance-only pilot validation rules
  - [x] Warning-tagged fallback execution path
  - [x] Unit tests for pilot behavior
  - [x] Native Nautilus execution path (engine/data/strategy wiring)
- Acceptance:
  - One strategy runs in paper mode via Nautilus path. ✅

### E6-T2 (S) Comparative evaluation report

- Output: `docs/research/nautilus-pilot-evaluation.md`
- Acceptance:
  - Fill realism, latency fit, ops complexity, integration cost compared.

### E6-T3 (S) Go/No-Go recommendation memo

- Output: `docs/adr/ADR-011-nautilus-decision.md`
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

## Sprint 2 Backlog - ✅ COMPLETE

1. [x] `E2-T1` Backtrader adapter skeleton.
2. [x] `E2-T2` A/B parity harness for one strategy (GS-01 passing with 100% parity).
3. [x] `E2-T4` CI parity gate for one golden strategy (dedicated CI job, datasets in git).
4. [x] `E0-T2` Publish first baseline report draft.
5. [x] Migration status report (`docs/research/adapter-migration-status-2026-02-16.md`).

## Sprint 3 Status - ✅ COMPLETE (Epic E2 Closure)

**Epic E2 now complete** - all golden strategies validated with 100% parity:
1. [x] `E2-T3` Golden-master parity tests for GS-02 (DualMomentum + SPY/TLT) - 100% parity
2. [x] `E2-T3` Golden-master parity tests for GS-03 (RiskParity + SPY/QQQ/TLT) - 100% parity
3. [x] `E2-T4` Extended CI parity gate to all 3 golden strategies

## Sprint 4 Status - ✅ Complete (E3-T1 Fully Delivered)

**Epic E3: Backtesting Fidelity Improvements**

1. [x] `E3-T1` Expand cost model - **Fully complete** (infrastructure + integration + examples)
   - ✅ Cost model contracts (CostModel, CostEvent, CostSummary, CostType)
   - ✅ 7 cost model implementations (Zero, Flat, Percentage, Fixed, Sqrt)
   - ✅ 36 unit tests (all passing)
   - ✅ Parity maintained (100% on all 3 golden strategies)
   - ✅ Example notebook demonstrating all cost models
   - ✅ Full adapter integration (BacktestRunResult.costs field, TradeTracker analyzer)
   - ✅ Cost serialization/deserialization
   - ✅ 5 integration tests verifying end-to-end cost tracking
   - ✅ 455 tests passing (up from 450)

2. [x] `E3-T2` Corporate action + calendar correctness - **Fully complete**
   - ✅ Adjusted price handling (Adj Close)
   - ✅ OHLC proportional adjustment
   - ✅ Corporate action tests (splits, dividends)
   - ✅ Missing data policies (5 policies)
   - ✅ 11 policy tests + 6 corporate action tests
   - ✅ Comprehensive user guide
   - ✅ Practical Jupyter notebook
   - ✅ 467 tests passing (up from 464)
   - ✅ 100% parity maintained

3. [x] `E3-T3` Walk-forward + regime evaluation support ✅

## Sprint 5 Status - ✅ Complete (E3-T3 Fully Delivered)

## Sprint 6 Status - ✅ Complete (E4-T1 Fully Delivered)

**Epic E4: Reproducibility and Observability**

1. [x] `E4-T1` Experiment registry and metadata hashes - **Fully complete**
   - ✅ ExperimentRegistry class (save/load/query/delete)
   - ✅ Year/month organized JSON file storage
   - ✅ Query by strategy, date range, config hash
   - ✅ 14 unit tests (all passing)
   - ✅ 509 tests passing total (up from 489)
   - ✅ Implementation plan documented

**Next Sprint:**
- E4-T2: Snapshot-based reproducibility mode

## Progress Tracking

- `E0`: ✅ Complete
- `E1`: ✅ Complete
- `E2`: ✅ Complete (all tasks done: adapter, parity harness, golden tests, CI gate)
- `E3`: ✅ Complete (All tasks: E3-T1 cost models, E3-T2 corporate actions + data quality, E3-T3 walk-forward + regime analysis)
- `E4`: 🟡 Mostly complete (core infra complete; replay docs and retry ergonomics remain)
- `E5`: ✅ Complete (All tasks: E5-T1 orders/executions, E5-T2 latency simulation, E5-T3 risk controls, E5-T4 state checkpoints)
- `E6`: 🚧 In progress (contract-aligned pilot fallback complete; native Nautilus path pending decision gate follow-up)
