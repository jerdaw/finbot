# DCA Optimization

This page summarizes Finbot's research on dollar-cost-averaging allocation
optimization and links to the full repository report.

## Overview

Finbot's DCA optimizer evaluates allocation ratios, investment horizons, and
purchase frequencies across multiple portfolio constructions using exhaustive
grid search and risk-adjusted metrics.

## Key Findings

- Classic 60/40 stock-bond allocations remain competitive for risk-adjusted
  performance in non-leveraged portfolios.
- Leveraged stock-bond mixes can improve Sharpe ratio when allocation is tuned
  conservatively.
- Longer investment horizons generally support somewhat higher equity weights.
- Monthly contributions tend to outperform quarterly contributions when trading
  frictions remain modest.

## Why It Matters

This work shows Finbot is not limited to single-strategy backtests; it also
supports systematic portfolio-construction questions with reproducible search
and comparison workflows.

## Read The Full Report

- [Full repository research note](https://github.com/jerdaw/finbot/blob/main/docs/research/dca-optimization-findings.md)
- [DCA optimization notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/02_dca_optimization_results.ipynb)

## Scope Note

This summary page keeps the public docs path coherent while the full empirical
discussion remains in the repository research note.