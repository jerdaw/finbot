# CLI Reference

The Finbot CLI provides command-line access to simulations, backtesting, optimization, data updates, and status monitoring.

## Overview

The CLI is built with Click and provides:

- **5 main commands**: simulate, backtest, optimize, update, status
- **Streamlit dashboard**: Launch interactive web interface
- **Subcommands**: Multiple simulation and optimization types
- **Rich output**: Colored, formatted console output
- **Error handling**: Graceful failures with helpful messages

## Installation

The CLI is installed automatically with finbot:

```bash
uv sync
```

## Global Options

```bash
finbot --help
finbot --version
```

## Commands

### CLI Module

Main CLI entry point and command definitions:

::: finbot.cli.main
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Command Reference

### 1. simulate

Run financial simulations (funds, indexes, bond ladder, Monte Carlo).

#### Subcommands

##### simulate fund

Simulate a specific fund:

```bash
finbot simulate fund UPRO --start 2010-01-01 --end 2024-01-01
```

**Options:**
- `TICKER` (required): Fund ticker symbol (UPRO, TQQQ, TMF, etc.)
- `--start DATE`: Start date (YYYY-MM-DD, default: 10 years ago)
- `--end DATE`: End date (YYYY-MM-DD, default: today)
- `--output PATH`: Save results to file (parquet format)

**Available funds:**
SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, NTSX

##### simulate index

Simulate a stock or bond index:

```bash
finbot simulate index sp500 --start 2010-01-01
```

**Options:**
- `INDEX` (required): Index name (sp500, nasdaq100, treasury_20y, treasury_7y, treasury_1y)
- `--start DATE`: Start date
- `--end DATE`: End date
- `--output PATH`: Save results to file

**Available indexes:**
- **Stock**: sp500, nasdaq100
- **Bond**: treasury_20y, treasury_7y, treasury_1y

##### simulate bond-ladder

Simulate a bond ladder portfolio:

```bash
finbot simulate bond-ladder --investment 100000 --years 10 --start 2010-01-01
```

**Options:**
- `--investment FLOAT`: Initial investment amount (default: 100000)
- `--years INT`: Ladder duration in years (default: 10)
- `--start DATE`: Start date (default: 10 years ago)
- `--end DATE`: End date (default: today)
- `--output PATH`: Save results to file

##### simulate monte-carlo

Run Monte Carlo risk simulation:

```bash
finbot simulate monte-carlo --ticker SPY --trials 10000 --years 30
```

**Options:**
- `--ticker TEXT`: Asset ticker symbol (default: SPY)
- `--trials INT`: Number of simulation trials (default: 10000)
- `--years INT`: Projection horizon in years (default: 30)
- `--initial-investment FLOAT`: Starting amount (default: 100000)
- `--annual-contribution FLOAT`: Yearly contribution (default: 0)
- `--output PATH`: Save results to file

##### simulate all

Run all simulations (full pipeline):

```bash
finbot simulate all
```

Runs:
1. Overnight LIBOR approximation
2. All stock indexes (SP500, Nasdaq 100)
3. All bond indexes (1Y, 7Y, 20Y Treasuries)
4. All 15 fund simulations

**Use case:** Daily data update pipeline

### 2. backtest

Run strategy backtests.

```bash
finbot backtest --strategy Rebalance --tickers SPY TLT --start 2010-01-01
```

**Options:**
- `--strategy TEXT` (required): Strategy name
- `--tickers TEXT...` (required): Asset tickers (space-separated)
- `--start DATE`: Start date (default: 10 years ago)
- `--end DATE`: End date (default: today)
- `--cash FLOAT`: Starting cash (default: 100000)
- `--commission FLOAT`: Commission rate (default: 0.001)
- `--params JSON`: Strategy parameters as JSON (default: {})
- `--output PATH`: Save results to file

**Available strategies:**
Rebalance, NoRebalance, SMACrossover, SMACrossoverDouble, SMACrossoverTriple, MACDSingle, MACDDual, DipBuySMA, DipBuyStdev, SMARebalMix, DualMomentum, RiskParity

**Example with parameters:**
```bash
finbot backtest \
  --strategy SMACrossover \
  --tickers SPY \
  --params '{"fast_period": 50, "slow_period": 200}' \
  --start 2010-01-01 \
  --commission 0.001
```

