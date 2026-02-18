# AGENTS.md

## Repository Overview

Finbot is a financial data collection, simulation, and backtesting platform that consolidates:
- Modern infrastructure (Dynaconf config, queue-based logging, API management)
- **Engine-agnostic execution system** with orders, latency simulation, risk controls, and state checkpoints
- Comprehensive backtesting engine (Backtrader-based with 12 strategies)
- **Typed contracts** for portable backtests with versioning, serialization, and migration
- Advanced simulation systems (fund, bond ladder, Monte Carlo, multi-asset Monte Carlo, index simulators)
- Portfolio optimization (DCA optimizer, rebalance optimizer)
- **Cost models** and **corporate actions** handling for realistic backtests
- **Walk-forward analysis** and **market regime detection** for robust strategy evaluation
- **Experiment tracking** with snapshots, batch observability, and dashboard comparison
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

## Current Delivery Status (2026-02-18)

**Status:** Production-ready. Priority 0-6 substantially complete (P5: 93.3%, P6: 100%). Priority 7 in progress (24/27 items, 89%).

### Priority 5: OMSAS/CanMEDS Improvements (93.3% Complete)

**Completed:** 42/45 items across 7 categories
- ✅ Governance & Professionalism (7/7): LICENSE, SECURITY, CODE_OF_CONDUCT, templates
- ✅ Quality & Reliability (4/5): CI/CD, test coverage (59.20%), integration tests, py.typed
- ✅ Documentation (6/6): MkDocs site, API docs, docstring enforcement, limitations
- ✅ Health Economics (4/5): Research papers, clinical scenarios, methodology
- ✅ Ethics & Security (6/6): Disclaimers, audit trails, license auditing, Docker security
- ✅ Testing (5/5): Property-based testing, CLI tests, performance regression
- ✅ Professional Polish (10/11): CODEOWNERS, releases, changelog, TestPyPI, OpenSSF

**Remaining:** 3 items (Item 12 partially started, Items 22 & 42 blocked on external resources)

### Priority 6: Backtesting-to-Live Readiness (100% Complete)

**All Epics Complete (E0-E6):**
- ✅ **E0**: Baseline and decision framing
- ✅ **E1**: Contracts and schema layer
- ✅ **E2**: Backtrader adapter and parity harness (100% parity on 3 golden strategies)
- ✅ **E3**: Fidelity improvements (cost models, corporate actions, walk-forward, regime)
- ✅ **E4**: Reproducibility (experiment tracking, snapshots, batch observability, dashboard)
- ✅ **E5**: Live-readiness (orders, latency simulation, risk controls, checkpoints)
- ✅ **E6**: NautilusTrader pilot and decision gate (Hybrid approach adopted)

**Key Metrics:**
- 1063+ total tests (all passing)
- 61.63% test coverage (exceeds 60% target)
- 100% parity maintained on all golden strategies
- CI parity gate prevents regressions
- 7 CI jobs (lint, type-check, security, test, docs, parity, performance)
- All GitHub Actions pinned to SHA hashes for supply chain security

**Authoritative tracking docs:**
- `docs/planning/roadmap.md` (overall roadmap)
- `docs/planning/priority-5-6-completion-status.md` (detailed summary)
- `docs/planning/backtesting-live-readiness-backlog.md` (Epic tracking)
- `docs/planning/archive/` (20+ completed implementation plans)

### Priority 7: External Impact & Advanced Capabilities (89% Complete)

**In Progress:** 24/27 items complete
- ✅ **P7.1**: Stricter mypy Phase 1 audit — 355 errors catalogued, phased roadmap published
- ✅ **P7.2**: Test coverage raised to 61.63% (1063+ tests)
- ✅ **P7.3**: Scheduled CI for daily data updates
- 🟡 **P7.4**: Conventional commits guide created (user action required)
- ✅ **P7.5**: Blog post — "Why I Built Finbot"
- ✅ **P7.6**: Blog post — "Backtesting Engines Compared"
- ✅ **P7.7**: Tutorial series — "Health Economics with Python" (3 parts)
- ✅ **P7.10**: CanMEDS Competency Reflection essay
- ✅ **P7.11**: Finbot Portfolio Summary (1-pager)
- ✅ **P7.12**: Lessons Learned document (15 lessons)
- ✅ **P7.13**: Impact Statement
- ✅ **P7.14**: Nautilus strategy migration guide
- ✅ **P7.15**: Walk-forward visualization — `walkforward_viz.py` (5 chart functions, dashboard page 8, 23 tests)
- ✅ **P7.16**: Regime-adaptive strategy — `strategies/regime_adaptive.py` + 19 tests
- ✅ **P7.17**: Multi-objective Pareto optimizer — `pareto_optimizer.py` + dashboard integration
- ✅ **P7.22**: Hypothesis testing module — `hypothesis_testing.py` (6 functions, 24 tests)
- ✅ **P7.23**: Deferred unit tests — 39 new tests (bond_ladder, backtest_batch, rebalance_optimizer)
- ✅ **P7.24**: Roadmap updates (ongoing)
- ✅ **P7.21**: Health economics clinical scenarios — cancer screening, hypertension, vaccine (3 scenarios, 22 tests, dashboard tab 4)
- ✅ **P7.26**: FAQ document (30+ Q&A pairs)

