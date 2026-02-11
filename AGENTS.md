# AGENTS.md

## Repository Overview

Finbot is a financial data collection, simulation, and backtesting platform that consolidates:
- Modern infrastructure (Dynaconf config, queue-based logging, API management)
- Comprehensive backtesting engine (Backtrader-based with 10 strategies)
- Advanced simulation systems (fund, bond ladder, Monte Carlo, index simulators)
- Portfolio optimization (DCA optimizer, rebalance optimizer)

Python `>=3.11,<3.15`. Uses **Poetry** for dependency management.

## Quick Start

```bash
# Install
poetry install

# Set environment
export DYNACONF_ENV=development

# Run tests
poetry run pytest

# Run daily data pipeline
poetry run python scripts/update_daily.py
```

## Common Commands

```bash
# Code quality
poetry run ruff check . --fix    # lint + autofix
poetry run ruff format .         # format
poetry run mypy                  # type check (configured in pyproject.toml)
poetry run bandit -r finbot libs # security scan

# Pre-commit hooks (lightweight set)
poetry run pre-commit run --all-files

# Testing
poetry run pytest tests/ -v                    # all tests with verbose output
poetry run pytest tests/unit/ -v              # unit tests only
poetry run pytest -k test_import              # tests matching pattern
```

## Architecture

**Data Flow:** Data Collection (utils) → Simulations (services) → Backtesting (services) → Performance Analysis

### Global Access Pattern

```python
from config import settings, logger, settings_accessors  # Dynaconf settings + logger + settings accessors
from libs.api_manager import api_manager                  # Singleton API registry
```

### Package Structure

#### `config/` — Configuration Layer
- **Dynaconf-based** environment-aware YAML files (`development.yaml`, `production.yaml`)
- **APIKeyManager**: Lazy-loaded API keys from env vars (no import failures when keys missing)
- Set `DYNACONF_ENV=development|production` to switch environments

#### `constants/` — Application Constants
- `path_constants.py`: All data directory paths (auto-creates missing dirs)
- `api_constants.py`: API URLs and endpoints
- `datetime_constants.py`, `networking_constants.py`, etc.
- `tracked_collections/`: CSV manifests of tracked funds, FRED symbols, MSCI indexes

#### `libs/` — Core Infrastructure
- **`api_manager/`**: Central API registry with `APIResourceGroup` for rate limits/retry
  - Supports FRED, Alpha Vantage, NASDAQ Data Link, Google Finance, BLS APIs
- **`logger/`**: Queue-based async logging
  - Dual output: colored console (stdout for INFO+, stderr for ERROR+) + JSON file
  - Rotating file handlers (5MB, 3 backups)

#### `finbot/` — Main Package

##### `finbot/services/backtesting/` — Backtrader-Based Backtesting Engine
Entry point: `BacktestRunner` in `backtest_runner.py`

**Key modules:**
- **`backtest_runner.py`**: Main orchestrator, wraps Backtrader's Cerebro engine
- **`run_backtest.py`**: Single backtest execution
- **`backtest_batch.py`**: Parallel batch backtesting
- **`compute_stats.py`**: Performance metrics using quantstats (Sharpe, Sortino, Calmar, max drawdown, Kelly criterion)
- **`rebalance_optimizer.py`**: Gradient descent-like optimizer for portfolio rebalance ratios

**Strategies** (in `strategies/`):
- `rebalance.py`: Periodic portfolio rebalancing
- `no_rebalance.py`: Buy and hold
- `sma_crossover.py`, `sma_crossover_double.py`, `sma_crossover_triple.py`: SMA timing strategies
- `macd_single.py`, `macd_dual.py`: MACD-based strategies
- `dip_buy_sma.py`, `dip_buy_stdev.py`: Dip buying strategies
- `sma_rebal_mix.py`: Mixed SMA + rebalance approach

**Supporting components:**
- `analyzers/cv_tracker.py`: Tracks cash and value throughout backtest
- `brokers/`: Commission schemes (fixed commission)
- `indicators/`: Returns, positive returns, negative returns
- `sizers/`: Position sizing (AllInSizer, etc.)

##### `finbot/services/simulation/` — Simulators (No Numba, Vectorized Numpy)

**Fund simulator** (`fund_simulator.py`):
- Simulates leveraged funds with fees, spread costs, LIBOR borrowing
- **Equation**: `(underlying_change * leverage - daily_expenses) * mult_constant + add_constant`
- Uses **vectorized numpy** (replaced numba @jit for performance + Python 3.12+ compatibility)

**Bond ladder simulator** (`bond_ladder/`):
- 6 files: `bond.py`, `ladder.py`, `bond_ladder_simulator.py`, `build_yield_curve.py`, `loop.py`, `get_yield_history.py`
- Uses `numpy_financial.pv()` for present value calculations (replaced custom numba PV function)
- Plain Python classes (removed `@jitclass` decorators)

