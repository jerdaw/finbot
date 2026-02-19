# Finbot — Portfolio Summary

*Quantitative Finance & Health Economics Research Platform*
*GitHub: [github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)*

---

## The Problem

How do different investment strategies — buy-and-hold, quarterly rebalancing, momentum, risk parity — perform over 40 years of market history? How does a leveraged ETF like UPRO actually behave during a financial crisis? When is the GLP-1 agonist cost-effective relative to Metformin for type 2 diabetes management?

These questions matter. They affect retirement security, healthcare coverage decisions, and individual financial outcomes. They deserve systematic, evidence-based answers — not gut instinct.

---

## The Approach

I built Finbot over three years as an independent research project to answer these questions with the same rigor applied in academic research:

- Vectorized simulation (not approximation) of leveraged ETFs back to 1950
- Backtest 12 investment strategies with realistic transaction costs, slippage, and corporate action handling
- Monte Carlo probabilistic sensitivity analysis for both portfolio returns and QALY outcomes
- Walk-forward analysis and market regime detection to test strategy robustness
- Cost-effectiveness analysis using ICER, NMB, and CEAC — standard health technology assessment methods

---

## Key Achievements

| Metric | Value |
|--------|-------|
| Lines of original Python code | 15,000+ |
| Automated tests | 866 (all passing) |
| Code coverage | 61.6% |
| Documentation pages | 113 |
| Research notebooks | 8 |
| Strategies backtested | 12 |
| Fund simulations | 16 (SPY, UPRO, TQQQ, TMF, and more) |
| CI/CD checks per commit | 7 |
| Years of data analyzed | 40+ (equity), 50+ (leveraged ETF sim) |

---

## Technical Highlights

**Engine-agnostic backtesting:** Typed contracts allow the same strategy code to run on Backtrader (bar-based, mature) or NautilusTrader (event-driven, Rust core, built for live trading). A parity gate in CI prevents the engines from diverging — 100% parity maintained on all golden strategies.

**Health economics module:** Full probabilistic CEA pipeline implemented from scratch: `HealthIntervention → simulate_qalys() → cost_effectiveness_analysis() → optimize_treatment()`. Implements the same methods used by NICE and CADTH. Three published tutorials explain the methods with clinical scenarios and runnable code.

**Production-quality infrastructure:** 7-job CI/CD pipeline (lint, type-check, security, test, docs, parity, performance), Docker containerization, structured JSON audit logging, SHA-pinned GitHub Actions for supply chain security, scheduled daily data updates.

---

## Research Findings

The most important finding from 12 strategies and 40 years of data: **simple buy-and-hold with low-cost index funds is extraordinarily hard to beat consistently over long time horizons.** Complex timing strategies occasionally outperform, but not reliably enough to justify the additional complexity, tax drag, or behavioral risk.

This is consistent with academic research on active management — and having tested it rigorously myself makes the evidence far more compelling than reading a paper.

---

## Skills Demonstrated

Python · NumPy · Pandas · Backtrader · NautilusTrader · Streamlit · pytest · mypy · Docker · GitHub Actions · Health economics (QALY/ICER/CEA) · Statistical simulation · Monte Carlo methods · Time-series analysis · Software architecture

---

## Relevance to Medicine

Health economics uses the same mathematical infrastructure as financial economics: discounted cash flows become discounted QALYs; portfolio optimization becomes treatment schedule optimization; Monte Carlo portfolio simulation becomes probabilistic sensitivity analysis. The quantitative methods transfer directly.

Building Finbot taught me to approach complex, uncertain, high-stakes decisions with structured analysis rather than intuition — the same approach medicine requires.

---

*This document is part of a medical school application portfolio. Created: 2026-02-17.*
