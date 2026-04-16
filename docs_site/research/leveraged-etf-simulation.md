# Leveraged ETF Simulation

This page summarizes Finbot's leveraged ETF simulation research and points to
the full repository report.

## Overview

Finbot includes a vectorized leveraged ETF simulator designed to approximate
long-run fund behavior using underlying index returns, expense ratios,
borrowing-cost approximations, and spread adjustments.

## Key Findings

- Tracking accuracy remains strong across 1x, 2x, and 3x products.
- Error grows with leverage, consistent with volatility-decay theory.
- The simulator is suitable for research, education, and historical scenario
  extension when direct fund history is limited.

## Why It Matters

This research supports one of Finbot's core value propositions: transparent,
inspectable simulation of fund mechanics rather than opaque extrapolation.

## Read The Full Report

- [Full repository research note](https://github.com/jerdaw/finbot/blob/main/docs/research/leveraged-etf-simulation-accuracy.md)
- [Fund simulation notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/01_fund_simulation_demo.ipynb)

## Scope Note

This summary page exists so the published docs site can point readers to the
underlying work without leaving broken navigation. The detailed methodology,
results tables, and discussion live in the repository research note.