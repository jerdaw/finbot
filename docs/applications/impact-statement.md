# Impact Statement: Finbot

**Document:** Medical School Application Portfolio — Impact Statement
**Date:** 2026-02-17
**Word count:** ~500 words

---

## Finbot: Quantitative Tools for Better Financial and Health Decisions

Over three years, I built Finbot from a spreadsheet into a production-grade quantitative analysis platform. The concrete outcomes are measurable.

**Scale of the work:** 15,000+ lines of original Python across 170+ modules; 866 automated tests achieving 61.6% code coverage; 113 pages of documentation; 8 research notebooks. The CI/CD pipeline runs 7 automated checks on every change, including performance regression testing with a 20% tolerance threshold. The project is governed by a complete suite of community health documents (LICENSE, CODE_OF_CONDUCT, SECURITY, CONTRIBUTING, CODEOWNERS) and has been published as an open-source project on GitHub.

**Research findings:** 12 investment strategies backtested across 40+ years of historical data. The finding that emerged most clearly and most consistently: simple buy-and-hold with low-cost index funds outperforms complex timing strategies over long time horizons in the majority of market conditions. This conclusion — documented in research summaries and Jupyter notebooks — is consistent with the academic literature on active management. Having tested it myself, rather than simply reading about it, makes the evidence viscerally real in a way that reading alone does not.

**Simulation capability:** The fund simulator models leveraged ETFs (UPRO, TQQQ, TMF, and 13 others) back to 1950, accounting for management fees, bid-ask spreads, and LIBOR borrowing costs. This is infrastructure that would have taken weeks to build from scratch for any individual researcher. As open-source, it is freely available to anyone who wants to study leveraged fund dynamics.

**Health economics extension:** The QALY simulator, cost-effectiveness analysis module, and treatment optimizer implement methods used daily by NICE, CADTH, and similar health technology assessment bodies. Three published tutorial posts explain these methods in accessible terms with runnable Python code. A researcher with a Python environment and Finbot installed can run a full probabilistic cost-effectiveness analysis in under 30 lines of code.

**Personal impact:** Finbot's analysis directly informed my own financial decisions — when to rebalance, how to think about risk in leveraged ETFs, how to structure a long-term DCA program. The discipline of testing investment ideas systematically rather than on gut instinct has made me a more rational decision-maker in domains well beyond finance.

**Technical skills developed:** Production-grade Python software engineering; statistical simulation and Monte Carlo methods; health economics methodology (QALYs, ICER, NMB, CEAC); backtesting frameworks (Backtrader, NautilusTrader); event-driven system design; CI/CD pipeline construction; quantitative finance.

**What makes this worth noting in an application:** Medicine is a field that runs on evidence, analysis, and systematic thinking. Finbot demonstrates three years of commitment to exactly those practices — not in a course, not under supervision, but as an independent research project sustained over time. The extension to health economics demonstrates that the same quantitative methods transfer to clinical questions, and that I have both the interest and the capacity to engage those methods seriously.

---

*Full project documentation: [github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)*
