# Why I Built Finbot: A Developer's Journey from Spreadsheets to Systematic Backtesting

*Originally published: 2026-02-17*
*Reading time: ~8 minutes*

---

It started with a spreadsheet.

Like many people interested in personal finance, I started my investing journey with a few cells in Excel, manually tracking my portfolio performance. I'd pull prices from Google Finance every weekend, paste them in, and stare at the numbers. Was I doing well? Better than just holding the S&P 500? Better than a bond ladder? I genuinely didn't know. The spreadsheet could tell me what *had* happened, but it couldn't tell me what *would* happen — or more importantly, what *would have* happened if I'd done something different.

That question — "what would have happened?" — eventually became Finbot.

---

## The Problem With Gut Instinct Investing

There's a seductive simplicity to financial advice. Everyone has a hot take. "Just buy index funds." "Rebalance every quarter." "Dollar-cost average in." "Leveraged ETFs are too risky." "Leveraged ETFs are the only rational choice." "3x leverage will eventually ruin you." "Here's why 3x leverage won't ruin you."

The frustrating thing is that many of these claims are based on anecdote, short time windows, or survivorship bias. And when I started digging into the actual research, I found that even the peer-reviewed literature was often contradictory, cherry-picked, or limited to a specific market regime.

I wanted to *test* these ideas myself. Not just read about them — actually run the numbers on historical data, under realistic conditions, with realistic costs. That's much harder than it sounds.

---

## Why the Existing Tools Weren't Enough

The obvious answer is "just use an existing backtesting library." And I tried. I explored several options:

**Spreadsheets** are fine for simple scenarios but collapse under complexity. The moment you want to model realistic execution costs, rebalancing logic, or leverage decay, you're fighting the tool.

**Off-the-shelf platforms** (like Portfolio Visualizer) are excellent for quick lookups, but they're black boxes. I couldn't inspect how they calculated leveraged ETF returns, couldn't modify assumptions, couldn't test the exact strategy I was thinking about.

**Python libraries** like Backtrader are powerful but have a steep learning curve and their documentation is sparse. And the gap between "backtest works great" and "strategy runs live" turns out to be enormous — different data formats, execution assumptions, cost models, and more.

What I wanted was something in between: the transparency and control of writing code myself, but with the infrastructure already built out — data collection, cost modeling, performance metrics, visualization.

So I built it.

---

## Three Years of Iteration (Across Three Repos)

Finbot didn't start as Finbot. It started as three separate projects that gradually grew toward each other:

1. **finbot** — data collection scripts that pulled prices from Yahoo Finance and FRED
2. **bb** — a backtesting engine that used Selenium to fetch Google Finance data
3. **backbetter** — an attempt at a more principled simulation framework

Each had good ideas but serious problems. The data collection scripts had no caching, no rate limiting, and would hammer APIs on every run. The backtesting engine mixed data fetching with strategy logic in ways that made testing nearly impossible. The simulation framework never quite worked for leveraged ETFs.

The consolidation into a single codebase — documented in ADR-001 — was painful but necessary. Along the way, I made several architectural decisions that turned out to be right:

- **Drop numba.** It seemed like an obvious win for performance, but the compilation overhead, the Python 3.12 incompatibility, and the debugging pain weren't worth it. Vectorized numpy was fast enough and much more maintainable.
- **Replace pickle with parquet.** Pickle files silently break across Python versions. Parquet files are self-describing, fast, and interoperable.
- **Lazy API key loading.** Failing loudly at import time when a key isn't needed is a terrible developer experience. Load keys only when they're actually used.

---

## What Finbot Can Do (Now)

After three years of iteration and a major consolidation effort, Finbot covers a lot of ground:

**Data Collection** — Automated pipelines for Yahoo Finance, FRED, Alpha Vantage, Google Finance, Shiller datasets, and BLS. Data is cached locally as parquet files, with freshness monitoring to detect staleness.