**Remaining notable items:**
- ⬜ P7.8/P7.9: Video/poster (requires user recording/design)
- ⬜ P7.20: Video tutorials (requires user recording)

**Mypy hardening:** Phase 4 (backtesting core) and Phase 5 (strategies/costs/indicators) complete — `disallow_untyped_defs = true` enforced for all `finbot.services.backtesting.*` modules.

**Implementation plan:** `docs/planning/priority-7-batch4-implementation-plan.md` (v1.0)

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

Typed contracts for portable, engine-agnostic backtesting and execution. Enables multiple backends (Backtrader, NautilusTrader) with consistent interfaces.

**Core Modules:**

- **`models.py`**: Core data models
  - `BacktestRunRequest`, `BacktestRunResult`, `BacktestRunMetadata`: Backtest request/response
  - `BarEvent`, `FillEvent`, `OrderRequest`: Event types
  - `PortfolioSnapshot`: Point-in-time portfolio state
  - `OrderSide`, `OrderType`: Enums for order parameters

- **`orders.py`**: Order lifecycle tracking
  - `Order`: Complete order state (status, fills, rejections, timestamps)
  - `OrderExecution`: Individual fill records
  - `OrderStatus`: Enum (NEW, SUBMITTED, PARTIALLY_FILLED, FILLED, REJECTED, CANCELLED)
  - `RejectionReason`: Typed rejection reasons (funds, validation, risk controls)

- **`checkpoint.py`**: State persistence for disaster recovery
  - `ExecutionCheckpoint`: Snapshot of ExecutionSimulator state
  - `CHECKPOINT_VERSION`: Schema version for migration support
  - Captures: cash, positions, orders, risk state, configuration

- **`latency.py`**: Realistic order timing simulation
  - `LatencyConfig`: Submission, fill, and cancellation delays
  - Pre-configured profiles: `LATENCY_INSTANT`, `LATENCY_FAST`, `LATENCY_NORMAL`, `LATENCY_SLOW`
  - Supports min/max ranges for realistic variance

- **`risk.py`**: Risk management rules
  - `RiskConfig`: Composable risk rule configuration
  - `PositionLimitRule`: Max shares/value per position
  - `ExposureLimitRule`: Gross/net exposure limits
  - `DrawdownLimitRule`: Daily/total drawdown protection
  - `RiskViolation`: Typed violation records

- **`costs.py`**: Cost modeling for realistic simulations
  - `CostModel`: Slippage + commission configuration
  - `CostEvent`: Individual cost records (type, amount, timestamp)
  - `CostSummary`: Aggregated cost metrics
  - `CostType`: Enum (COMMISSION, SLIPPAGE, BORROW, FEE)

- **`schemas.py`**: Data validation and canonical metrics
  - `validate_bar_dataframe()`: OHLCV data validation
  - `extract_canonical_metrics()`: Standardized performance metrics
  - `CANONICAL_METRIC_KEYS`: Standard metric names (CAGR, Sharpe, Sortino, max drawdown, etc.)
  - Column mappings for cross-engine compatibility

- **`versioning.py`**: Schema versioning and migration
  - `CONTRACT_SCHEMA_VERSION`: Current contract version
  - `BACKTEST_RESULT_SCHEMA_VERSION`: Result format version
  - `is_schema_compatible()`: Version compatibility check
  - `migrate_backtest_result_payload()`: Automatic migration

- **`serialization.py`**: Portable result serialization
  - `backtest_result_to_payload()`: Serialize to JSON-compatible dict
  - `backtest_result_from_payload()`: Deserialize with migration
  - `build_backtest_run_result_from_stats()`: Build from metrics dict

