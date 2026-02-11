# API Reference Overview

This section provides comprehensive API documentation for Finbot's modules, automatically generated from inline docstrings.

## Package Structure

Finbot is organized into three main areas:

### Services (`finbot/services/`)

High-level analysis and simulation services:

- **Backtesting** (`backtesting/`): Strategy backtesting engine powered by Backtrader
  - `BacktestRunner`: Main orchestrator for running backtests
  - `run_backtest`, `backtest_batch`: Single and parallel backtest execution
  - `compute_stats`: Performance metrics calculation
  - `strategies/`: 10 trading strategies
  - `rebalance_optimizer`: Portfolio rebalancing optimization

- **Simulation** (`simulation/`): Financial instrument simulators
  - `fund_simulator`: Simulate leveraged ETFs with fees and borrowing costs
  - `bond_ladder/`: Bond ladder construction and simulation
  - `monte_carlo/`: Monte Carlo risk analysis
  - `sim_specific_funds`: Pre-configured fund simulations (SPY, UPRO, TQQQ, etc.)
  - `sim_specific_*_indexes`: Stock and bond index simulations

- **Optimization** (`optimization/`): Portfolio optimization tools
  - `dca_optimizer`: Dollar-cost averaging strategy optimizer
  - `rebalance_optimizer`: Rebalance ratio optimizer (convenience import)

### Utilities (`finbot/utils/`)

160+ utility functions across 15 categories:

| Category | Count | Purpose |
|----------|-------|---------|
| **finance_utils** | 19 | CGR, drawdown, periods, risk-free rate, price trends |
| **datetime_utils** | 23 | Business dates, duration, conversions, time ranges |
| **pandas_utils** | 17 | Save/load parquet, filtering, frequency detection |
| **data_collection_utils** | 40 | Yahoo Finance, FRED, Alpha Vantage, BLS, Google Finance |
| **data_science_utils** | 37 | Missing data, outliers, scaling, imputation |
| **file_utils** | 10 | Text I/O with compression, staleness checking |
| **json_utils** | 4 | JSON serialization with zstandard compression |
| **request_utils** | 2 | HTTP client with retry logic and caching |
| **plotting_utils** | 1 | Interactive plotly visualizations |
| **multithreading_utils** | 1 | Optimal thread count calculation |
| **validation_utils** | 1 | Parameter validation helpers |
| **vectorization_utils** | 1 | Vectorization profiling |
| **class_utils** | 1 | Singleton metaclasses |
| **dict_utils** | 1 | Deterministic dictionary hashing |
| **function_utils** | 1 | Logging decorators |

### Infrastructure

- **config/**: Dynaconf-based configuration with lazy API key loading
- **constants/**: Application constants (paths, APIs, datetime, networking)
- **libs/**: Core libraries (API manager, queue-based logger)

## Navigation

Use the left sidebar to navigate to specific modules. Each page provides:

- Module overview and purpose
- Typical usage examples
- Full API documentation with signatures
- Parameter descriptions
- Return types
- Raises information
- Related modules

## Key Entry Points

| Module | Purpose | Documentation |
|--------|---------|---------------|
| `fund_simulator` | Simulate leveraged funds | [Fund Simulator API](services/simulation/fund-simulator.md) |
| `BacktestRunner` | Run strategy backtests | [BacktestRunner API](services/backtesting/backtest-runner.md) |
| `dca_optimizer` | Optimize DCA strategies | [DCA Optimizer API](services/optimization/dca-optimizer.md) |
| `monte_carlo_simulator` | Portfolio risk analysis | [Monte Carlo API](services/simulation/monte-carlo.md) |
| `finbot.cli` | Command-line interface | [CLI Reference](../user-guide/cli-reference.md) |

## Type Hints

All services and utilities include type hints for parameters and return values. Type checking is performed using `mypy` with strict optional checking.

## Docstring Format

All modules use Google-style docstrings with the following sections:

- Module-level docstring with purpose, usage examples, and features
- Function/method docstrings with Args, Returns, Raises
- Class docstrings with attributes and methods

## Source Code

All API documentation pages include links to the source code on GitHub for reference.
