# Strategy Backtesting

This page summarizes Finbot's strategy-comparison research and links to the
full repository report.

## Overview

The original published comparison analyzed Finbot's first 10 strategy
implementations across multiple archetypes, including buy-and-hold,
rebalancing, moving-average timing, MACD, dip-buying, and hybrid approaches.

The current codebase has grown beyond that initial cohort. The report remains
useful as a foundational comparison, while the live platform and notebooks now
expose a broader strategy set.

## Key Findings

- No single strategy dominates across all metrics.
- Buy-and-hold tends to maximize raw return but not always risk-adjusted
  performance.
- Rebalancing and timing approaches can reduce drawdowns or improve specific
  risk metrics depending on regime.
- Higher-complexity strategies do not automatically justify their added
  implementation burden.

## Why It Matters

This report documents the evidence-oriented reasoning behind Finbot's
backtesting module: compare strategies transparently, examine tradeoffs, and
state limitations instead of presenting a single best approach.

## Read The Full Report

- [Full repository research note](https://github.com/jerdaw/finbot/blob/main/docs/research/strategy-backtest-results.md)
- [Strategy comparison notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/03_backtest_strategy_comparison.ipynb)

## Scope Note

The public docs page is intentionally brief. The repository report contains the
full methods, assumptions, and results tables for the original comparison.