### 3. optimize

Run portfolio optimizers.

#### Subcommands

##### optimize dca

Optimize dollar cost averaging allocations:

```bash
finbot optimize dca --tickers SPY TLT --start 2010-01-01
```

**Options:**
- `--tickers TEXT...` (required): Asset tickers
- `--start DATE`: Start date (default: 10 years ago)
- `--end DATE`: End date (default: today)
- `--investment FLOAT`: Monthly investment amount (default: 1000)
- `--output PATH`: Save results to file

**Grid search across:**
- Asset allocation ratios (50-95% equity in 5% steps)
- Investment durations (5-30 years)
- Purchase frequencies (monthly, quarterly)

**Metrics computed:**
- Sharpe ratio
- Sortino ratio
- Calmar ratio
- CAGR
- Max drawdown
- Standard deviation

##### optimize rebalance

Optimize portfolio rebalancing ratios:

```bash
finbot optimize rebalance --tickers SPY TLT --start 2010-01-01
```

**Options:**
- `--tickers TEXT...` (required): Asset tickers
- `--start DATE`: Start date
- `--end DATE`: End date
- `--output PATH`: Save results to file

**Optimizer:**
Gradient descent-like search for optimal allocation ratios maximizing Sharpe ratio.

### 4. update

Run the daily data update pipeline.

```bash
finbot update
```

**Pipeline:**
1. Fetch latest YFinance price data
2. Fetch latest FRED economic data (yields, rates, CPI, etc.)
3. Fetch latest Google Finance index data
4. Fetch latest Shiller datasets
5. Run overnight LIBOR approximation
6. Run all index simulations
7. Run all fund simulations

**Requirements:**
- API keys (FRED, Google Finance service account) in environment variables
- Internet connection
- ~5-10 minutes runtime (first run or stale data)
- ~30 seconds runtime (fresh data, incremental updates)

**Output:**
- Updated parquet files in `finbot/data/` subdirectories
- Log messages showing progress
- Success/failure status for each step

### 5. status

Check data freshness and health.

```bash
finbot status
```

**Checks:**
- YFinance data age
- FRED data age
- Google Finance data age
- Alpha Vantage data age
- BLS data age
- Shiller data age
- Simulation data age

**Output:**
```
Data Source Status
==================
YFinance: ✓ FRESH (0.2 days old, threshold: 1 day)
FRED: ✓ FRESH (0.5 days old, threshold: 7 days)
Google Finance: ⚠ STALE (8.3 days old, threshold: 7 days)
Simulations: ✓ FRESH (0.1 days old, threshold: 1 day)
...
```

**Status codes:**
- ✓ **FRESH**: Age < threshold (green)
- ⚠ **STALE**: Age ≥ threshold (yellow)
- ✗ **MISSING**: No data files found (red)

### 6. dashboard

Launch the Streamlit web dashboard.

```bash
finbot dashboard
```

**Dashboard features:**
- **6 pages**: Overview, Simulations, Backtesting, Optimizer, Monte Carlo, Data Status, Health Economics
- **Interactive charts**: Plotly visualizations
- **Parameter controls**: Sliders, dropdowns, date pickers
- **Real-time updates**: Rerun analyses with new parameters
- **Export results**: Download data as CSV

**Default:**
- Launches on http://localhost:8501
- Opens browser automatically
- Streamlit serves from `finbot/dashboard/app.py`

## Examples

### Daily Update Workflow

```bash
# Check current data status
finbot status

# Run update pipeline
finbot update

# Verify updates
finbot status
```

### Strategy Comparison Workflow

```bash
# Backtest multiple strategies
finbot backtest --strategy Rebalance --tickers SPY TLT --start 2010-01-01 --output rebalance.parquet
finbot backtest --strategy NoRebalance --tickers SPY TLT --start 2010-01-01 --output no_rebalance.parquet
finbot backtest --strategy DualMomentum --tickers SPY TLT --start 2010-01-01 --output dual_momentum.parquet

# Analyze results in Python
import pandas as pd

rebalance = pd.read_parquet('rebalance.parquet')
no_rebalance = pd.read_parquet('no_rebalance.parquet')
dual_momentum = pd.read_parquet('dual_momentum.parquet')

# Compare returns
print(f"Rebalance CAGR: {rebalance['cagr'][0]:.2%}")
print(f"No Rebalance CAGR: {no_rebalance['cagr'][0]:.2%}")
print(f"Dual Momentum CAGR: {dual_momentum['cagr'][0]:.2%}")
```

