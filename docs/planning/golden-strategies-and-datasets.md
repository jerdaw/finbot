# Golden Strategies and Frozen Datasets

**Created:** 2026-02-14
**Last Updated:** 2026-02-16
**Status:** Active baseline set for parity validation
**Data Snapshot As Of:** 2026-02-09
**Repository Status:** Golden datasets committed to git for CI parity testing

## Purpose

Define a stable reference set used to validate behavior while introducing contract/adapters.
These cases are used for A/B parity checks (legacy path vs adapter path).

## Frozen Configuration Rules

- Keep strategy logic and parameters fixed unless an ADR approves changes.
- Keep data source and file paths fixed for parity runs.
- Keep date windows fixed.
- Any change to this file requires updating parity baselines and noting rationale.

## Dataset Repository Status

Golden strategy datasets are committed to the repository to enable CI parity testing:
- `finbot/data/yfinance_data/history/SPY_history_1d.parquet` (303KB)
- `finbot/data/yfinance_data/history/TLT_history_1d.parquet` (199KB)
- `finbot/data/yfinance_data/history/QQQ_history_1d.parquet` (252KB)

These files are excluded from the general `.gitignore` rule for the data directory to ensure deterministic, fast CI runs without external data fetching.

## Golden Strategy Set

## GS-01: Buy-and-Hold Baseline

- Strategy: `NoRebalance`
- File: `finbot/services/backtesting/strategies/no_rebalance.py`
- Assets: `SPY`
- Dataset file(s):
  - `finbot/data/yfinance_data/history/SPY_history_1d.parquet`
- Date window: `2010-01-04` to `2026-02-09`
- Key params:
  - `equity_proportions=[1.0]`
- Why included:
  - Lowest-complexity control case.
  - Detects basic accounting or brokerage regressions quickly.

## GS-02: Dual Momentum Rotation

- Strategy: `DualMomentum`
- File: `finbot/services/backtesting/strategies/dual_momentum.py`
- Assets: `SPY`, `TLT`
- Dataset file(s):
  - `finbot/data/yfinance_data/history/SPY_history_1d.parquet`
  - `finbot/data/yfinance_data/history/TLT_history_1d.parquet`
- Date window: `2010-01-04` to `2026-02-09`
- Key params:
  - `lookback=252`
  - `rebal_interval=21`
- Why included:
  - Covers regime switching and safe-asset fallback behavior.
  - Sensitive to rebalance scheduling and signal calculation.

## GS-03: Multi-Asset Risk Parity

- Strategy: `RiskParity`
- File: `finbot/services/backtesting/strategies/risk_parity.py`
- Assets: `SPY`, `QQQ`, `TLT`
- Dataset file(s):
  - `finbot/data/yfinance_data/history/SPY_history_1d.parquet`
  - `finbot/data/yfinance_data/history/QQQ_history_1d.parquet`
  - `finbot/data/yfinance_data/history/TLT_history_1d.parquet`
- Date window: `2010-01-04` to `2026-02-09`
- Key params:
  - `vol_window=63`
  - `rebal_interval=21`
- Why included:
  - Covers multi-asset weighting, volatility windowing, and rebalance sequencing.
  - More likely to catch subtle allocation regressions.

## Run Invariants

- Initial cash: `100000.0`
- Frequency: daily bars from local parquet histories
- Commission model: current default backtesting commission settings
- Sizer: current default all-in sizing path used by existing runner
- Plotting: disabled for parity runs

## Ownership and Change Control

- Owner: Core platform + quant engineering
- Update trigger:
  - Strategy behavior changes
  - Contract schema changes affecting outputs
  - Data source migration requiring new frozen files
