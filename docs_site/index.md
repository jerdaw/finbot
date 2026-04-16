# Finbot Documentation

Welcome to the Finbot documentation. Finbot is a quantitative research
platform that combines financial analysis workflows with health-economics
tooling for transparent, evidence-oriented modeling.

!!! warning "Important Context"

    Finbot is an educational and research project. It is not financial advice,
    not medical advice, and not a substitute for formal clinical or policy
    review. If you are exploring the health-economics side of the project,
    start with the [Health Economics Evidence](research/health-economics-evidence.md)
    page and the repository
    [Disclaimer](https://github.com/jerdaw/finbot/blob/main/DISCLAIMER.md).

## Overview

Finbot brings together two applied domains that share the same quantitative
core:

- **Financial analysis**: data collection, simulation, backtesting, risk
    analysis, and optimization.
- **Health economics**: QALY simulation, cost-effectiveness analysis,
    treatment-schedule optimization, and illustrative clinical scenarios.

## Key Features

### 📊 Production-Ready Backtesting Engine
- **13 built-in strategies**: Rebalance, NoRebalance, SMA Crossovers, MACD, Dip Buying, Dual Momentum, Risk Parity, Regime Adaptive, and more
- **Performance metrics**: CAGR, Sharpe ratio, Sortino ratio, Calmar ratio, Max drawdown, Win rate, Kelly criterion
- **Engine-agnostic contracts**: Swap Backtrader for NautilusTrader without code changes
- **100% parity testing**: CI gate prevents regressions on golden strategies
- **Advanced features**: Cost models, corporate actions, walk-forward analysis, regime detection

### 🎯 Advanced Simulation Systems
- **Fund Simulator**: Simulate leveraged ETFs with fees, borrowing costs, and tracking error
- **Bond Ladder Simulator**: Model bond portfolios with yield curves and maturity rolling
- **Monte Carlo Simulator**: Portfolio risk analysis with probability distributions and VaR
- **Specific fund implementations**: SPY, SSO, UPRO, QQQ, TQQQ, TLT, TMF, and more

### 🔧 Portfolio Optimization
- **DCA Optimizer**: Grid search across asset ratios, durations, and purchase intervals
- **Rebalance Optimizer**: Gradient descent for optimal portfolio rebalancing
- **Multi-metric optimization**: CAGR, Sharpe, Sortino, Max drawdown

### 🏥 Health Economics Analysis
- **QALY Simulator**: Monte Carlo simulation with stochastic cost/utility/mortality
- **Cost-Effectiveness Analysis**: ICER, NMB, CEAC with probabilistic sensitivity analysis
- **Treatment Optimizer**: Grid-search optimization for dose frequency and duration
- **Clinical scenarios**: Type 2 diabetes, cancer screening with NICE/CADTH/WHO thresholds
- **Publication-grade research**: 3 research documents with 22+ academic citations

### 🔎 Reviewer-Oriented Entry Points
- **Health Economics Evidence**: Public context page explaining scope, intended use, and limitations
- **Health Economics Methodology**: Public summary of model structure, equations, and standards alignment
- **Project Tour**: Guided reading path for quickly understanding the main public surfaces
- **Responsible use**: Repository disclaimer and ethics guidance for interpreting outputs conservatively

### 📈 Data Collection Infrastructure
- **Multiple data sources**: Yahoo Finance, FRED, Alpha Vantage, Google Finance, BLS, MSCI
- **Automatic caching**: Zstandard-compressed parquet files for performance
- **Daily update pipeline**: Automated data refresh with retry logic and error handling

### 🛠️ Production-Ready Infrastructure
- **CLI interface**: `finbot simulate`, `finbot backtest`, `finbot optimize`, `finbot update`, `finbot dashboard`
- **Web Dashboard**: Interactive Streamlit app with 12 task-focused pages plus the home page
- **Comprehensive CI/CD**: Python 3.11/3.12/3.13 validation plus separate CLI/API Docker security scanning
- **Queue-based logging**: Non-blocking async logging with JSON output and audit trails
- **Security scanning**: bandit, pip-audit, trivy container scanning, OpenSSF Scorecard
- **Test coverage**: Comprehensive unit, integration, property, and validation coverage
- **Dynaconf configuration**: Environment-aware YAML config (development, production)
- **Comprehensive utilities**: 160+ utility functions across 15 categories

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install the full contributor environment
uv sync --all-extras

# Minimal runtime only
# uv sync

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
- uv for dependency management
- Optional: API keys for data sources (Alpha Vantage, NASDAQ Data Link, BLS, Google Finance)

## License

MIT License - see [LICENSE](https://github.com/jerdaw/finbot/blob/main/LICENSE) for details.
