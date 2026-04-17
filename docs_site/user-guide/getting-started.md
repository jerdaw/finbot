# Getting Started

This guide will help you get started with Finbot for financial simulation, backtesting, and portfolio optimization.

## What is Finbot?

Finbot is a comprehensive platform for:

- **Data Collection**: Automated fetching from 6+ data sources
- **Simulation**: Model leveraged ETFs, bond ladders, and Monte Carlo scenarios
- **Backtesting**: Test 13 trading strategies with detailed performance metrics
- **Optimization**: Explore DCA schedules and portfolio rebalancing tools

## Installation

### Prerequisites

- Python >=3.11, <3.15
- uv (recommended) or pip
- Optional: API keys for data sources

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install the full contributor environment
uv sync --all-extras

# Minimal CLI/runtime only
# uv sync

# Activate virtual environment (optional, uv creates .venv automatically)
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows

# Set environment (development or production)
export DYNACONF_ENV=development

# Verify installation
DYNACONF_ENV=development uv run finbot --version
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the full contributor environment
pip install -e '.[dashboard,web,nautilus,notebooks]'

# Minimal CLI/runtime only
# pip install -e .

# Set environment
export DYNACONF_ENV=development

# Verify installation
DYNACONF_ENV=development finbot --version
```

## Configuration

### Environment Setup

Finbot uses Dynaconf for environment-aware configuration. Export environment variables directly in your shell or store them in `finbot/config/.env` for local development. Dynaconf auto-loads that `.env` file when `DYNACONF_ENV=development`.

```bash
# finbot/config/.env
DYNACONF_ENV=development

# Optional: API keys for data collection
ALPHA_VANTAGE_API_KEY=your_key_here
NASDAQ_DATA_LINK_API_KEY=your_key_here
US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key_here
GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

### Configuration Files

Finbot loads settings from YAML files based on `DYNACONF_ENV`:

- `finbot/config/settings.yaml`: Base settings (shared across all environments)
- `finbot/config/development.yaml`: Development-specific settings
- `finbot/config/production.yaml`: Production-specific settings

Example development configuration:

```yaml
# finbot/config/development.yaml
threading:
    min_threads: 1
    max_threads: null # Auto-detect CPU cores
    reserved_threads: 2 # Reserve 2 cores for system

logging:
    level: INFO
    json_output: true
```

## First Steps

### 1. Run Tests

Verify your installation by running the test suite:

```bash
# Run all tests
DYNACONF_ENV=development uv run pytest

# Run with verbose output
DYNACONF_ENV=development uv run pytest -v

# Run specific test file
DYNACONF_ENV=development uv run pytest tests/unit/test_imports.py
```

Expected output: the suite completes without failures.

### 2. Update Data

Fetch the latest data from all sources:

```bash
# Run full update (requires API keys)
uv run finbot update

# Dry run (shows what would be updated)
uv run finbot update --dry-run

# Skip price updates
uv run finbot update --skip-prices

# Skip simulations
uv run finbot update --skip-simulations
```

This will:

- Fetch Yahoo Finance and Google Finance price histories
- Update FRED economic data
- Download Shiller datasets
- Re-run overnight LIBOR approximation
- Regenerate all index and fund simulations

### 3. Run Your First Simulation

Simulate a leveraged fund:

```bash
# Simulate UPRO (3x leveraged S&P 500)
uv run finbot simulate --fund UPRO --start 2010-01-01 --plot

# Save results to file
uv run finbot simulate --fund UPRO --start 2010-01-01 --output results/upro_sim.parquet

# See all available funds
uv run finbot simulate --help
```

Available funds: SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, NTSX

### 4. Run Your First Backtest

Test a trading strategy:

```bash
# Backtest a single asset with the current CLI
uv run finbot backtest --strategy NoRebalance --asset SPY --plot

# Save results to file
uv run finbot backtest --strategy SMACrossover --asset QQQ \
  --cash 100000 --output results/backtest.parquet

# See all available strategies
uv run finbot backtest --help
```

CLI strategies: Rebalance, NoRebalance, SMACrossover, SMACrossoverDouble, SMACrossoverTriple, MACDSingle, MACDDual, DipBuySMA, DipBuyStdev, SMARebalMix, DualMomentum, RiskParity

`RegimeAdaptive` is available from the Python API and service layer, but it is not exposed by the current CLI command.

### 5. Optimize a Portfolio

Find optimal asset allocation:

