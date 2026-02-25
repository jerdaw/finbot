# AGENTS.md

## Repository Overview

Finbot is a financial data collection, simulation, and backtesting platform that consolidates:
- Modern infrastructure (Dynaconf config, queue-based logging, API management)
- **Engine-agnostic execution system** with orders, latency simulation, risk controls, and state checkpoints
- Comprehensive backtesting engine (Backtrader-based with 13 strategies)
- **Typed contracts** for portable backtests with versioning, serialization, and migration
- Advanced simulation systems (fund, bond ladder, Monte Carlo, multi-asset Monte Carlo, index simulators)
- Portfolio optimization (DCA optimizer, rebalance optimizer, Pareto optimizer)
- **Cost models** and **corporate actions** handling for realistic backtests
- **Walk-forward analysis** and **market regime detection** for robust strategy evaluation
- **Experiment tracking** with snapshots, batch observability, and dashboard comparison
- **Real-time market data** from Alpaca, Twelve Data, and yfinance with composite fallback
- **Standalone analytics**: risk (VaR/CVaR, stress testing, Kelly), portfolio (rolling, benchmark, drawdown, diversification), factor (Fama-French regression, attribution, risk decomposition)
- Health economics analysis (QALY simulation, cost-effectiveness, treatment optimization)
- Interactive Streamlit web dashboard

Python `>=3.11,<3.15`. Uses **uv** for dependency management.

## Quick Start

```bash
# Install
uv sync

# Set environment
export DYNACONF_ENV=development

# Run tests
uv run pytest

# Run daily data pipeline
uv run python scripts/update_daily.py
```

## Current Delivery Status (2026-02-25)

**P0-P8 complete. 1749 tests. P9 active.**

- **P5** (97.8%): OMSAS/CanMEDS improvements — 44/45 items (item 42 blocked on external resources)
- **P6** (100%): Backtesting-to-live readiness — Epics E0-E6 complete; ADR-011 confirmed **Defer**
- **P7** (93%): External impact & advanced capabilities — 25/27 active items
- **P8** (100%): Risk Analytics, Portfolio Analytics, Real-Time Data, Factor Analytics
- **P9** (active): Agent tooling optimizations

**Tracking docs:** `docs/planning/roadmap.md`, `docs/planning/backtesting-live-readiness-backlog.md`, `docs/planning/priority-5-6-completion-status.md`, `docs/adr/ADR-011-nautilus-decision.md`

## Common Commands

```bash
# Code quality
uv run ruff check . --fix    # lint + autofix
uv run ruff format .         # format
uv run mypy                  # type check (configured in pyproject.toml)
uv run bandit -r finbot      # security scan

# Pre-commit hooks (lightweight set)
uv run pre-commit run --all-files

# Testing
uv run pytest tests/ -v                    # all tests with verbose output
uv run pytest tests/unit/ -v              # unit tests only
uv run pytest -k test_import              # tests matching pattern

# Docker
make docker-build                # build image
make docker-run CMD="status"     # run any CLI command
make docker-update               # run daily update pipeline
make docker-test                 # run tests in container
```

## Architecture

**Data Flow:** Data Collection (utils) → Simulations (services) → Backtesting (services) → Performance Analysis

### Backtesting Engines

Finbot supports two backtesting engines through a unified adapter interface:
- **Backtrader** (default): Mature, bar-based, great for pure backtesting
- **NautilusTrader**: Event-driven, realistic fills, built for live trading

**Choosing an engine:** See [docs/guides/choosing-backtest-engine.md](docs/guides/choosing-backtest-engine.md)

**Hybrid approach (recommended):** Use both engines based on use case
- Backtrader for familiar backtesting workflows
- Nautilus for strategies planned for live trading
- Decision rationale: [ADR-011](docs/adr/ADR-011-nautilus-decision.md)

### Global Access Pattern

```python
from finbot.config import settings, logger, settings_accessors  # Dynaconf settings + logger + settings accessors
from finbot.libs.api_manager import api_manager                  # Singleton API registry
```

### Package Structure

All packages live under the single `finbot/` namespace:

#### `finbot/config/` — Configuration Layer
- **Dynaconf-based** environment-aware YAML files (`development.yaml`, `production.yaml`)
- **APIKeyManager**: Lazy-loaded API keys from env vars (no import failures when keys missing)
- Set `DYNACONF_ENV=development|production` to switch environments