**Index simulators**:
- `stock_index_simulator.py`, `bond_index_simulator.py`: Generic index simulation
- `sim_specific_stock_indexes.py`: S&P 500 TR, Nasdaq 100 TR
- `sim_specific_bond_indexes.py`: ICE US Treasury indexes (1Y, 7Y, 20Y)

**Fund-specific simulators** (`sim_specific_funds.py`):
- 16 fund simulation functions (SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, 2x/3x short-term treasuries, NTSX)
- Generic `_sim_fund()` helper reduces code duplication

**Monte Carlo** (`monte_carlo/`):
- `monte_carlo_simulator.py`: Main simulator
- `sim_types.py`: Normal distribution simulation
- `visualization.py`: Plot trials and histograms

##### `finbot/services/optimization/` — Portfolio Optimizers
- **`dca_optimizer.py`**: DCA (Dollar Cost Averaging) optimizer
  - Grid search across ratios, durations, purchase intervals using multiprocessing
  - Calculates CAGR, Sharpe, max drawdown, std dev for each combination
- **`rebalance_optimizer.py`**: Placeholder (see `backtesting/rebalance_optimizer.py` for working version)

##### `finbot/utils/` — Utility Library (~176 files)

**Data collection** (`data_collection_utils/`):
- `yfinance/`: Yahoo Finance price histories
- `fred/`: FRED economic data (yields, rates, CPI, GDP, unemployment)
- `google_finance/`: Google Sheets-based index data (XNDX, ICE treasury indexes)
- `scrapers/shiller/`: Shiller's online datasets (CAPE, PE ratios, S&P data)
- `alpha_vantage/`: Alpha Vantage API (quotes, sentiment, economic indicators)
- `bls/`: Bureau of Labor Statistics data
- `pdr/`: Pandas DataReader wrapper utilities

**Finance utilities** (`finance_utils/`):
- `get_cgr.py`: Compound growth rate
- `get_pct_change.py`: Percentage change
- `get_periods_per_year.py`: Detect frequency from price data
- `merge_price_histories.py`: Merge overlapping price series
- `get_risk_free_rate.py`: Fetch risk-free rate
- `get_drawdown.py`, `get_timeseries_stats.py`, etc.

**Pandas utilities** (`pandas_utils/`):
- Save/load DataFrames (parquet, CSV, Excel)
- Date filtering, frequency detection, hashing
- Column sorting, data masking

**Other utilities**:
- `datetime_utils/`: Date conversions, US business dates, time ranges
- `data_science_utils/`: Data cleaning, imputation, outlier detection, scalers/normalizers
- `plotting_utils/`: Interactive plotly visualizations
- `request_utils/`: HTTP request handler with retry logic, exponential backoff, response caching (zstandard compression)
- `multithreading_utils/`: Thread pool configuration

#### `scripts/` — Automation Scripts
- **`update_daily.py`**: Daily data update pipeline
  - Fetches YF/GF price histories, FRED data, Shiller data
  - Re-runs all simulations (overnight LIBOR approximation → index sims → fund sims)
  - Uses `_run_with_retry()` helper with logging

### Data Storage

All data stored as **parquet** files (replaced pickle throughout for safety, speed, interoperability).

Directories under `finbot/data/` (configured in `constants/path_constants.py`):
- `simulations/`: Fund and index simulation results
- `backtests/`: Backtest results
- `price_histories/`: Cached price data (YF, GF)
- `longtermtrends_data/`: Long-term trends datasets
- `fred_data/`: FRED economic data
- `yfinance_data/`: YFinance data cache
- `google_finance_data/`: Google Finance data cache
- `shiller_data/`: Shiller datasets
- `alpha_vantage_data/`: Alpha Vantage data cache
- `bls_data/`: BLS data cache
- `responses/`: HTTP response cache (by source)

## Environment Variables

Required for data collection features (loaded lazily via `APIKeyManager`):

```bash
export DYNACONF_ENV=development  # or production
export ALPHA_VANTAGE_API_KEY=your_key
export NASDAQ_DATA_LINK_API_KEY=your_key
export US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

Create `.env` file in `config/` (excluded by `.gitignore`).

## Key Entry Points

| File | Purpose |
| --- | --- |
| `finbot/services/backtesting/run_backtest.py` | Run single backtest |
| `finbot/services/backtesting/backtest_batch.py` | Run backtests in parallel |
| `finbot/services/backtesting/backtest_runner.py` | BacktestRunner class (Cerebro wrapper) |
| `finbot/services/simulation/fund_simulator.py` | Simulate leveraged funds with fees |
| `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py` | Simulate bond ladders |
| `finbot/services/simulation/monte_carlo/monte_carlo_simulator.py` | Monte Carlo simulations |
| `finbot/services/optimization/dca_optimizer.py` | DCA grid search optimizer |
| `scripts/update_daily.py` | Daily data update + simulation pipeline |

## Code Style

- **Linter**: ruff (line-length 120, Python 3.11 target)
- **Formatter**: ruff format
- **Type checker**: mypy (config in `pyproject.toml`)
- **Security**: bandit
- **Lint rules**: E, F, UP, B, SIM, I (import sorting)
- **Pre-commit hooks**: Basic checks only (trailing whitespace, YAML, AST, private keys, ruff)

## Testing

```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/unit/test_imports.py -v