- **`snapshot.py`**: Data lineage tracking
  - `DataSnapshot`: Captures data source versions and checksums
  - `compute_data_content_hash()`: Content-based hashing
  - `compute_snapshot_hash()`: Snapshot fingerprinting

- **`walkforward.py`**: Walk-forward analysis
  - `WalkForwardConfig`: Window configuration (rolling/anchored)
  - `WalkForwardWindow`: Single window definition
  - `WalkForwardResult`: Aggregated walk-forward metrics

- **`regime.py`**: Market regime detection
  - `MarketRegime`: Enum (BULL, BEAR, SIDEWAYS, HIGH_VOL, LOW_VOL)
  - `RegimeConfig`: Detection parameters (lookback, thresholds)
  - `RegimeDetector`: Regime classification logic
  - `RegimePeriod`: Regime time periods

- **`batch.py`**: Batch execution tracking
  - `BatchRun`: Batch metadata and status
  - `BatchItemResult`: Individual backtest result
  - `BatchStatus`: Enum (PENDING, RUNNING, COMPLETED, FAILED)
  - `ErrorCategory`: Typed error classification

- **`interfaces.py`**: Engine abstraction interfaces
  - `BacktestEngine`: Engine interface (Backtrader, Nautilus)
  - `ExecutionSimulator`: Execution interface for paper trading
  - `MarketDataProvider`: Data source interface
  - `PortfolioStateStore`: State persistence interface

- **`missing_data.py`**: Missing data policies
  - `MissingDataPolicy`: How to handle gaps (ERROR, WARN, SKIP, FILL)
  - `DEFAULT_MISSING_DATA_POLICY`: Project-wide default

**Export:** All contracts available via `from finbot.core.contracts import ...`

#### `finbot/services/execution/` — Execution Simulation System

Paper trading simulator with realistic latency, risk controls, and state persistence. Engine-agnostic, usable standalone or integrated with backtesting engines.

**Core Components:**

- **`execution_simulator.py`**: Main execution simulator (350+ lines)
  - Order submission with latency simulation
  - Market/limit order execution with slippage
  - Position and cash tracking
  - Risk checking before order acceptance
  - Pending action queue for delayed execution
  - Full order lifecycle tracking
  - Configurable commission and slippage
  - State checkpoint support via `simulator_id`

- **`order_validator.py`**: Order validation logic
  - Quantity validation (positive, non-zero)
  - Symbol validation (non-empty)
  - Limit price validation for limit orders
  - Returns typed rejection reasons

- **`pending_actions.py`**: Latency simulation (104 lines)
  - `PendingActionQueue`: Time-based action queue
  - `PendingAction`: Scheduled actions (submit, fill, cancel)
  - Binary search insertion for O(log n) performance
  - Process actions up to current time

- **`risk_checker.py`**: Risk controls enforcement (300 lines)
  - Position limit checking (max shares, max value)
  - Exposure limit checking (gross, net)
  - Drawdown limit checking (daily, total)
  - Trading kill-switch (enable/disable)
  - Peak value and daily start tracking
  - Returns typed violation reasons

- **`checkpoint_manager.py`**: State persistence (360 lines)
  - `create_checkpoint()`: Extract simulator state
  - `save_checkpoint()`: Persist to JSON with versioning
  - `load_checkpoint()`: Load from disk (latest or specific timestamp)
  - `restore_simulator()`: Rebuild simulator from checkpoint
  - `list_checkpoints()`: Available checkpoints for simulator
  - Storage: `checkpoints/{simulator_id}/{timestamp}.json`

- **`checkpoint_serialization.py`**: Checkpoint serialization (168 lines)
  - `serialize_checkpoint()`: JSON-compatible dict conversion
  - `deserialize_checkpoint()`: Rebuild from dict
  - Decimal-to-string conversion for precision
  - Datetime ISO format handling
  - Order and execution serialization helpers

**Example Usage:**