#### `finbot/constants/` — Application Constants
- `path_constants.py`: All data directory paths (auto-creates missing dirs)
- `api_constants.py`: API URLs and endpoints
- `datetime_constants.py`, `networking_constants.py`, etc.
- `tracked_collections/`: CSV manifests of tracked funds, FRED symbols, MSCI indexes

#### `finbot/libs/` — Core Infrastructure
- **`api_manager/`**: Central API registry with `APIResourceGroup` for rate limits/retry
  - Supports FRED, Alpha Vantage, NASDAQ Data Link, Google Finance, BLS APIs
- **`logger/`**: Queue-based async logging
  - Dual output: colored console (stdout for INFO+, stderr for ERROR+) + JSON file
  - Rotating file handlers (5MB, 3 backups)

#### `finbot/core/contracts/` — Engine-Agnostic Contracts

Typed frozen dataclasses for portable, engine-agnostic backtesting and execution. All contracts use `slots=True`, `__post_init__` validation, and are available via `from finbot.core.contracts import ...`.

21 modules covering: models, orders, checkpoint, latency, risk, costs, schemas, versioning, serialization, snapshot, walkforward, regime, batch, interfaces, missing_data, optimization, risk_analytics, portfolio_analytics, realtime_data, factor_analytics, corporate_actions. See Key Entry Points table for file paths.

#### `finbot/services/execution/` — Execution Simulation System

Paper trading simulator with realistic latency, risk controls, and state persistence. **No `__init__.py`** — import from submodules directly:

```python
from finbot.services.execution.execution_simulator import ExecutionSimulator
from finbot.services.execution.checkpoint_manager import CheckpointManager
```

- **`execution_simulator.py`**: Order submission, market/limit execution with slippage, position/cash tracking, risk checking, pending action queue, checkpoint support
- **`order_validator.py`**: Quantity, symbol, and limit price validation with typed rejection reasons
- **`order_registry.py`**: Order lookup and lifecycle queries
- **`pending_actions.py`**: Time-based action queue with O(log n) binary search insertion for latency simulation
- **`risk_checker.py`**: Position limits, exposure limits, drawdown limits, kill-switch
- **`checkpoint_manager.py`**: Create/save/load/restore state checkpoints (`checkpoints/{simulator_id}/{timestamp}.json`)
- **`checkpoint_serialization.py`**: JSON-safe serialization (Decimal→string, datetime→ISO)

#### `finbot/services/backtesting/` — Backtrader-Based Backtesting Engine

Entry point: `BacktestRunner` in `backtest_runner.py`

**Key modules:**
- **`backtest_runner.py`**: Main orchestrator, wraps Backtrader's Cerebro engine
- **`run_backtest.py`**: Single backtest execution
- **`backtest_batch.py`**: Parallel batch backtesting
- **`compute_stats.py`**: Performance metrics using quantstats (Sharpe, Sortino, Calmar, max drawdown, Kelly criterion)
- **`rebalance_optimizer.py`**: Gradient descent-like optimizer for portfolio rebalance ratios
- **`hypothesis_testing.py`**: Statistical hypothesis tests (t-test, bootstrap, permutation, etc.)

**13 strategies** (in `strategies/`): `rebalance`, `no_rebalance`, `sma_crossover`, `sma_crossover_double`, `sma_crossover_triple`, `macd_single`, `macd_dual`, `dip_buy_sma`, `dip_buy_stdev`, `sma_rebal_mix`, `dual_momentum`, `risk_parity`, `regime_adaptive`

**Supporting:** `analyzers/cv_tracker.py` (cash/value tracking), `brokers/` (commission schemes), `indicators/` (returns), `sizers/` (position sizing)

#### `finbot/services/simulation/` — Simulators (Vectorized Numpy)

- **`fund_simulator.py`**: Leveraged fund simulation with fees, spread costs, LIBOR borrowing (vectorized numpy)
- **`bond_ladder/`**: 6-file bond ladder simulator using `numpy_financial.pv()`
- **`stock_index_simulator.py`**, **`bond_index_simulator.py`**: Generic index simulation
- **`sim_specific_stock_indexes.py`**, **`sim_specific_bond_indexes.py`**: S&P 500 TR, Nasdaq 100 TR, ICE Treasury indexes
- **`sim_specific_funds.py`**: 16 fund simulation functions (SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, etc.)
- **`monte_carlo/`**: Single-asset and correlated multi-asset Monte Carlo simulation