# Run tests matching pattern
poetry run pytest -k test_simulation

# Run with coverage
poetry run pytest --cov=finbot tests/
```

**Test structure**:
- `tests/unit/`: Unit tests (18 tests currently)
  - `test_imports.py`: Smoke tests for all key module imports
  - `test_simulation_math.py`: Unit tests for simulation math correctness
- `tests/integration/`: Integration tests (future)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to main:
- Lint: `ruff check .`
- Format check: `ruff format --check .`
- Tests: `pytest tests/ -v`
- Matrix: Python 3.11, 3.12, 3.13

## Architecture Decisions

See `docs/adr/` for architectural decision records:
- **ADR-001**: Consolidate three repos (finbot, bb, backbetter) into one
  - Drop numba → vectorized numpy + numpy-financial
  - Drop Scrapy → bb's Selenium
  - Keep quantstats
  - Replace pickle → parquet
  - Lazy API key loading

## Key Design Patterns

| Pattern | Implementation | Rationale |
| --- | --- | --- |
| **Settings Accessors** | `settings_accessors` module in `config/` | Lazy accessors for MAX_THREADS and API keys (alpha_vantage, nasdaq_data_link, bls, google_finance) |
| **Lazy API keys** | `APIKeyManager.get_key()` only loads on first access | Prevents import failures when keys not needed |
| **Queue-based logging** | `libs/logger/setup_queue_logging.py` | Non-blocking async logging for performance |
| **Vectorized simulation** | Numpy broadcasting in `fund_simulator.py` | Faster than numba loop, no JIT compilation required |
| **Parquet everywhere** | All serialization uses `to_parquet()`/`read_parquet()` | Safer, faster, smaller than pickle |
| **Auto-create dirs** | `path_constants._process_dir()` uses `mkdir(exist_ok=True)` | Works in CI, fresh clones, no manual setup |

## Performance Notes

- **Fund simulator**: Vectorized numpy is faster than the original numba @jit loop
- **Bond ladder**: Plain Python + numpy-financial is adequate (~16K trading days in seconds)
- **No numba dependency**: Better Python 3.12+ compatibility, no C compiler required

## Common Gotchas

1. **Missing API keys**: Functions using `settings_accessors.get_alpha_vantage_api_key()` will raise `OSError` on access if env var not set. Set up `.env` file or export env vars before running data collection.

2. **DYNACONF_ENV not set**: Defaults to "development" but logs a warning. Always set explicitly.

3. **Empty data directories**: First run of simulators/backtests will populate `finbot/data/` subdirectories. This is normal.

4. **Backtrader SyntaxWarnings**: Backtrader library has invalid escape sequences. This is a known upstream issue and can be ignored.

5. **pandas_datareader DeprecationWarnings**: Uses deprecated `distutils.LooseVersion`. This is a known upstream issue and can be ignored.

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `poetry run pytest`
4. Run linter: `poetry run ruff check . --fix`
5. Run formatter: `poetry run ruff format .`
6. Commit with descriptive message following commit authorship policy (see below)
7. Push and create PR
8. CI must pass (all 3 Python versions)

### Commit Authorship Policy

**IMPORTANT:** All commits must list only human authors, co-authors, and contributors.

- ✅ **Do:** Attribute commits to human developers
- ❌ **Don't:** Include AI assistants (Claude, ChatGPT, etc.) in author, co-author, or contributor fields
- **Rationale:** Commits represent human accountability and decision-making

**Examples:**

Good commit message:
```
Add performance benchmarks

- Created benchmark_fund_simulator.py with 10 data sizes
- Created comprehensive docs/benchmarks.md
- Validates vectorized numpy performance claims
```

Bad commit message (don't do this):
```
Add performance benchmarks

[changes...]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

This policy applies to:
- All past commits (if needed, amend history to comply)
- All current commits
- All future commits

## See Also

- `README.md`: User-facing quick start and usage guide
- `docs/adr/`: Architectural decision records
- `docs/planning/archive/`: Archived implementation plans
- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `pyproject.toml`: Poetry dependencies, tool configuration
