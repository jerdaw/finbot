# Finbot Documentation

Welcome to the Finbot documentation! Finbot is a comprehensive financial data collection, simulation, and backtesting platform designed for quantitative analysis and portfolio optimization.

## Overview

Finbot consolidates three key areas of quantitative finance:

- **Data Collection**: Automated fetching from Yahoo Finance, FRED, Alpha Vantage, Google Finance, and more
- **Simulation**: Fund simulators (leveraged ETFs), bond ladders, Monte Carlo risk analysis
- **Backtesting**: 10 trading strategies with comprehensive performance metrics using Backtrader

## Key Features

### 📊 Comprehensive Backtesting Engine
- **10 built-in strategies**: Rebalance, NoRebalance, SMA Crossovers, MACD, Dip Buying, Hybrid strategies
- **Performance metrics**: CAGR, Sharpe ratio, Sortino ratio, Max drawdown, Win rate, Kelly criterion
- **Powered by Backtrader**: Industry-standard backtesting framework with custom analyzers

### 🎯 Advanced Simulation Systems
- **Fund Simulator**: Simulate leveraged ETFs with fees, borrowing costs, and tracking error
- **Bond Ladder Simulator**: Model bond portfolios with yield curves and maturity rolling
- **Monte Carlo Simulator**: Portfolio risk analysis with probability distributions and VaR
- **Specific fund implementations**: SPY, SSO, UPRO, QQQ, TQQQ, TLT, TMF, and more

### 🔧 Portfolio Optimization
- **DCA Optimizer**: Grid search across asset ratios, durations, and purchase intervals
- **Rebalance Optimizer**: Gradient descent for optimal portfolio rebalancing
- **Multi-metric optimization**: CAGR, Sharpe, Sortino, Max drawdown

### 📈 Data Collection Infrastructure
- **Multiple data sources**: Yahoo Finance, FRED, Alpha Vantage, Google Finance, BLS, MSCI
- **Automatic caching**: Zstandard-compressed parquet files for performance
- **Daily update pipeline**: Automated data refresh with retry logic and error handling

### 🛠️ Modern Infrastructure
- **CLI interface**: `finbot simulate`, `finbot backtest`, `finbot optimize`, `finbot update`
- **Dynaconf configuration**: Environment-aware YAML config (development, production)
- **Queue-based logging**: Non-blocking async logging with JSON output
- **Comprehensive utilities**: 160+ utility functions across 15 categories

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install with Poetry
uv sync

# Set environment
export DYNACONF_ENV=development

# Run tests
uv run pytest
```

### Basic Usage

```bash
# Simulate a leveraged fund
finbot simulate --fund UPRO --start 2010-01-01 --plot

# Backtest a strategy
finbot backtest --strategy Rebalance --asset SPY,TLT --plot

# Optimize DCA portfolio
finbot optimize --method dca --assets SPY,TQQQ --plot

# Update all data
finbot update
```

### Python API

```python
from finbot.services.simulation import fund_simulator
from finbot.services.backtesting import BacktestRunner
from finbot.services.optimization import dca_optimizer

# Simulate UPRO fund
upro_sim = fund_simulator.simulate_fund('UPRO', start_date='2010-01-01')

# Run backtest
runner = BacktestRunner(
    strategy='Rebalance',
    data_feeds={'SPY': spy_data, 'TLT': tlt_data},
    strategy_params={'rebalance_days': 30}
)
results = runner.run()

# Optimize DCA strategy
optimal_results = dca_optimizer(
    price_history=combined_df,
    ratio_linspace=(0.5, 0.95, 10),
    dca_duration_days=365 * 5,
    trial_duration_days=365 * 10
)
```

## Documentation Structure

- **[User Guide](user-guide/getting-started.md)**: Installation, configuration, and usage tutorials
- **[API Reference](api/index.md)**: Detailed API documentation for all modules
- **[Research](research/index.md)**: Published research findings and analysis
- **[Contributing](contributing.md)**: Guidelines for contributors

## Project Links

- **GitHub Repository**: [github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)
- **Issue Tracker**: [GitHub Issues](https://github.com/jerdaw/finbot/issues)
- **Changelog**: [CHANGELOG.md](changelog.md)

## Requirements

- Python >=3.11, <3.15
- Poetry for dependency management
- Optional: API keys for data sources (Alpha Vantage, NASDAQ Data Link, BLS, Google Finance)

## License

MIT License - see [LICENSE](https://github.com/jerdaw/finbot/blob/main/LICENSE) for details.