#### `finbot/services/optimization/` — Portfolio Optimizers
- **`dca_optimizer.py`**: DCA grid search across ratios, durations, purchase intervals (multiprocessing)
- **`pareto_optimizer.py`**: Multi-objective Pareto optimization with dashboard integration
- **`rebalance_optimizer.py`**: Placeholder (see `backtesting/rebalance_optimizer.py` for working version)

#### `finbot/services/health_economics/` — Health Economics Analysis
- **`qaly_simulator.py`**: Monte Carlo QALY simulation with stochastic cost/utility/mortality
- **`cost_effectiveness.py`**: ICER, NMB, CEAC, cost-effectiveness plane (probabilistic sensitivity analysis)
- **`treatment_optimizer.py`**: Grid-search treatment schedule optimization (dose frequency x duration)
- **`scenarios/`**: Clinical scenarios — cancer screening, hypertension, vaccine (3 scenarios composed from above modules)

#### `finbot/services/data_quality/` — Data Quality and Observability
- **`data_source_registry.py`**: Registry of 7 data sources with staleness thresholds
- **`check_data_freshness.py`**: Scan directories and report freshness status
- **`validate_dataframe.py`**: Lightweight DataFrame validation (empty, schema, duplicates, nulls)

#### `finbot/services/risk_analytics/` — Standalone Risk Analytics

Standalone risk analysis on any returns/price series, independent of the backtesting engine.

- **`var.py`**: VaR and CVaR — historical, parametric, Monte Carlo methods; multi-day scaling; expanding-window backtest
- **`stress.py`**: Parametric stress testing — 4 built-in crisis scenarios + custom `StressScenario` support
- **`kelly.py`**: Kelly criterion — single-asset discrete formula + multi-asset matrix Kelly `f* = Sigma^-1 * mu`
- **`viz.py`**: 6 Plotly charts (VaR distribution, comparison, stress path/comparison, Kelly fractions, correlation heatmap)

#### `finbot/services/portfolio_analytics/` — Standalone Portfolio Analytics

Standalone portfolio analysis on any returns/price series.

- **`rolling.py`**: Rolling Sharpe, annualized vol, beta over configurable windows
- **`benchmark.py`**: OLS alpha, beta, R-squared, tracking error, information ratio, up/down capture
- **`drawdown.py`**: Full drawdown period detection — underwater curve, per-episode peak/trough/recovery
- **`correlation.py`**: HHI, effective N, diversification ratio, pairwise correlation matrix
- **`viz.py`**: 6 Plotly charts (rolling metrics, benchmark scatter, underwater, drawdown bars, correlation heatmap, weights bar)

#### `finbot/services/realtime_data/` — Real-Time Market Data

Multi-provider real-time quotes for US and Canadian equities via REST (no vendor SDKs).

- **`_providers/`**: `alpaca_provider.py` (IEX feed), `twelvedata_provider.py` (US + TSX/TSXV), `yfinance_provider.py` (fallback)
- **`composite_provider.py`**: Priority routing with fallback (Canadian → Twelve Data → yfinance; US → Alpaca → Twelve Data → yfinance)
- **`quote_cache.py`**: Thread-safe TTL cache (15s default)
- **`viz.py`**: 3 Plotly charts (quote table, sparkline, provider status bar)

#### `finbot/services/factor_analytics/` — Fama-French-Style Factor Analytics

Standalone multi-factor model modules. Accept returns arrays/DataFrames — no data fetching.

- **`factor_regression.py`**: OLS regression with auto-detected model type (CAPM/FF3/FF5/CUSTOM) + rolling R-squared
- **`factor_attribution.py`**: Per-factor return contribution decomposition
- **`factor_risk.py`**: Systematic/idiosyncratic variance decomposition with per-factor marginal contributions
- **`viz.py`**: 5 Plotly charts (loadings, attribution, risk donut, rolling R-squared, factor correlation heatmap)