```python
from decimal import Decimal
from finbot.core.contracts import Order, OrderSide, OrderType, LatencyConfig
from finbot.core.contracts.risk import RiskConfig, DrawdownLimitRule
from finbot.services.execution import ExecutionSimulator, CheckpointManager

# Create simulator with risk controls and latency
risk_config = RiskConfig(
    drawdown_limit=DrawdownLimitRule(max_daily_drawdown_pct=Decimal("5"))
)
simulator = ExecutionSimulator(
    initial_cash=Decimal("100000"),
    latency_config=LATENCY_NORMAL,
    risk_config=risk_config,
    simulator_id="my-paper-account",
)

# Submit order (will be delayed by latency)
order = Order(...)
simulator.submit_order(order, timestamp=datetime.now())

# Process market data (triggers fills)
simulator.process_market_data(current_time, current_prices)

# Checkpoint state for recovery
manager = CheckpointManager("checkpoints")
checkpoint = manager.create_checkpoint(simulator)
manager.save_checkpoint(checkpoint)

# Later: restore from checkpoint
restored = manager.restore_simulator(checkpoint)
```

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
- `dual_momentum.py`: Dual momentum (absolute + relative) with safe-asset fallback
- `risk_parity.py`: Inverse-volatility weighting with periodic rebalance

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
- `monte_carlo_simulator.py`: Main simulator (single-asset)
- `multi_asset_monte_carlo.py`: Correlated multi-asset simulation using multivariate normal
- `sim_types.py`: Normal distribution simulation
- `visualization.py`: Plot trials and histograms

##### `finbot/services/optimization/` — Portfolio Optimizers
- **`dca_optimizer.py`**: DCA (Dollar Cost Averaging) optimizer
  - Grid search across ratios, durations, purchase intervals using multiprocessing
  - Calculates CAGR, Sharpe, max drawdown, std dev for each combination
- **`rebalance_optimizer.py`**: Placeholder (see `backtesting/rebalance_optimizer.py` for working version)

##### `finbot/services/health_economics/` — Health Economics Analysis
- **`qaly_simulator.py`**: Monte Carlo QALY simulation with stochastic cost/utility/mortality
- **`cost_effectiveness.py`**: ICER, NMB, CEAC, cost-effectiveness plane (probabilistic sensitivity analysis)
- **`treatment_optimizer.py`**: Grid-search treatment schedule optimization (dose frequency x duration)
- **`scenarios/`**: Real-world clinical scenario analyses composed from the above modules
  - `models.py`: `ScenarioResult` frozen dataclass (ICER, NMB, QALY gain, cost difference)
  - `cancer_screening.py`: Annual mammography vs. no screening (10-year horizon)
  - `hypertension.py`: ACE inhibitor vs. lifestyle modification for Stage 1 HTN (5-year)
  - `vaccine.py`: Influenza vaccination vs. no vaccination for elderly ≥65 (1-year, societal)

##### `finbot/services/data_quality/` — Data Quality and Observability
- **`data_source_registry.py`**: Registry of 7 data sources with staleness thresholds
- **`check_data_freshness.py`**: Scan directories and report freshness status
- **`validate_dataframe.py`**: Lightweight DataFrame validation (empty, schema, duplicates, nulls)

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
- `get_inflation_adjusted_returns.py`: Deflate nominal prices by FRED CPI data

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

Directories under `finbot/data/` (configured in `finbot/constants/path_constants.py`):
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
| **Execution System** | |
| `finbot/services/execution/execution_simulator.py` | Paper trading simulator with latency/risk controls |
| `finbot/services/execution/checkpoint_manager.py` | State checkpoint/restore for disaster recovery |
| `finbot/services/execution/risk_checker.py` | Risk limit enforcement (position, exposure, drawdown) |
| **Backtesting** | |
| `finbot/services/backtesting/run_backtest.py` | Run single backtest |
| `finbot/services/backtesting/backtest_batch.py` | Run backtests in parallel |
| `finbot/services/backtesting/backtest_runner.py` | BacktestRunner class (Cerebro wrapper) |
| **Simulations** | |
| `finbot/services/simulation/fund_simulator.py` | Simulate leveraged funds with fees |
| `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py` | Simulate bond ladders |
| `finbot/services/simulation/monte_carlo/monte_carlo_simulator.py` | Monte Carlo simulations |
| **Optimization** | |
| `finbot/services/optimization/dca_optimizer.py` | DCA grid search optimizer |
| **Infrastructure** | |
| `scripts/update_daily.py` | Daily data update + simulation pipeline |
| `finbot/cli/main.py` | CLI entry point (`finbot simulate/backtest/optimize/update/status/dashboard`) |
| `finbot/dashboard/app.py` | Streamlit dashboard entry point (6 pages) |
| **Other Services** | |
| `finbot/services/health_economics/qaly_simulator.py` | QALY Monte Carlo simulation |
| `finbot/services/health_economics/cost_effectiveness.py` | Cost-effectiveness analysis (ICER/NMB/CEAC) |
| `finbot/services/health_economics/scenarios/` | Clinical scenarios: cancer screening, hypertension, vaccine |
| `finbot/services/data_quality/check_data_freshness.py` | Data freshness monitoring |

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

