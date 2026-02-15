# Backtesting Baseline Report

**Date:** 2026-02-14
**Status:** Baseline established for adapter migration parity work
**Related Plan:** `docs/planning/backtesting-live-readiness-implementation-plan.md`

## Objective

Create a reproducible baseline for golden strategies before adapter migration work.
This baseline is used as the reference point for parity checks and regression tracking.

## Scope

- Strategy set: `GS-01`, `GS-02`, `GS-03` from `docs/planning/golden-strategies-and-datasets.md`
- Date window: `2010-01-04` to `2026-02-09`
- Initial cash: `100000.0`
- Runner: `finbot.services.backtesting.backtest_runner.BacktestRunner`
- Broker/sizer:
  - `bt.brokers.BackBroker`
  - `finbot.services.backtesting.brokers.fixed_commission_scheme.FixedCommissionScheme`
  - `bt.sizers.AllInSizer`

## Reproducibility Command

```bash
ENV=development uv run python scripts/generate_backtesting_baseline.py
```

## Baseline Results (Summary)

Source file: `docs/research/backtesting-baseline-results-2026-02-14.csv`

| Case | Strategy | Symbols | Rows | Runtime (s) | Ending Value | ROI | CAGR | Sharpe | Max Drawdown |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| GS-01 | NoRebalance | SPY | 4050 | 0.410 | 612168.59 | 5.1217 | 0.1193 | 0.7410 | -0.3409 |
| GS-02 | DualMomentum | SPY,TLT | 4050 | 0.624 | 177024.74 | 0.7702 | 0.0362 | 0.3500 | -0.2672 |
| GS-03 | RiskParity | SPY,QQQ,TLT | 4050 | 0.991 | 396359.65 | 2.9636 | 0.0895 | 0.8382 | -0.2964 |

## Runtime Observations

- Baseline runtimes are all below 1 second per golden case on this machine.
- Runtime ranking for these cases:
  - Fastest: `GS-01` (single-asset buy/hold)
  - Mid: `GS-02` (2-asset rotational logic)
  - Slowest: `GS-03` (3-asset risk parity rebalancing)
- Runtime values will vary slightly between runs based on machine load.

## Failure Modes Observed

- No execution failures observed for the three baseline cases.
- No missing-column issues in result output for baseline run.

## Reproducibility Limits

- Results are dependent on local parquet snapshot state as of `2026-02-09`.
- Any changes to:
  - source parquet files,
  - strategy logic,
  - quantstats/backtrader versions,
  can shift metric values.
- Parity checks should use tolerance rules from `docs/planning/parity-tolerance-spec.md`, not strict floating-point equality.

## Next Use in Migration

- Use this report and CSV as the baseline reference for:
  - Adapter A/B parity harness outputs.
  - CI parity regression gates.