#### `finbot/utils/` — Utility Library (~176 files)

- **`data_collection_utils/`**: yfinance, FRED, Google Finance, Shiller scrapers, Alpha Vantage, BLS, Pandas DataReader
- **`finance_utils/`**: CGR, percent change, period detection, price series merging, risk-free rate, drawdown, inflation adjustment
- **`pandas_utils/`**: Save/load (parquet, CSV, Excel), date filtering, frequency detection, hashing
- **`datetime_utils/`**: Date conversions, US business dates, time ranges
- **`data_science_utils/`**: Data cleaning, imputation, outlier detection, scalers/normalizers
- **`plotting_utils/`**: Interactive plotly visualizations
- **`request_utils/`**: HTTP handler with retry, exponential backoff, response caching (zstandard)
- **`multithreading_utils/`**: Thread pool configuration

#### `scripts/` — Automation Scripts
- **`update_daily.py`**: Daily data update pipeline — fetches prices/FRED/Shiller, re-runs all simulations

### Data Storage

All data stored as **parquet** files under `finbot/data/` (configured in `finbot/constants/path_constants.py`): `simulations/`, `backtests/`, `price_histories/`, `longtermtrends_data/`, `fred_data/`, `yfinance_data/`, `google_finance_data/`, `shiller_data/`, `alpha_vantage_data/`, `bls_data/`, `responses/`.

## Environment Variables

Required for data collection features (loaded lazily via `APIKeyManager`):