**Simulation** — The crown jewel: a vectorized fund simulator that can model leveraged ETFs back to 1950, accounting for management fees, bid-ask spreads, and LIBOR borrowing costs. I can simulate UPRO's behavior during the 2008 financial crisis with a few lines of Python.

**Backtesting** — An engine-agnostic system using Backtrader (and optionally NautilusTrader) with 12 built-in strategies, typed contracts for portability, cost models, corporate action handling, walk-forward analysis, and market regime detection.

**Execution Simulation** — A paper trading simulator with realistic latency, slippage, risk controls (position limits, drawdown protection), and state checkpoints for disaster recovery.

**Health Economics** — Probably the most unexpected feature. QALY simulators, cost-effectiveness analysis, and treatment optimization — applying quantitative methods from the investing world to healthcare economics.

---

## What I Actually Learned (That the Code Doesn't Show)

The technical output is documented in the code. What's harder to see are the lessons that shaped how I approached problems.

**Backtesting is easy to do wrong in 100 different ways.** Survivorship bias, look-ahead bias, transaction cost optimism, overfitting, incorrect return calculation — every one of these can turn a losing strategy into a paper winner. Building good tooling forced me to confront each of these issues directly.

**Simple strategies often beat complex ones.** I built twelve backtesting strategies. After all that work, the results consistently pointed to the same boring conclusion: buy-and-hold with periodic rebalancing is hard to beat over long time periods. The complex momentum strategies occasionally outperform, but not reliably enough to justify the complexity.

**Software engineering principles matter even in research code.** The messy three-repo state I started with was a productivity killer. Tests that didn't exist meant I couldn't refactor confidently. Lack of type hints meant I spent hours debugging type errors. The investment in code quality paid off in velocity.

**Health economics and financial economics have more in common than I expected.** Cost-effectiveness analysis (ICER, QALY) uses the same mathematical infrastructure as portfolio optimization. Probabilistic sensitivity analysis is just Monte Carlo simulation. The tools transfer.

---

## The Medical School Connection

I'll be transparent about something: I'm applying to medical school, and this project is partly a portfolio piece. That might seem like a strange admission in a technical blog post, but I think it's worth explaining.

I'm applying to medicine because I'm genuinely interested in the quantitative and systems-level aspects of healthcare. Health economics, evidence-based medicine, clinical research — these are areas where the kind of systematic, data-driven thinking I've been developing translates directly.

Building Finbot demonstrated that I can:
- Take a complex domain (quantitative finance) and build tools that produce useful insights
- Maintain quality standards (60%+ test coverage, continuous integration, rigorous documentation) over an extended project
- Apply quantitative methods across domains (hence the health economics extension)
- Communicate technical results to non-technical audiences (hence the Jupyter notebooks and Streamlit dashboard)

The CanMEDS framework that guides Canadian medical education emphasizes roles like Scholar, Communicator, and Professional. Those aren't abstract ideals — they're exactly the capacities I've been developing while building this.

---

## What's Next

Priority 7 focuses on external impact: publishing research findings, creating tutorial content, and deepening the health economics capabilities.

The technical roadmap continues with:
- **Multi-objective portfolio optimization** using Pareto frontier methods
- **Regime-adaptive strategies** that adjust behavior based on detected market conditions
- **Statistical hypothesis testing** for rigorous strategy comparison
- **NautilusTrader migration guide** for teams ready to move toward live trading

But honestly, the most interesting next chapter isn't technical — it's medical school. If Finbot helped me get there, it will have been worth every hour.

---

## Resources

If you want to explore the codebase:

- **GitHub:** [github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)
- **Documentation:** [jerdaw.github.io/finbot](https://jerdaw.github.io/finbot)
- **Quick start:** `pip install uv && uv run finbot --help`

The research notebooks in `notebooks/` are the best starting point for understanding what the system can do. Start with `01_fund_simulation_demo.ipynb` and work forward.

---

*Questions or feedback? Open an issue on GitHub or reach out directly.*

---

**Tags:** Python, quantitative finance, backtesting, health economics, software engineering, personal projects
