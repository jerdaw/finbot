# Getting Started

This guide will help you get started with Finbot for financial simulation, backtesting, and portfolio optimization.

## What is Finbot?

Finbot is a comprehensive platform for:

- **Data Collection**: Automated fetching from 6+ data sources
- **Simulation**: Model leveraged ETFs, bond ladders, and Monte Carlo scenarios
- **Backtesting**: Test 10 trading strategies with detailed performance metrics
- **Optimization**: Find optimal portfolios using DCA and rebalancing strategies

## Installation

### Prerequisites

- Python >=3.11, <3.15
- Poetry (recommended) or pip
- Optional: API keys for data sources

### Install with Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install dependencies
uv sync

# Activate virtual environment
poetry shell

# Set environment (development or production)
export DYNACONF_ENV=development

# Verify installation
finbot --version
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Verify installation
finbot --version
```

## Configuration

### Environment Setup

Finbot uses Dynaconf for environment-aware configuration. Create a `.env` file in the `config/` directory:

```bash
# config/.env
DYNACONF_ENV=development

# Optional: API keys for data collection
ALPHA_VANTAGE_API_KEY=your_key_here
NASDAQ_DATA_LINK_API_KEY=your_key_here
US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key_here
GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

### Configuration Files

Finbot loads settings from YAML files based on `DYNACONF_ENV`:

- `config/settings.yaml`: Base settings (shared across all environments)
- `config/development.yaml`: Development-specific settings
- `config/production.yaml`: Production-specific settings

Example development configuration:

```yaml
# config/development.yaml
threading:
  min_threads: 1
  max_threads: null  # Auto-detect CPU cores
  reserved_threads: 2  # Reserve 2 cores for system

logging:
  level: INFO
  json_output: true
```

## First Steps

### 1. Run Tests

Verify your installation by running the test suite:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_imports.py
```

Expected output: `80 passed` (all tests should pass)

### 2. Update Data

Fetch the latest data from all sources:

```bash
# Run full update (requires API keys)
finbot update

# Dry run (shows what would be updated)
finbot update --dry-run

# Skip price updates
finbot update --skip-prices

# Skip simulations
finbot update --skip-simulations
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
finbot simulate --fund UPRO --start 2010-01-01 --plot

# Save results to file
finbot simulate --fund UPRO --start 2010-01-01 --output results/upro_sim.parquet

# See all available funds
finbot simulate --help
```

Available funds: SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, NTSX

### 4. Run Your First Backtest

Test a trading strategy:

```bash
# Backtest rebalancing strategy on 60/40 portfolio
finbot backtest --strategy Rebalance --asset SPY,TLT --plot

# Backtest with custom parameters
finbot backtest --strategy Rebalance --asset SPY,TLT \
  --cash 100000 --commission 0.001 --output results/backtest.csv

# See all available strategies
finbot backtest --help
```

Available strategies: Rebalance, NoRebalance, SMACrossover, SMACrossoverDouble, SMACrossoverTriple, MACDSingle, MACDDual, DipBuySMA, DipBuyStdev, SMARebalMix

### 5. Optimize a Portfolio

Find optimal asset allocation:

```bash
# Optimize SPY/TLT allocation with DCA strategy
finbot optimize --method dca --assets SPY,TLT --plot

# Custom optimization parameters
finbot optimize --method dca --assets SPY,TLT \
  --duration 1825 --interval 30 --ratios 0.5,0.95,10 \
  --output results/optimization.parquet
```

## Python API Usage

### Simulate a Fund

```python
from finbot.services.simulation.fund_simulator import simulate_fund

# Simulate TQQQ (3x leveraged Nasdaq 100)
tqqq_sim = simulate_fund('TQQQ', start_date='2010-02-11', end_date='2024-01-01')

# Access results
print(tqqq_sim.head())
print(f"Total return: {(tqqq_sim['Close'][-1] / tqqq_sim['Close'][0] - 1) * 100:.2f}%")
```

### Run a Backtest

```python
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.utils.data_collection_utils.yfinance import get_history

# Load data
spy = get_history('SPY', start='2010-01-01')
tlt = get_history('TLT', start='2010-01-01')

# Create backtest runner
runner = BacktestRunner(
    strategy='Rebalance',
    data_feeds={'SPY': spy, 'TLT': tlt},
    strategy_params={'rebalance_days': 30, 'target_allocations': {'SPY': 0.6, 'TLT': 0.4}},
    cash=100000,
    commission=0.001
)

# Run backtest
results = runner.run()
stats = runner.get_stats()

print(f"CAGR: {stats['CAGR']:.2%}")
print(f"Sharpe: {stats['Sharpe']:.2f}")
print(f"Max Drawdown: {stats['Max Drawdown']:.2%}")
```

### Optimize DCA Strategy

```python
from finbot.services.optimization.dca_optimizer import dca_optimizer
import pandas as pd

# Load and merge price data
spy = get_history('SPY')['Close']
tlt = get_history('TLT')['Close']
combined = pd.DataFrame({'SPY': spy, 'TLT': tlt}).dropna()

# Run optimizer
results = dca_optimizer(
    price_history=combined,
    ratio_linspace=(0.50, 0.95, 10),
    dca_duration_days=365 * 5,
    dca_step_days=30,
    trial_duration_days=365 * 10,
    starting_cash=100000
)

# View best allocation
print(results.head())
print(f"Optimal: {results.iloc[0]['ratio']:.0%} SPY / {1-results.iloc[0]['ratio']:.0%} TLT")
print(f"Expected Sharpe: {results.iloc[0]['sharpe']:.2f}")
```

## Next Steps

- **[Quick Start Guide](quick-start.md)**: Detailed walkthrough of common tasks
- **[CLI Reference](cli-reference.md)**: Complete command-line interface documentation
- **[API Reference](../api/index.md)**: Detailed API documentation for all modules
- **[Configuration Guide](configuration.md)**: Advanced configuration options
- **[Example Notebooks](../../notebooks/)**: Jupyter notebooks with analysis examples

## Common Issues

### Import Errors

If you see import errors, ensure you've installed all dependencies:

```bash
uv sync
# or
pip install -e .
```

### API Key Errors

If data collection fails with "OSError: API key not found":

1. Create `config/.env` file
2. Add the relevant API key (see Configuration section)
3. Restart your shell / reload environment

### No Data Available

If simulations fail with "no data available":

1. Run `finbot update` to fetch data
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
- **Examples**: [Jupyter Notebooks](../../notebooks/)
- **Research**: [Published Findings](../research/index.md)

## Development Setup

If you plan to contribute:

```bash
# Install dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run code quality checks
make check  # Runs lint, format, type, security

# Run tests with coverage
make test-cov
```

See [Contributing Guide](../contributing.md) for details.