```bash
export DYNACONF_ENV=development  # or production
export ALPHA_VANTAGE_API_KEY=your_key
export ALPACA_API_KEY=your_key            # Real-time US quotes (IEX feed)
export ALPACA_SECRET_KEY=your_secret      # Alpaca secret key
export TWELVEDATA_API_KEY=your_key        # Real-time US + Canada quotes
export NASDAQ_DATA_LINK_API_KEY=your_key
export US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

Create `.env` file in `finbot/config/` (excluded by `.gitignore`).

## Key Entry Points

| File | Purpose |
| --- | --- |
| **Core Contracts** | |
| `finbot/core/contracts/models.py` | Backtest request/result models, events |
| `finbot/core/contracts/orders.py` | Order lifecycle tracking |
| `finbot/core/contracts/checkpoint.py` | State persistence contracts |
| `finbot/core/contracts/risk.py` | Risk management rules |
| `finbot/core/contracts/schemas.py` | Data validation, canonical metrics |
| `finbot/core/contracts/optimization.py` | Optimization result contracts |
| **Execution System** | |
| `finbot/services/execution/execution_simulator.py` | Paper trading simulator with latency/risk controls |
| `finbot/services/execution/checkpoint_manager.py` | State checkpoint/restore for disaster recovery |
| `finbot/services/execution/risk_checker.py` | Risk limit enforcement (position, exposure, drawdown) |
| `finbot/services/execution/order_registry.py` | Order lookup and lifecycle queries |
| **Backtesting** | |
| `finbot/services/backtesting/run_backtest.py` | Run single backtest |
| `finbot/services/backtesting/backtest_batch.py` | Run backtests in parallel |
| `finbot/services/backtesting/backtest_runner.py` | BacktestRunner class (Cerebro wrapper) |
| `finbot/services/backtesting/hypothesis_testing.py` | Statistical hypothesis tests for strategy evaluation |
| **Simulations** | |
| `finbot/services/simulation/fund_simulator.py` | Simulate leveraged funds with fees |
| `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py` | Simulate bond ladders |
| `finbot/services/simulation/monte_carlo/monte_carlo_simulator.py` | Monte Carlo simulations |
| **Optimization** | |
| `finbot/services/optimization/dca_optimizer.py` | DCA grid search optimizer |
| `finbot/services/optimization/pareto_optimizer.py` | Multi-objective Pareto optimizer |
| **Infrastructure** | |
| `scripts/update_daily.py` | Daily data update + simulation pipeline |
| `finbot/cli/main.py` | CLI entry point (`finbot simulate/backtest/optimize/update/status/dashboard`) |
| `finbot/dashboard/app.py` | Streamlit dashboard entry point (12 pages) |
| **Other Services** | |
| `finbot/services/health_economics/qaly_simulator.py` | QALY Monte Carlo simulation |
| `finbot/services/health_economics/cost_effectiveness.py` | Cost-effectiveness analysis (ICER/NMB/CEAC) |
| `finbot/services/health_economics/scenarios/` | Clinical scenarios: cancer screening, hypertension, vaccine |
| `finbot/services/data_quality/check_data_freshness.py` | Data freshness monitoring |
| **Risk Analytics** | |
| `finbot/services/risk_analytics/var.py` | VaR / CVaR (historical, parametric, Monte Carlo) |
| `finbot/services/risk_analytics/stress.py` | Parametric stress testing (4 built-in scenarios) |
| `finbot/services/risk_analytics/kelly.py` | Kelly criterion (single + multi-asset) |
| `finbot/services/risk_analytics/viz.py` | 6 risk analytics Plotly charts |
| `finbot/core/contracts/risk_analytics.py` | Risk analytics result contracts |
| **Portfolio Analytics** | |
| `finbot/services/portfolio_analytics/rolling.py` | Rolling Sharpe, vol, beta |
| `finbot/services/portfolio_analytics/benchmark.py` | Alpha, beta, R-squared, tracking error, IR, up/down capture |
| `finbot/services/portfolio_analytics/drawdown.py` | Drawdown period detection + underwater curve |
| `finbot/services/portfolio_analytics/correlation.py` | HHI, effective N, diversification ratio |
| `finbot/services/portfolio_analytics/viz.py` | 6 portfolio analytics Plotly charts |
| `finbot/core/contracts/portfolio_analytics.py` | Portfolio analytics result contracts |
| **Real-Time Data** | |
| `finbot/services/realtime_data/composite_provider.py` | Multi-provider quote fetcher with fallback + caching |
| `finbot/services/realtime_data/quote_cache.py` | Thread-safe TTL cache for quotes |
| `finbot/services/realtime_data/_providers/alpaca_provider.py` | Alpaca IEX feed (US equities) |
| `finbot/services/realtime_data/_providers/twelvedata_provider.py` | Twelve Data (US + Canada/TSX) |
| `finbot/services/realtime_data/_providers/yfinance_provider.py` | yfinance fallback (always available) |
| `finbot/services/realtime_data/viz.py` | 3 real-time data Plotly charts |
| `finbot/core/contracts/realtime_data.py` | Quote, QuoteBatch, ProviderStatus contracts |
| **Factor Analytics** | |
| `finbot/services/factor_analytics/factor_regression.py` | OLS factor regression + rolling R-squared |
| `finbot/services/factor_analytics/factor_attribution.py` | Per-factor return contribution decomposition |
| `finbot/services/factor_analytics/factor_risk.py` | Systematic/idiosyncratic variance decomposition |
| `finbot/services/factor_analytics/viz.py` | 5 factor analytics Plotly charts |
| `finbot/core/contracts/factor_analytics.py` | FactorModelType, FactorRegressionResult, FactorAttributionResult, FactorRiskResult |

## Code Style

- **Linter**: ruff (line-length 120, Python 3.11 target)
- **Formatter**: ruff format
- **Type checker**: mypy (config in `pyproject.toml`)
- **Security**: bandit
- **Lint rules**: E, F, UP, B, SIM, I, C901, N, A, C4, RUF, LOG, PERF
- **Pre-commit hooks**: 15 automatic (whitespace, YAML, AST, private keys, ruff, line endings) + 2 manual (mypy, bandit)

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_imports.py -v

# Run tests matching pattern
uv run pytest -k test_simulation

# Run with coverage
uv run pytest --cov=finbot tests/
```

**Test structure**: `tests/unit/` contains 1749 tests across 50+ files covering imports, simulation math, finance utils, all 13 strategies, health economics, order lifecycle, latency, risk controls, checkpoints, cost models, corporate actions, walk-forward, regime detection, dashboard charts, risk analytics, portfolio analytics, real-time data, and factor analytics. `tests/integration/` reserved for future integration tests.

## Documentation

**MkDocs documentation site** (`docs_site/`):

```bash
make docs-serve       # or: uv run mkdocs serve (http://127.0.0.1:8000)
make docs-build       # build static site
uv run mkdocs gh-deploy  # deploy to GitHub Pages
```

