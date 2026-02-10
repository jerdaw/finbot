# AGENTS.md

## Repository Overview

Finbot is a financial data collection, simulation, and backtesting platform. It consolidates modern infrastructure (Dynaconf config, queue-based logging, API management, extensive utilities) with a full backtesting and simulation engine.

Python `>=3.11,<3.15`. Uses **Poetry** for dependency management.

## Common Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Code quality
poetry run ruff check . --fix    # lint + autofix
poetry run ruff format .         # format
poetry run mypy                  # type check
poetry run bandit -r finbot libs # security scan

# Pre-commit hooks
poetry run pre-commit run --all-files

# Daily data update pipeline
DYNACONF_ENV=development poetry run python scripts/update_daily.py
```

## Architecture

**Data pipeline:** Data Collection (utils) -> Simulations (services) -> Backtesting (services) -> Performance Analysis

### Global access pattern
```python
from config import settings, logger, Config  # Dynaconf settings + logger + Config singleton
from libs.api_manager import api_manager     # Singleton API registry
```

### Package structure

- **`config/`** — Dynaconf-based configuration with environment-aware YAML files. API keys managed via `APIKeyManager` (lazy-loaded from env vars). Set `DYNACONF_ENV=development|production`.
- **`constants/`** — Application-wide constants (API URLs, paths, datetime formats, networking). `path_constants.py` defines all data directories.
- **`libs/`** — `api_manager` (central API registry with rate limits) + `logger` (queue-based async logging with colored console + JSON file output).
- **`finbot/`** — Main package:
  - **`services/backtesting/`** — Backtrader-based backtesting engine. Entry point: `BacktestRunner` in `backtest_runner.py`. Includes strategies (rebalance, SMA crossover, MACD, dip-buy), analyzers, brokers, indicators, sizers. `compute_stats.py` uses quantstats for performance metrics.
  - **`services/simulation/`** — Leveraged fund simulation (vectorized numpy, no numba), bond ladder simulation (numpy-financial for PV), stock/bond index simulation, Monte Carlo simulation. Fund sim equation: `(underlying_change * leverage - daily_expenses) * mult + additive`.
  - **`services/optimization/`** — DCA optimizer (multiprocessing grid search) and rebalance optimizer (placeholder).
  - **`utils/`** — Extensive utility library (~174 files) including `data_collection_utils/` (Yahoo Finance, FRED, Google Finance, Shiller, Alpha Vantage, BLS), `finance_utils/`, `pandas_utils/`, `datetime_utils/`, `data_science_utils/`, etc.
- **`scripts/`** — `update_daily.py` runs the full data update + simulation pipeline.

### Data storage
- All data stored as **parquet** files in directories under `finbot/data/` (configured in `constants/path_constants.py`):
  - `simulations/` — Fund and index simulation results
  - `backtests/` — Backtest results
  - `price_histories/` — Cached price data
  - `longtermtrends_data/` — Long-term trends datasets

### Key entry points
- `finbot/services/backtesting/run_backtest.py` — Run a single backtest
- `finbot/services/backtesting/backtest_batch.py` — Run backtests in parallel
- `finbot/services/simulation/fund_simulator.py` — Simulate leveraged funds with fees
- `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py` — Simulate bond ladders
- `scripts/update_daily.py` — Daily data pipeline

## Environment Variables

Required for data collection features:
- `DYNACONF_ENV` — `development` or `production`
- `ALPHA_VANTAGE_API_KEY`
- `NASDAQ_DATA_LINK_API_KEY`
- `US_BUREAU_OF_LABOR_STATISTICS_API_KEY`
- `GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH`

## Code Style

- ruff for linting + formatting (line-length 120, Python 3.11 target)
- Lint rules: E, F, UP, B, SIM, I
- mypy for type checking
- bandit for security scanning
