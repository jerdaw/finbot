# Finbot

Financial data collection, simulation, and backtesting platform.

[![CI](https://github.com/jer/finbot/actions/workflows/ci.yml/badge.svg)](https://github.com/jer/finbot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jer/finbot/branch/main/graph/badge.svg)](https://codecov.io/gh/jer/finbot)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.7+-blue.svg)](https://python-poetry.org/)

## Quick Start

```bash
# Install dependencies
make install

# Set environment
export DYNACONF_ENV=development

# Run all code quality checks
make check

# Run tests
make test

# Run daily data pipeline
make run-update
```

**Makefile Commands:**
- `make help` - Show all available commands
- `make install` - Install dependencies with Poetry
- `make test` - Run all tests with verbose output
- `make check` - Run all code quality checks (lint, format, type, security)
- `make clean` - Remove cache files and build artifacts
- `make all` - Run full CI pipeline (check + test)

## Prerequisites

| Requirement | Minimum Version |
| --- | --- |
| **Python** | 3.11+ |
| **Poetry** | 1.7+ |

## Usage

### Backtesting

```python
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.strategies.rebalance import Rebalance

runner = BacktestRunner(
    price_histories={"SPY": spy_df, "TLT": tlt_df},
    start=None, end=None, duration=None, start_step=None,
    init_cash=100000,
    strat=Rebalance,
    strat_kwargs={"rebal_proportions": (0.6, 0.4), "rebal_interval": 63},
    broker=bt.brokers.BackBroker, broker_kwargs={},
    broker_commission=FixedCommissionScheme,
    sizer=AllInSizer, sizer_kwargs={},
    plot=False,
)
stats = runner.run_backtest()
```

### Fund Simulation

```python
from finbot.services.simulation.fund_simulator import fund_simulator

# Simulate a 3x leveraged S&P 500 fund
fund_df = fund_simulator(
    price_df=sp500_price_history,
    leverage_mult=3,
    annual_er_pct=0.91 / 100,
    percent_daily_spread_cost=0.015 / 100,
    fund_swap_pct=2.5 / 3,
)
```

### Monte Carlo Simulation

```python
from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator

trials_df = monte_carlo_simulator(equity_data=spy_df, sim_periods=252, n_sims=10000)
```

## Settings Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `DYNACONF_ENV` | Yes | `development` or `production` |
| `ALPHA_VANTAGE_API_KEY` | For data collection | Alpha Vantage API access |
| `NASDAQ_DATA_LINK_API_KEY` | For data collection | Nasdaq Data Link access |
| `US_BUREAU_OF_LABOR_STATISTICS_API_KEY` | For data collection | BLS API access |
| `GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH` | For data collection | Google Sheets service account |

## Development

### Using Makefile (Recommended)

```bash
make lint       # Run ruff linter with auto-fix
make format     # Format code with ruff
make type       # Run mypy type checker
make security   # Run bandit security scanner
make test       # Run all tests
make test-cov   # Run tests with coverage report
make check      # Run all checks (lint + format + type + security)
make all        # Run full CI pipeline (check + test)
```

### Direct Poetry Commands

```bash
poetry run ruff check . --fix   # Lint
poetry run ruff format .        # Format
poetry run mypy                 # Type check
poetry run pytest               # Test
```

Run `make help` to see all available commands.

## Architecture

See [docs/adr/](docs/adr/) for architectural decision records.

**Data pipeline:** Data Collection (utils) -> Simulations (services) -> Backtesting (services) -> Performance Analysis

| Layer | Purpose |
| --- | --- |
| `config/` | Dynaconf-based environment configuration |
| `constants/` | Application constants and path definitions |
| `libs/` | API manager and async logger |
| `finbot/utils/` | Data collection, finance, pandas, datetime utilities |
| `finbot/services/simulation/` | Fund, index, bond ladder, Monte Carlo simulators |
| `finbot/services/backtesting/` | Backtrader-based backtesting engine with strategies |
| `finbot/services/optimization/` | DCA and rebalance portfolio optimizers |
| `scripts/` | Daily data update pipeline |