Source in `docs_site/` (index, user-guide, api, research, contributing, changelog). Project docs in `docs/` (adr, guidelines, planning, research, guides). See [ADR-003](docs/adr/ADR-003-add-mkdocs-documentation.md).

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) on push/PR to main:
- Lint (`ruff check`), format (`ruff format --check`), type check (`mypy`), security (`bandit`, `pip-audit`)
- Tests: `pytest --cov` on Python 3.11, 3.12, 3.13
- Parity gate: Golden strategy tests (GS-01, GS-02, GS-03)
- Performance regression: benchmarks vs `tests/performance/baseline.json` (fails if >20% slower)
- Update baseline: `uv run python tests/performance/benchmark_runner.py --update-baseline`

## Architecture Decisions

See `docs/adr/` for architectural decision records:
- **ADR-001**: Consolidate three repos (finbot, bb, backbetter) into one
  - Drop numba → vectorized numpy + numpy-financial
  - Drop Scrapy → bb's Selenium
  - Keep quantstats
  - Replace pickle → parquet
  - Lazy API key loading
- **ADR-004**: Consolidate package layout — move config/, constants/, libs/ under finbot/ as subpackages

## Key Design Patterns

| Pattern | Implementation | Rationale |
| --- | --- | --- |
| **Settings Accessors** | `settings_accessors` module in `finbot/config/` | Lazy accessors for MAX_THREADS and API keys (alpha_vantage, nasdaq_data_link, bls, google_finance) |
| **Lazy API keys** | `APIKeyManager.get_key()` only loads on first access | Prevents import failures when keys not needed |
| **Queue-based logging** | `finbot/libs/logger/setup_queue_logging.py` | Non-blocking async logging for performance |
| **Structured audit logs** | `finbot/libs/audit/audit_logger.py` | Queryable audit trails for compliance and debugging |
| **Vectorized simulation** | Numpy broadcasting in `fund_simulator.py` | Faster than numba loop, no JIT compilation required |
| **Parquet everywhere** | All serialization uses `to_parquet()`/`read_parquet()` | Safer, faster, smaller than pickle |
| **Auto-create dirs** | `path_constants._process_dir()` uses `mkdir(exist_ok=True)` | Works in CI, fresh clones, no manual setup |
| **Typed contracts** | Frozen dataclasses in `finbot/core/contracts/` | Engine-agnostic, immutable, serializable |
| **Versioned schemas** | `CONTRACT_SCHEMA_VERSION` + migration functions | Forward compatibility, automatic upgrades |
| **Pluggable risk** | `RiskConfig` with composable rules | Add/remove risk controls without code changes |
| **Pending action queue** | Binary search insertion in `PendingActionQueue` | O(log n) insertion, realistic latency simulation |
| **Checkpoint versioning** | `CHECKPOINT_VERSION` in all checkpoints | Detect incompatible restores, enable migration |
| **Decimal precision** | String serialization for Decimal in JSON | Preserve precision across checkpoint/restore |

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
3. Run tests: `uv run pytest`
4. Run linter: `uv run ruff check . --fix`
5. Run formatter: `uv run ruff format .`
6. Commit with conventional commit message: `type(scope): subject` (e.g., `feat(api): add new endpoint`)
7. Push and create PR — CI must pass

### Commit Authorship Policy

**IMPORTANT:** All commits must list only human authors, co-authors, and contributors.

- **Do:** Attribute commits to human developers
- **Don't:** Include AI assistants (Claude, Gemini, Codex, ChatGPT, Copilot, etc.) in author, co-author, or contributor fields
- **Don't:** Add "AI-generated" or "Created with AI" notices in code, docs, or commit messages
- **Rationale:** Commits represent human accountability. AI tools are instruments, not authors.
- **Scope:** Applies to all commits and documentation attribution (README, ADRs, research, planning, changelogs, release notes)

### Agent File Sync

- `AGENTS.md` is canonical for agent instructions.
- `CLAUDE.md` and `GEMINI.md` must be symlinks to `AGENTS.md`.

## See Also

- `README.md`: User-facing quick start and usage guide
- `docs/adr/`: Architectural decision records
- `docs/planning/archive/`: Archived implementation plans
- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `pyproject.toml`: Dependencies (PEP 621), tool configuration