**Test structure**:
- `tests/unit/`: Unit tests (645 tests across 30+ files)
  - `test_imports.py`: Smoke tests for all key module imports
  - `test_simulation_math.py`: Simulation math correctness
  - `test_finance_utils.py`: Finance calculation tests
  - `test_strategies.py`, `test_strategies_parametrized.py`: All 12 backtesting strategies
  - `test_health_economics.py`: QALY simulator, CEA, treatment optimizer
  - `test_health_economics_scenarios.py`: Clinical scenarios (cancer screening, hypertension, vaccine, 22 tests)
  - `test_order_lifecycle.py`: Order tracking and execution (20 tests)
  - `test_latency_simulation.py`: Latency hooks and pending actions (17 tests)
  - `test_risk_controls.py`: Risk management (14 tests)
  - `test_checkpoint_recovery.py`: State persistence (18 tests)
  - `test_backtrader_adapter.py`: Backtrader adapter compliance
  - `test_cost_models.py`, `test_corporate_actions.py`: Cost tracking, dividend/split handling
  - `test_walkforward.py`, `test_regime_detection.py`: Walk-forward and regime analysis
  - `test_dashboard_charts.py`: Chart component tests
  - `test_new_strategies.py`: DualMomentum, RiskParity, multi-asset Monte Carlo
  - More test files for core functionality
- `tests/integration/`: Integration tests (future)

## Documentation

**MkDocs documentation site** (`docs_site/`):

```bash
# Serve locally with auto-reload
make docs-serve
# or
uv run mkdocs serve
# Access at http://127.0.0.1:8000

# Build static site
make docs-build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

**Documentation structure**:
- `docs_site/`: MkDocs source (Markdown)
  - `index.md`: Home page with project overview
  - `user-guide/`: Installation, quick start, CLI reference, configuration
  - `api/`: API reference for services and utilities
  - `research/`: Research documentation
  - `contributing.md`, `changelog.md`: Contributing guide and version history
- `site/`: Generated static site (gitignored)
- `docs/`: Project documentation
  - `adr/`: Architectural Decision Records
  - `guidelines/`: Development guidelines (testing, documentation, roadmap process)
  - `planning/`: Roadmap and implementation guides
  - `research/`: Research findings and analysis
  - `guides/`: Development guides
  - `benchmarks.md`: Performance benchmarks

**Features**:
- Material Design theme with dark mode
- Full-text search
- Auto-generated API reference from docstrings
- Responsive mobile/desktop layout
- Fast builds (~2 seconds)

See [ADR-003](docs/adr/ADR-003-add-mkdocs-documentation.md) for implementation details.

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to main:
- Lint: `ruff check .`
- Format check: `ruff format --check .`
- Type check: `mypy finbot/` (continue-on-error)
- Security: `bandit -r finbot/`, `pip-audit` (continue-on-error)
- Tests: `pytest tests/ -v --cov` (Python 3.11, 3.12, 3.13)
- Parity gate: Golden strategy parity tests (GS-01, GS-02, GS-03)
- **Performance regression:** Benchmark fund_simulator and backtest_adapter (fails if >20% slower)

**Performance Regression Testing** (Priority 5 Item 33):
- Automated benchmarks run on every PR
- Compares to baseline in `tests/performance/baseline.json`
- Fails CI if performance degrades >20%
- See `tests/performance/README.md` for details
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
6. Commit with conventional commit message following commit authorship policy (see below)
   - Format: `type(scope): subject` (e.g., `feat(api): add new endpoint`)
   - Pre-commit hook validates commit messages automatically
   - See CONTRIBUTING.md for complete guidelines
7. Push and create PR
8. CI must pass

### Commit Authorship Policy

**IMPORTANT:** All commits must list only human authors, co-authors, and contributors.

- ✅ **Do:** Attribute commits to human developers
- ❌ **Don't:** Include AI assistants in author, co-author, or contributor fields. This includes Claude, Gemini, Codex, ChatGPT, Copilot, or any other AI tool.
- ❌ **Don't:** Add "AI-generated" or "Created with AI" notices in code, docs, or commit messages.
- **Rationale:** Commits represent human accountability and decision-making. AI tools are instruments, not authors.

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
- `pyproject.toml`: Dependencies (PEP 621), tool configuration