### Fund Simulation Workflow

```bash
# Simulate UPRO (3x S&P 500)
finbot simulate fund UPRO --start 2010-01-01 --end 2024-01-01 --output upro.parquet

# Simulate TQQQ (3x Nasdaq 100)
finbot simulate fund TQQQ --start 2010-01-01 --end 2024-01-01 --output tqqq.parquet

# Simulate TMF (3x 20Y Treasury)
finbot simulate fund TMF --start 2010-01-01 --end 2024-01-01 --output tmf.parquet

# Compare in Python
import pandas as pd

upro = pd.read_parquet('upro.parquet')
tqqq = pd.read_parquet('tqqq.parquet')
tmf = pd.read_parquet('tmf.parquet')

# Calculate total returns
upro_return = (upro['Close'][-1] / upro['Close'][0] - 1) * 100
tqqq_return = (tqqq['Close'][-1] / tqqq['Close'][0] - 1) * 100
tmf_return = (tmf['Close'][-1] / tmf['Close'][0] - 1) * 100

print(f"UPRO: {upro_return:.1f}%")
print(f"TQQQ: {tqqq_return:.1f}%")
print(f"TMF: {tmf_return:.1f}%")
```

### DCA Optimization Workflow

```bash
# Optimize SPY/TLT allocation
finbot optimize dca --tickers SPY TLT --start 2010-01-01 --investment 1000 --output dca_results.parquet

# Analyze results in Python
import pandas as pd

results = pd.read_parquet('dca_results.parquet')

# Find best Sharpe ratio
best = results.loc[results['sharpe'].idxmax()]
print(f"Best allocation: {best['spy_allocation']:.0%} SPY / {best['tlt_allocation']:.0%} TLT")
print(f"Sharpe ratio: {best['sharpe']:.2f}")
print(f"CAGR: {best['cagr']:.2%}")
print(f"Max drawdown: {best['max_drawdown']:.2%}")
```

## Error Handling

The CLI provides helpful error messages:

```bash
# Missing required argument
$ finbot backtest --strategy Rebalance
Error: Missing option '--tickers'

# Invalid strategy name
$ finbot backtest --strategy InvalidStrategy --tickers SPY
Error: Unknown strategy 'InvalidStrategy'
Available strategies: Rebalance, NoRebalance, SMACrossover, ...

# Invalid date format
$ finbot simulate fund UPRO --start 2010-13-01
Error: Invalid date format '2010-13-01'. Use YYYY-MM-DD

# Missing API key
$ finbot update
Error: FRED_API_KEY environment variable not set
Set it in .env file or export FRED_API_KEY=your_key
```

## Environment Variables

Required for data collection features:

```bash
export DYNACONF_ENV=development  # or production
export FRED_API_KEY=your_key
export NASDAQ_DATA_LINK_API_KEY=your_key
export US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

Create `.env` file in `finbot/config/` for persistent configuration.

## Performance

CLI commands are designed for interactive use:

| Command | Typical Runtime | Notes |
|---------|----------------|-------|
| status | <1 second | File system checks only |
| simulate fund | 1-2 seconds | Single fund simulation |
| simulate all | 2-5 minutes | All 15 funds + indexes |
| backtest | 2-5 seconds | Single strategy |
| optimize dca | 30-60 seconds | Grid search, parallel execution |
| update | 30 seconds - 10 minutes | Depends on data staleness |
| dashboard | 2-3 seconds | Streamlit startup |

## Testing

CLI has smoke tests:

```bash
# Test CLI imports and --help
uv run pytest tests/unit/test_imports.py::test_cli_import -v
```

## See Also

- [User Guide: Quick Start](../user-guide/quick-start.md) - CLI tutorial
- [Configuration](../user-guide/configuration.md) - Environment setup
- [Data Quality](services/data-quality.md) - Status monitoring
- [BacktestRunner](services/backtesting/backtest-runner.md) - Backtest API
- [DCA Optimizer](services/optimization/dca-optimizer.md) - Optimizer API
