# Finbot

Financial data collection, simulation, and backtesting platform.

## Quick Start

```bash
# Install
poetry install

# Set environment
export DYNACONF_ENV=development

# Run daily data pipeline
poetry run python scripts/update_daily.py

# Run tests
poetry run pytest
```

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

```bash
poetry run ruff check . --fix   # Lint
poetry run ruff format .        # Format
poetry run mypy                 # Type check
poetry run pytest               # Test
```

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
