# Backtesting Parity Tolerance Specification

**Created:** 2026-02-14
**Status:** Active
**Applies To:** Legacy backtest path vs adapter path comparisons

## Purpose

Define objective pass/fail thresholds for migration parity checks.

## Comparison Inputs

- Strategy and params from `docs/planning/golden-strategies-and-datasets.md`
- Same frozen dataset files and date windows
- Same initial cash and broker/sizer configuration

## Metrics and Tolerances

## Hard Equality (must match exactly)

- Number of rows in value/cash time series
- Backtest start date and end date
- Presence of expected result columns

## Numerical Tolerances

- Final portfolio value:
  - Relative error <= `0.10%` (10 bps)
- CAGR:
  - Absolute difference <= `0.15%` (15 bps)
- Max drawdown:
  - Absolute difference <= `0.20%` (20 bps)
- Sharpe ratio:
  - Absolute difference <= `0.05`
- Number of rebalances/trades (if metric available):
  - Absolute difference <= `1`

## Time-Series Drift Tolerance

- Daily portfolio value series:
  - At least `99.0%` of points within `0.25%` relative error
  - No single point exceeding `1.0%` relative error unless explained by known event-handling differences

## Failure Handling

- Any hard-equality failure: immediate fail.
- Any numerical threshold breach: fail and open regression issue with:
  - Strategy ID (`GS-01`/`GS-02`/`GS-03`)
  - Metric(s) breached
  - Candidate root-cause notes

## Allowed Temporary Exceptions

Exceptions are allowed only with:

1. Linked issue documenting cause.
2. Time-bound waiver (expiry date).
3. Explicit reviewer sign-off.

## Revision Policy

- Tighten thresholds only after two consecutive green runs on all golden strategies.
- Any threshold relaxation requires ADR or roadmap note.
