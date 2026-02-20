# Finbot

**Financial data collection, simulation, and backtesting platform for quantitative analysis**

[![CI](https://github.com/jerdaw/finbot/actions/workflows/ci.yml/badge.svg)](https://github.com/jerdaw/finbot/actions/workflows/ci.yml)
[![Docs](https://github.com/jerdaw/finbot/actions/workflows/docs.yml/badge.svg)](https://github.com/jerdaw/finbot/actions/workflows/docs.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/jerdaw/finbot/badge)](https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot)
[![codecov](https://codecov.io/gh/jerdaw/finbot/branch/main/graph/badge.svg)](https://codecov.io/gh/jerdaw/finbot)
[![Docstring Coverage](https://img.shields.io/badge/docstring%20coverage-58.2%25-brightgreen.svg)](https://github.com/jerdaw/finbot)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-0.9+-blue.svg)](https://docs.astral.sh/uv/)

## Overview

Finbot is a comprehensive platform for quantitative financial analysis, combining:

- **Data Collection**: Automated pipelines for Yahoo Finance, FRED, Alpha Vantage, Google Sheets, Shiller datasets, and BLS
- **Simulation**: Realistic modeling of leveraged ETFs, bond ladders, indexes, and Monte Carlo scenarios
- **Backtesting**: Engine-agnostic backtesting with 12 strategies, typed contracts, and comprehensive performance metrics
- **Execution**: Paper trading simulator with realistic latency, risk controls, and state recovery for disaster resilience
- **Optimization**: Grid-search DCA optimizer and portfolio rebalancing tools
- **Analysis**: Walk-forward analysis, market regime detection, and research-grade documentation with statistical significance testing

### Why Finbot?

**Problem**: Testing investment strategies requires stitching together disparate tools, managing data inconsistencies, and writing repetitive boilerplate code.

**Solution**: Finbot provides a unified platform where you can:
- Fetch historical data from 6+ sources with a single function call
- Simulate leveraged funds back to 1950 with realistic cost modeling (fees, spreads, borrowing costs)
- Backtest any strategy with engine-agnostic contracts (swap Backtrader for NautilusTrader without code changes)
- Run paper trading with realistic latency, slippage, and execution delays
- Optimize portfolios across multiple dimensions (allocations, durations, intervals)
- Validate strategies with walk-forward analysis and regime detection
- Generate publication-ready research with example notebooks

**Use Cases**:
- Test rebalancing strategies (60/40, All-Weather, etc.) with realistic execution costs
- Evaluate leveraged ETF performance vs unleveraged alternatives
- Model bond ladder mechanics across different yield environments
- Optimize DCA timing and allocation ratios
- Generate Monte Carlo risk scenarios for retirement planning
- Paper trade with risk controls (position limits, drawdown protection, exposure limits)
- Analyze strategy performance across market regimes (bull, bear, sideways)

### Project History

This repository consolidates three years of development across three repositories (2021-2024). See [CHANGELOG.md](CHANGELOG.md) for detailed history and [ADR-001](docs/adr/ADR-001-consolidate-three-repos.md) for consolidation rationale.

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
- `make install` - Install dependencies with uv
- `make test` - Run all tests with verbose output
- `make check` - Run all code quality checks (lint, format, type, security)
- `make clean` - Remove cache files and build artifacts
- `make all` - Run full CI pipeline (check + test)

## Current Implementation Status (2026-02-19)

Engine-agnostic backtesting system with live-readiness execution simulator complete.

- **Epics E0-E5 Complete** (674 tests in latest local suite run; 672 passing, 2 skipped)
  - ✅ E0: Typed contracts for engine portability
  - ✅ E1: Backtrader adapter implementation
  - ✅ E2: A/B parity testing with CI gate
  - ✅ E3: Cost models, corporate actions, walk-forward analysis, regime detection
  - ✅ E4: Experiment tracking with reproducible snapshots
  - ✅ E5: Execution simulator with latency, risk controls, state checkpoints
- **E6 Status**: Pilot adapter hardening + native single-strategy execution path complete; final adoption decision deferred pending broader comparative evidence
- **CI Status**: Tiered CI is active for free-tier budget control (`ci.yml` for PR/main core gates, `ci-heavy.yml` for scheduled/manual heavy checks)
- **Priority 6 Follow-up**: GS-01/GS-02/GS-03 evidence published; ADR-011 refreshed (decision remains Defer)
- **Next Focus**: Priority 5 governance/security quick wins and CI/process polish

Key deliverables:
- Engine-agnostic contracts (`finbot/core/contracts/`)
- Execution simulator with risk management (`finbot/services/execution/`)
- Backtrader adapter (`finbot/adapters/backtrader/`)
- Walk-forward and regime detection tools
- State checkpoint/recovery system

Planning and handoff docs:
- `docs/planning/post-e5-handoff-2026-02-16.md`
- `docs/planning/backtesting-live-readiness-backlog.md`
- `docs/planning/roadmap.md` (Priority 6)

## Prerequisites

| Requirement | Minimum Version |
| --- | --- |
| **Python** | 3.12+ |
| **uv** | 0.6+ |

### Docker (Alternative)

Run finbot without installing Python or uv:

```bash
# Build image
make docker-build

# Check data freshness
make docker-status

# Run daily update pipeline
make docker-update

# Run any CLI command
make docker-run CMD="simulate --fund UPRO --start 2020-01-01"
```

Data is persisted in a Docker volume (`finbot-data`). API keys are loaded from `finbot/config/.env`.

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

### Paper Trading with Risk Controls

```python
from decimal import Decimal
from datetime import datetime
from finbot.core.contracts import LATENCY_NORMAL
from finbot.core.contracts.risk import RiskConfig, DrawdownLimitRule
from finbot.services.execution import ExecutionSimulator

# Create paper trading simulator with drawdown protection
risk_config = RiskConfig(
    drawdown_limit=DrawdownLimitRule(max_daily_drawdown_pct=Decimal("5"))
)
simulator = ExecutionSimulator(
    initial_cash=Decimal("100000"),
    slippage_bps=Decimal("5"),
    commission_per_share=Decimal("0.01"),
    latency_config=LATENCY_NORMAL,  # Realistic execution delays
    risk_config=risk_config,
    simulator_id="paper-001",
)

# Submit order (delayed by realistic latency)
simulator.submit_order(order, timestamp=datetime.now())

# Process market data (triggers fills)
simulator.process_market_data(current_time, current_prices)

# Save state for disaster recovery
from finbot.services.execution import CheckpointManager
manager = CheckpointManager("checkpoints")
checkpoint = manager.create_checkpoint(simulator)
manager.save_checkpoint(checkpoint)
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

### Direct uv Commands

```bash
uv run ruff check . --fix   # Lint
uv run ruff format .        # Format
uv run mypy                 # Type check
uv run pytest               # Test
```

Run `make help` to see all available commands.

## Architecture

### High-Level Data Flow

```mermaid
graph LR
    A[Data Sources] -->|YFinance, FRED, Alpha Vantage, etc.| B[Data Collection Utils]
    B -->|Price Histories, Economic Data| C[Data Storage]
    C -->|Parquet Files| D[Simulators]
    C -->|Parquet Files| E[Backtesting Engine]
    D -->|Simulated Histories| E
    E -->|Portfolio Performance| F[Optimization]
    E -->|Performance Metrics| G[Analysis & Visualization]
    F -->|Optimal Parameters| G

    style A fill:#e1f5ff
    style C fill:#fff4e1
    style G fill:#e8f5e9
```

### Architecture Diagram

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        CONFIG[config/<br/>Dynaconf Settings]
        CONST[constants/<br/>Paths & API URLs]
        LIBS[libs/<br/>API Manager & Logger]
    end

    subgraph "Contract Layer"
        CONTRACTS[core/contracts/<br/>Typed Contracts, Orders, Risk, Checkpoints]
        ADAPTERS[adapters/<br/>Backtrader, NautilusTrader]
    end

    subgraph "Utility Layer"
        DC[finbot/utils/data_collection/<br/>YFinance, FRED, Alpha Vantage, GF, BLS]
        FIN[finbot/utils/finance/<br/>CGR, Drawdown, Risk Metrics]
        PD[finbot/utils/pandas/<br/>Save/Load, Filter, Transform]
        DT[finbot/utils/datetime/<br/>Business Dates, Conversions]
    end

    subgraph "Service Layer"
        EXEC[finbot/services/execution/<br/>Paper Trading Simulator, Risk Controls, Checkpoints]
        SIM[finbot/services/simulation/<br/>Fund, Bond Ladder, Monte Carlo]
        BT[finbot/services/backtesting/<br/>12 Strategies, Cost Models, Corporate Actions, Regime Detection]
        OPT[finbot/services/optimization/<br/>DCA Optimizer, Rebalance Optimizer]
        EXP[finbot/services/experiment/<br/>Tracking, Snapshots, Batch Execution]
    end

    subgraph "Interface Layer"
        CLI[CLI Commands<br/>simulate, backtest, optimize, update]
        NB[Jupyter Notebooks<br/>5 Example Analyses]
        SCRIPTS[scripts/<br/>Daily Update Pipeline]
    end

    CONFIG --> DC
    CONFIG --> SIM
    CONST --> DC
    LIBS --> DC

    CONTRACTS --> ADAPTERS
    CONTRACTS --> EXEC
    CONTRACTS --> BT
    ADAPTERS --> BT

    DC --> SIM
    DC --> BT
    FIN --> BT
    FIN --> OPT
    PD --> SIM
    PD --> BT
    DT --> DC

    EXEC --> BT
    SIM --> BT
    SIM --> OPT
    BT --> OPT
    BT --> EXP

    CLI --> SIM
    CLI --> BT
    CLI --> OPT
    CLI --> DC
    CLI --> EXEC
    NB --> SIM
    NB --> BT
    NB --> OPT
    NB --> EXEC
    SCRIPTS --> DC
    SCRIPTS --> SIM

    style CONFIG fill:#e3f2fd
    style CONST fill:#e3f2fd
    style LIBS fill:#e3f2fd
    style CONTRACTS fill:#fce4ec
    style ADAPTERS fill:#fce4ec
    style DC fill:#fff3e0
    style EXEC fill:#e1f5fe
    style SIM fill:#e8f5e9
    style BT fill:#e8f5e9
    style OPT fill:#e8f5e9
    style EXP fill:#e8f5e9
    style CLI fill:#f3e5f5
    style NB fill:#f3e5f5
```

### Package Structure

| Layer | Purpose |
| --- | --- |
| `config/` | Dynaconf-based environment configuration, settings accessors |
| `constants/` | Application constants, path definitions, API URLs |
| `libs/` | API manager with rate limiting, queue-based async logger |
| `finbot/core/contracts/` | **NEW**: Engine-agnostic typed contracts (orders, risk, checkpoints, costs, regimes) |
| `finbot/adapters/` | **NEW**: Engine adapters (Backtrader, future NautilusTrader) |
| `finbot/services/execution/` | **NEW**: Paper trading simulator with latency, risk controls, state recovery |
| `finbot/services/experiment/` | **NEW**: Experiment tracking and snapshot management |
| `finbot/utils/` | 176-file utility library (data collection, finance, pandas, datetime, plotting, etc.) |
| `finbot/services/simulation/` | Fund, index, bond ladder, Monte Carlo simulators |
| `finbot/services/backtesting/` | Backtesting engine with 12 strategies, cost tracking, corporate actions, regime detection |
| `finbot/services/optimization/` | DCA and rebalance portfolio optimizers |
| `finbot/cli/` | Click-based CLI with 4 commands (simulate, backtest, optimize, update) |
| `scripts/` | Daily data update pipeline, baseline generation |
| `notebooks/` | 5 example Jupyter notebooks with analysis |
| `docs/` | Research papers, ADRs, planning documents |

See [docs/adr/](docs/adr/) for architectural decision records and [finbot/utils/README.md](finbot/utils/README.md) for utility library overview.

## Key Features

### Engine-Agnostic Backtesting

Write strategies once, run on any engine (Backtrader, NautilusTrader, or custom backends):

- **Typed Contracts**: Immutable dataclasses for portability (`BacktestRunRequest`, `BacktestRunResult`, `PortfolioSnapshot`)
- **Schema Versioning**: Forward-compatible contracts with migration support
- **Adapter Pattern**: Swap engines without changing strategy code
- **Parity Testing**: CI gates ensure equivalent results across engines

### Live-Ready Execution Simulator

Paper trading with production-grade features:

- **Realistic Latency**: Four latency profiles (INSTANT, FAST, NORMAL, SLOW) with configurable delays for order submission, fills, and cancellations
- **Risk Controls**: Position limits, exposure limits (gross/net), drawdown protection (daily/total), trading kill-switch
- **Order Lifecycle**: Full tracking of pending, accepted, filled, partial fills, rejected, and cancelled orders
- **State Checkpoints**: JSON-based disaster recovery with versioned snapshots for resuming after crashes

### Advanced Analysis Tools

Research-grade features for strategy development:

- **Cost Models**: Track slippage, commissions, spreads, and borrowing costs with detailed event logging
- **Corporate Actions**: Handle dividends, splits, and other corporate events in backtests
- **Walk-Forward Analysis**: Out-of-sample validation with rolling training/test windows
- **Regime Detection**: Identify market regimes (bull, bear, sideways) and analyze strategy performance by regime
- **Experiment Tracking**: Reproducible experiments with data snapshots, version control, and comparison tools

### Production-Ready Infrastructure

Built for reliability and scale:

- **Queue-Based Logging**: Non-blocking async logging with dual output (console + JSON files)
- **Parquet Storage**: Fast, safe serialization (replaced pickle throughout for security)
- **API Rate Limiting**: Built-in retry with exponential backoff for data collection
- **Data Quality**: Automated freshness monitoring with staleness thresholds
- **Docker Support**: Run without installing Python or dependencies

## Example Notebooks

Explore comprehensive analyses demonstrating all major features:

1. **[Fund Simulation Demo](notebooks/01_fund_simulation_demo.ipynb)** - Compare simulated vs actual ETF performance (SPY, UPRO, TQQQ)
2. **[DCA Optimization Results](notebooks/02_dca_optimization_results.ipynb)** - Find optimal portfolio allocations and timing
3. **[Backtest Strategy Comparison](notebooks/03_backtest_strategy_comparison.ipynb)** - Compare all 10 strategies with risk-return analysis
4. **[Monte Carlo Risk Analysis](notebooks/04_monte_carlo_risk_analysis.ipynb)** - Portfolio risk scenarios and VaR analysis
5. **[Bond Ladder Analysis](notebooks/05_bond_ladder_analysis.ipynb)** - Bond ladder construction and yield curve modeling

Each notebook includes:
- Setup and data loading
- Multiple analysis sections with interactive visualizations
- Key findings with actionable insights
- Statistical validation and next steps

## Research Documentation

Three comprehensive research papers (docs/research/):

- **[Leveraged ETF Simulation Accuracy](docs/research/leveraged-etf-simulation-accuracy.md)** - Tracking error analysis and methodology validation
- **[DCA Optimization Findings](docs/research/dca-optimization-findings.md)** - Optimal allocations across market regimes
- **[Strategy Backtest Results](docs/research/strategy-backtest-results.md)** - 10 strategies compared with statistical significance testing

## Limitations and Known Issues

**Important:** Finbot is a research and educational tool. All models make simplifying assumptions and past performance does not guarantee future results.

See **[docs/limitations.md](docs/limitations.md)** for comprehensive documentation of:
- Survivorship bias and its impact
- Simulation assumptions and trade-offs
- Data quality and coverage limitations
- Overfitting risks in strategy optimization
- Tax and cost considerations not modeled
- Known bugs and workarounds

**Key Takeaways:**
- Use results as inputs to decisions, not sole decision-maker
- Combine quantitative analysis with qualitative judgment
- Always consult qualified financial professionals
- This is not financial advice

## Ethics and Responsible Use

**IMPORTANT:** This software is for educational and research purposes only.

See **[DISCLAIMER.md](DISCLAIMER.md)** for concise financial/medical decision disclaimers and liability terms.

See **[docs/ethics/responsible-use.md](docs/ethics/responsible-use.md)** for comprehensive ethical guidelines covering:
- **Financial Advice Disclaimer:** Not a substitute for professional financial advisors
- **Data Privacy and Security:** Practices for protecting API keys and credentials
- **Backtesting Limitations:** Survivorship bias, overfitting, and regime dependency
- **Health Economics Caveats:** Not medical advice; methodological limitations
- **User Responsibilities:** Risk management, independent judgment, and ethical conduct
- **Liability Limitations:** No warranty; use at your own risk

**Key Principles:**
- Seek professional advice for financial and health decisions
- Understand all limitations before using results
- Exercise independent judgment and due diligence
- Use responsibly and ethically

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code quality standards
- Pull request process
- Issue templates

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use Finbot in academic research:

```bibtex
@software{finbot2024,
  author = {Dawson, Jeremy},
  title = {Finbot: Financial Data Collection, Simulation, and Backtesting Platform},
  year = {2024},
  url = {https://github.com/jerdaw/finbot},
  version = {1.0.0}
}
```