```bash
# Optimize a DCA schedule for one asset
uv run finbot optimize --method dca --asset SPY --plot

# Save the raw trial table
uv run finbot optimize --method dca --asset QQQ \
  --cash 5000 --output results/optimization.parquet
```

The current CLI runs the built-in DCA sweep for a single asset. Use the Python API below when you want direct control over ratio ranges, DCA durations, or trial windows.

## Python API Usage

### Simulate a Fund

```python
from finbot.services.simulation.sim_specific_funds import simulate_fund

# Simulate TQQQ (3x leveraged Nasdaq 100)
tqqq_sim = simulate_fund("TQQQ", save_sim=False)
tqqq_sim = tqqq_sim.loc["2010-02-11":"2024-01-01"]

# Access results
print(tqqq_sim.head())
print(f"Total return: {(tqqq_sim['Close'].iloc[-1] / tqqq_sim['Close'].iloc[0] - 1) * 100:.2f}%")
```

### Run a Backtest

```python
import backtrader as bt

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.utils.data_collection_utils.yfinance.get_history import get_history

# Load data
spy = get_history("SPY", adjust_price=True)
tlt = get_history("TLT", adjust_price=True)

# Create backtest runner
runner = BacktestRunner(
  price_histories={"SPY": spy, "TLT": tlt},
  start=None,
  end=None,
  duration=None,
  start_step=None,
  init_cash=100000,
  strat=Rebalance,
  strat_kwargs={"rebal_proportions": [0.6, 0.4], "rebal_interval": 63},
  broker=bt.brokers.BackBroker,
  broker_kwargs={},
  broker_commission=FixedCommissionScheme,
  sizer=bt.sizers.AllInSizer,
  sizer_kwargs={},
  plot=False,
)

# Run backtest
stats = runner.run_backtest()

print(f"CAGR: {stats['CAGR'].iloc[0]:.2%}")
print(f"Sharpe: {stats['Sharpe'].iloc[0]:.2f}")
print(f"Max Drawdown: {stats['Max Drawdown'].iloc[0]:.2%}")
```

### Optimize DCA Strategy

```python
from finbot.services.optimization.dca_optimizer import dca_optimizer
from finbot.utils.data_collection_utils.yfinance.get_history import get_history

# Load one asset's close history
spy = get_history("SPY", adjust_price=True)["Close"]

# Run the default analysis views
ratio_df, duration_df = dca_optimizer(
  price_history=spy,
  ticker="SPY",
  starting_cash=100000,
)

# View the strongest front-loading ratios and DCA durations
print(ratio_df.head())
print(duration_df.head())
```

Set `analyze_results=False` when you want the raw per-trial DataFrame instead of the aggregated ratio and duration summaries.

## Next Steps

- **[Quick Start Guide](quick-start.md)**: Detailed walkthrough of common tasks
- **[CLI Reference](cli-reference.md)**: Complete command-line interface documentation
- **[API Reference](../api/index.md)**: Detailed API documentation for all modules
- **[Configuration Guide](configuration.md)**: Advanced configuration options
- **[Example Notebooks](https://github.com/jerdaw/finbot/tree/main/notebooks)**: Jupyter notebooks with analysis examples

## Common Issues

### Import Errors

If you see import errors, ensure you've installed all dependencies:

```bash
uv sync --all-extras
# or
pip install -e '.[dashboard,web,nautilus,notebooks]'
```

### API Key Errors

If data collection fails with "OSError: API key not found":

1. Export the relevant environment variable in your shell, or add it to `finbot/config/.env` for local development
2. Confirm `DYNACONF_ENV` is set correctly
3. Restart your shell / reload environment

### No Data Available

If simulations fail with "no data available":

1. Run `uv run finbot update` to fetch data
2. Check that `finbot/data/` subdirectories are populated
3. Verify API keys are configured correctly

### Permission Errors

If you see permission errors on `finbot/data/` directories:

```bash
# Linux/Mac
chmod -R 755 finbot/data

# Windows (run as administrator)
icacls finbot\data /grant Users:F /t
```

## Getting Help

- **Documentation**: [Full API Reference](../api/index.md)
- **Issues**: [GitHub Issues](https://github.com/jerdaw/finbot/issues)
- **Examples**: [Jupyter Notebooks](https://github.com/jerdaw/finbot/tree/main/notebooks)
- **Research**: [Published Findings](../research/index.md)

## Development Setup

If you plan to contribute:

```bash
# Install dev dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run code quality checks
make check  # Runs lint, format, type, security

# Run tests with coverage
make test-cov
```

See [Contributing Guide](../contributing.md) for details.
