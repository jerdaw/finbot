# Finbot Frequently Asked Questions

**Last updated:** 2026-02-17

---

## Getting Started

### Q: What is Finbot?

Finbot is a quantitative analysis platform for personal finance research. It provides tools for:
- **Fund simulation**: Model leveraged ETFs (UPRO, TQQQ, TMF, etc.) back to 1950 with realistic costs
- **Backtesting**: Test 12 investment strategies on historical data with realistic transaction costs
- **Portfolio optimization**: Find optimal dollar-cost averaging and rebalancing schedules
- **Monte Carlo simulation**: Simulate probability distributions of future portfolio outcomes
- **Health economics**: QALY simulation, cost-effectiveness analysis, treatment optimization

It is a research tool, not financial advice. See [DISCLAIMER.md](../../DISCLAIMER.md).

---

### Q: Who is Finbot for?

Finbot is designed for quantitatively-minded individuals who want to test investment ideas systematically rather than relying on gut instinct or off-the-shelf platforms. You should be comfortable writing Python code.

---

### Q: How do I install Finbot?

```bash
# Install uv (fast Python package manager)
pip install uv

# Clone the repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install dependencies
uv sync

# Verify installation
uv run finbot --help
```

See [docs_site/user-guide/installation.md](../../docs_site/user-guide/installation.md) for full details.

---

### Q: What Python versions are supported?

Python 3.11, 3.12, and 3.13. CI tests all three versions on every commit.

**Note:** NautilusTrader requires Python 3.12+. If you only use Backtrader for backtesting, Python 3.11 is sufficient.

---

### Q: Do I need API keys to use Finbot?

For basic functionality (simulation, backtesting with cached data), no API keys are required.

API keys are only needed for live data collection:
- **Alpha Vantage**: Economic indicators, sentiment data
- **NASDAQ Data Link**: Additional historical data
- **BLS**: Bureau of Labor Statistics data
- **Google Finance**: MSCI index data (requires service account)

Yahoo Finance (yfinance) and FRED data work without API keys for most purposes.

---

## Backtesting

### Q: What strategies are included?

12 built-in strategies:
1. `NoRebalance` — Buy and hold
2. `Rebalance` — Periodic portfolio rebalancing
3. `SmaCrossover` — Single SMA crossover
4. `SmaCrossoverDouble` — Dual SMA crossover
5. `SmaCrossoverTriple` — Triple SMA (slow/medium/fast)
6. `MacdSingle` — MACD signal line
7. `MacdDual` — MACD with two timeframes
8. `DipBuySma` — Buy dips below SMA
9. `DipBuyStdev` — Buy dips below standard deviation bands
10. `SmaRebalMix` — Combined SMA + rebalancing
11. `DualMomentum` — Absolute + relative momentum with safe-asset fallback
12. `RiskParity` — Inverse-volatility weighting with rebalancing

---

### Q: How realistic are the backtests?

More realistic than most consumer tools, but imperfect. Finbot accounts for:
- **Commissions**: Configurable per-trade fixed commissions
- **Slippage**: Configurable execution slippage model
- **Bid-ask spreads**: In fund simulations
- **Management fees**: In leveraged ETF simulations
- **Corporate actions**: Dividend reinvestment, stock splits
- **LIBOR/borrowing costs**: In leveraged fund simulations

Finbot does **not** account for:
- Taxes (capital gains, dividend tax)
- Exact intraday execution timing
- Market impact of large orders
- Survivorship bias in the asset universe (you choose what to test)
- Look-ahead bias (protected against by design, but always worth verifying)

For a complete list of limitations, see [docs/limitations.md](../../docs/limitations.md).

---

### Q: What is the difference between Backtrader and NautilusTrader?

Backtrader uses a **bar-based model**: your strategy receives one complete OHLCV bar at each step and decides to trade. Simple and predictable.

NautilusTrader uses an **event-driven model**: your strategy receives discrete events (BarEvent, OrderFilled, PositionChanged) that more accurately reflect how real markets work. More realistic fills, but a steeper learning curve.

**Quick guide:**
- For pure research/backtesting: Backtrader
- For strategies intended for live trading: NautilusTrader

See [docs/guides/choosing-backtest-engine.md](choosing-backtest-engine.md) and [ADR-011](../adr/ADR-011-nautilus-decision.md) for full details.

---

### Q: How do I run a backtest?

```bash
# CLI
uv run finbot backtest --strategy NoRebalance --symbols SPY --start 2000-01-01

# Python
from finbot.services.backtesting.run_backtest import run_backtest
from finbot.core.contracts.models import BacktestRunRequest

request = BacktestRunRequest(
    strategy_name="NoRebalance",
    symbols=["SPY"],
    start="2000-01-01",
    end="2024-01-01",
    initial_cash=100_000,
)
result = run_backtest(request)
print(result.metrics)
```

See [notebooks/](../../notebooks/) for complete examples.

---

### Q: Can I backtest a custom strategy?

Yes. Create a class that inherits from `bt.Strategy` (Backtrader) and register it. See the existing strategy files in `finbot/services/backtesting/strategies/` for examples.

For NautilusTrader strategies, see [docs/guides/nautilus-migration-guide.md](nautilus-migration-guide.md).

---

### Q: What are "golden strategies" and why do they matter?

Golden strategies (GS-01: NoRebalance, GS-02: Rebalance, GS-03: SmaCrossover) are reference strategies used to validate engine parity. The CI pipeline runs both Backtrader and NautilusTrader on identical data and verifies that CAGR, Sharpe ratio, and max drawdown match within 1 basis point.

This parity gate prevents silent discrepancies between the two engines from creeping in undetected.

---

## Simulation

### Q: How does the fund simulator work?

The fund simulator models leveraged ETFs using the daily compounding equation:

```
daily_return = (underlying_change × leverage) - daily_expenses
fund_value *= (1 + daily_return)
```

Where `daily_expenses` = management fee + bid-ask spread cost + LIBOR borrowing cost (for leveraged funds). This allows accurate simulation of UPRO (3x S&P 500) and similar ETFs back to 1950 using S&P 500 daily return data — before the ETFs themselves existed.

---

### Q: Can I simulate funds that don't exist yet?

Yes. The `_sim_fund()` helper function takes a leverage factor, expense ratio, and spread, and can simulate any hypothetical leveraged or inverse fund. See `finbot/services/simulation/fund_simulator.py`.

---

### Q: How accurate is the leveraged ETF simulation?

Highly accurate for long-run analysis. Finbot's simulation has been validated against published UPRO, SSO, TQQQ, and TMF returns for periods where actual ETF data exists. Typical error is <0.5% annualized CAGR over long periods.

The main source of error is the LIBOR approximation (Finbot estimates overnight LIBOR from the 3-month T-bill rate; the actual LIBOR rate isn't publicly available for the full historical period).

---

### Q: What is walk-forward analysis?

Walk-forward analysis splits your historical data into multiple train/test windows and backtests each window independently. This tests whether a strategy that worked in one period also works in subsequent periods — a stronger test of robustness than a single in-sample backtest.

See `finbot/core/contracts/walkforward.py` and the walk-forward notebooks.

---

## Data

### Q: Where does historical data come from?

- **Equity prices**: Yahoo Finance (via `yfinance`) for US stocks, ETFs, and international indices
- **Economic data**: Federal Reserve (FRED) — interest rates, CPI, GDP, unemployment
- **Index data**: Google Finance (via Sheets API) — MSCI indices, ICE treasury indices
- **Cape/Shiller data**: Shiller's online datasets — long-run market data back to 1871
- **Sentiment**: Alpha Vantage (API key required)

---

### Q: How is data cached?

All fetched data is cached locally as Parquet files in `finbot/data/`. Parquet was chosen over pickle for safety (pickle breaks across Python versions), speed (columnar format is faster for time-series), and interoperability (readable by R, Spark, etc.).

Cache freshness is monitored by the data quality module (`finbot/services/data_quality/`). Run `uv run finbot status` to see stale data sources.

---

### Q: How do I update data to the latest?

```bash
# CLI
uv run finbot update

# Or directly
uv run python scripts/update_daily.py
```

This runs the full data collection pipeline: Yahoo Finance prices, FRED data, Google Finance indices, Shiller data, and re-runs all simulations.

---

## Health Economics

### Q: Why does a finance tool have health economics features?

Health economics and financial economics use the same mathematical infrastructure: Monte Carlo simulation, discounting, optimization, probabilistic sensitivity analysis. The methods transfer directly.

The health economics extension demonstrates this cross-domain applicability and provides tools relevant to clinical research and healthcare policy analysis.

---

### Q: What is a QALY?

A Quality-Adjusted Life Year combines length of life (years) with quality of life (utility, 0-1 scale):
```
QALY = Years of Life × Health Utility
```

1.0 = perfect health. 0.0 = death. 0.7 = typical utility for well-managed chronic condition.

See [docs/blog/health-economics-part1-qaly.md](../blog/health-economics-part1-qaly.md) for a full explanation.

---

### Q: What is an ICER?

Incremental Cost-Effectiveness Ratio:
```
ICER = ΔCost / ΔQALY
```

The cost of generating one additional QALY compared to the comparator. If ICER < willingness-to-pay threshold (e.g., $50,000/QALY in Canada, $100,000+ in the US), the intervention is considered cost-effective.

---

## Technical

### Q: Why uv instead of pip/poetry?

`uv` is dramatically faster than pip and poetry for installing packages, is a drop-in replacement for both, and is the modern standard for Python project management. Finbot migrated from poetry in Priority 4.

---

### Q: Why parquet instead of CSV or pickle?

| Format | Problem |
|--------|---------|
| CSV | Slow to read/write, no type information, no compression by default |
| Pickle | Breaks across Python versions, not interoperable, security risks |
| Parquet | Fast columnar format, self-describing types, compressed, interoperable |

Parquet files in Finbot are readable by pandas, Polars, Arrow, R, Spark, and any other tool that supports the Apache Parquet format.

---

### Q: How is the CI/CD pipeline structured?

7 jobs run on every push/PR to main:
1. **Lint**: `ruff check` (code style, imports, security patterns)
2. **Format**: `ruff format --check`
3. **Type check**: `mypy finbot/`
4. **Security**: `bandit` + `pip-audit`
5. **Test**: `pytest` across Python 3.11, 3.12, 3.13 (866 tests, 61.6% coverage)
6. **Parity gate**: Golden strategy results match between Backtrader and Nautilus within 1bp
7. **Performance**: Benchmark fund_simulator and backtest_adapter; fails if >20% slower than baseline

---

### Q: How do I run tests?

```bash
# All tests
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Specific pattern
uv run pytest -k "backtest" -v

# With coverage
uv run pytest --cov=finbot --cov-report=term-missing tests/

# Integration tests (require data files)
uv run pytest tests/integration/ -v
```

---

### Q: How do I contribute?

1. Fork the repository on GitHub
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make changes and write tests
4. Run the pre-commit suite: `uv run pre-commit run --all-files`
5. Commit with conventional commit format: `feat(backtesting): add my feature`
6. Push and open a pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for complete guidelines.

---

### Q: The documentation says "not financial advice." What does that mean?

Finbot is a research tool. It provides analysis of historical data and simulated scenarios, not recommendations for what you should do with your money. Past performance does not predict future results. All investment decisions carry risk. Always consult a qualified financial advisor before making investment decisions.

See [DISCLAIMER.md](../../DISCLAIMER.md) for the full disclaimer.

---

## Still Have Questions?

- **GitHub Issues**: [github.com/jerdaw/finbot/issues](https://github.com/jerdaw/finbot/issues)
- **Documentation site**: [jerdaw.github.io/finbot](https://jerdaw.github.io/finbot)
- **Source code**: [github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)
