# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Snapshot replay support for contract runs via `BacktestRunRequest.data_snapshot_id` and `BacktraderAdapter(enable_snapshot_replay=True)`.
- Batch retry ergonomics in `backtest_batch` with opt-in controls:
  - `retry_failed`
  - `max_retry_attempts`
  - `retry_backoff_seconds`
- Retry observability metadata in batch contracts/registry:
  - `attempt_count`
  - `final_attempt_success`
- E6 benchmark harness: `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`.
- Benchmark artifacts:
  - `docs/research/artifacts/e6-benchmark-2026-02-19.json`
  - `docs/research/artifacts/e6-benchmark-2026-02-19.md`
- User guides:
  - `docs/user-guides/snapshot-replay.md`
  - `docs/user-guides/batch-observability-and-retries.md`

### Changed
- Updated `docs/research/nautilus-pilot-evaluation.md` with measured benchmark data.
- Refreshed `docs/adr/ADR-011-nautilus-decision.md` with evidence snapshot and tradeoff matrix (decision remains Defer for this cycle).
- Updated roadmap/backlog planning artifacts for E4 closure and E6 decision-gate completion.

## [1.0.0] - 2026-02-11

### Added
- **Configuration System Consolidation**: Single Dynaconf-based config system (Priority 0.4)
  - Created `config/settings_accessors.py` with lazy accessors for MAX_THREADS and API keys
  - Added threading configuration to YAML files (max_threads, reserved_threads)
  - Eliminated circular dependency between config/ and libs/
  - Single source of truth for all configuration
- **Enhanced CI/CD Pipeline**: Comprehensive 8-check workflow (Priority 3.4)
  - Poetry metadata validation (`poetry check`)
  - Mypy type checking (non-fatal, 109 pre-existing issues)
  - Bandit security scanning (non-fatal, 6 low-severity issues)
  - pip-audit dependency CVE scanning (non-fatal)
  - Pytest with coverage reporting (17.53% baseline)
  - Codecov integration for coverage tracking
  - CI status, coverage, Python version, and Poetry badges in README
- **CLI Interface**: Full-featured command-line interface using Click (Priority 2.1)
  - `finbot simulate` - Run fund simulations with multiple output formats
  - `finbot backtest` - Run strategy backtests with performance metrics
  - `finbot optimize` - Run portfolio optimization (DCA)
  - `finbot update` - Run daily data update pipeline
  - Global --verbose flag and --version support
  - Interactive plotly visualizations with --plot flag
- **Example Notebooks**: 5 comprehensive Jupyter notebooks (Priority 1.2)
  - Fund Simulation Demo (simulated vs actual ETF performance)
  - DCA Optimization Results (portfolio optimization analysis)
  - Backtest Strategy Comparison (all 10 strategies compared)
  - Monte Carlo Risk Analysis (VaR, percentiles, retirement sustainability)
  - Bond Ladder Analysis (yield curve, ladder construction)
  - Each with methodology, visualizations, key findings, and next steps
- **Research Documentation**: 3 comprehensive research summaries (~50 pages total) (Priority 1.3)
  - Leveraged ETF Simulation Accuracy (tracking error analysis, methodology, use cases)
  - DCA Optimization Findings (optimal allocations, regime analysis, investor guidance)
  - Strategy Backtest Results (10 strategies, statistical significance testing, practical recommendations)
  - Executive summaries, rigorous methodology, comprehensive analysis, conclusions
- **Makefile**: 14 targets for streamlined development workflow (Priority 2.6)
  - `make help`, `make install`, `make test`, `make lint`, `make format`, etc.
  - Comprehensive `make all` runs full CI pipeline locally
  - Excludes notebooks from linting/formatting (different conventions)
- **Test Coverage Expansion**: 444% increase in test coverage (Priority 1.1)
  - Expanded from 18 tests to 80 tests across 8 test files
  - 100% pass rate across all test categories
  - Tests for finance utils, pandas utils, datetime utils, config, strategies, backtest runner, fund simulator
  - Coverage baseline established at 17.53%

### Changed
- **Fund Simulation Refactoring**: Data-driven configuration system (Priority 2.3)
  - Created `FundConfig` dataclass and `FUND_CONFIGS` registry
  - Consolidated 16 individual sim_* functions into generic `simulate_fund(ticker)` function
  - Reduced core implementation from ~288 lines to ~80 lines
  - Maintained backward compatibility with thin wrapper functions
  - Fixed 3 pre-existing bugs (get_history adjust_price parameter)
- **Code Quality Improvements**: Fixed code smells (Priority 2.2, partial)
  - Replaced `print()` statements with `logger.info()` in production code
  - Replaced hardcoded `risk_free_rate = 2.0` with dynamic fetching via `get_risk_free_rate()`
  - Vectorized `compute_stats` cash_utilizations calculation for performance
  - Named all magic number constants (5 additive constants documented)
- **Ruff Configuration Update**: Enhanced linting and formatting (Priority 0.5)
  - Updated ruff from v0.1.15 to v0.11.13
  - Expanded rule selection from 6 to 13 categories (E, F, UP, B, SIM, I, C901, N, A, C4, RUF, LOG, PERF)
  - Fixed all 103 lint violations → 0 violations
  - Updated pre-commit hooks to match Poetry ruff version

### Fixed
- **Logger Code Duplication**: Eliminated duplicate logging code (Priority 0.1)
  - Deleted `config/_logging_utils.py` entirely
  - Consolidated to `libs/logger/utils.py` as single source
  - Changed `InfoFilter` to `NonErrorFilter` for better log stream separation
- **Import-Time Side Effects**: Prevented import failures when env vars not set (Priority 0.2)
  - Converted `ALPHA_VANTAGE_RAPI_HEADERS` to lazy function `get_alpha_vantage_rapi_headers()`
  - Module `constants/api_constants.py` can now be imported without API keys
- **Dangerous Error Handling**: Replaced unsafe exception handling (Priority 0.3)
  - Replaced 8 bare `except Exception:` blocks with specific exceptions
  - Replaced `assert` statements with explicit validation and `ValueError`
  - Added empty data validation to prevent silent failures
- **Path Constants Directory Creation**: Auto-create missing directories
  - Changed from raising errors to using `mkdir(exist_ok=True)`
  - Works in CI, fresh clones, no manual setup required

### Removed
- **Obsolete Config Files**: Deleted 5 obsolete BaseConfig files (Priority 0.4)
  - `config/base_config.py`, `config/development_config.py`, `config/production_config.py`
  - `config/staging_config.py`, `config/testing_config.py`
- **Empty Placeholder Directories**: Cleaned up unused scaffolding (Priority 2.5)
  - `finbot/services/investing/` (empty placeholder)
  - `finbot/models/` (empty placeholder)

### Infrastructure
- **Dependabot Configuration**: Automated dependency updates (Priority 0.6)
  - Weekly pip ecosystem updates (Monday 9am ET)
  - GitHub Actions monitoring for CI workflow updates
  - Grouped minor/patch updates, separate major updates
  - Limited to 5 PRs to avoid flood
- **CHANGELOG.md**: Comprehensive change tracking (Priority 2.4)
  - Keep a Changelog format
  - Project lineage documentation
  - Version history with dates and descriptions

## [0.1.0] - 2026-02-09

### Added - Initial Consolidation
This release represents the consolidation of three separate repositories into a single unified platform. See [ADR-001](docs/adr/ADR-001-consolidate-three-repos.md) for detailed rationale.

- **Modern Infrastructure** (from bb, 2023-2024):
  - Dynaconf-based configuration with environment-aware YAML files
  - Queue-based async logging with colored console output and JSON file logging
  - API manager with rate limiting and retry strategies
  - Comprehensive utility library (~176 files) for data collection, finance, pandas, datetime operations
  - HTTP request handler with exponential backoff and zstandard compression

- **Backtesting Engine** (from finbot, 2021-2022):
  - Backtrader-based backtesting framework with 10 strategies
  - Strategies: Rebalance, NoRebalance, SMA Crossover (single/double/triple), MACD (single/dual), Dip Buying (SMA/StDev), SMA+Rebalance hybrid
  - Performance metrics using quantstats (Sharpe, Sortino, Calmar, max drawdown, Kelly criterion)
  - Rebalance optimizer with gradient descent-like optimization
  - Parallel batch backtesting support

- **Simulation Systems** (from finbot, 2021-2022):
  - Fund simulator: Leveraged ETF simulation with fees, spread costs, LIBOR borrowing
  - Bond ladder simulator: 6-module system with yield curve construction
  - Index simulators: S&P 500 TR, Nasdaq 100 TR, ICE Treasury indexes (1Y, 7Y, 20Y)
  - Fund-specific simulators: 16 funds (SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, 2x/3x short-term treasuries, NTSX)
  - Monte Carlo simulator: Normal distribution simulations with visualization

- **Portfolio Optimization** (from finbot, 2021-2022):
  - DCA optimizer: Grid search across ratios, durations, purchase intervals using multiprocessing
  - Calculates CAGR, Sharpe, max drawdown, std dev for each combination

- **Data Collection** (from bb, 2023-2024):
  - Yahoo Finance price histories (yfinance)
  - FRED economic data (yields, rates, CPI, GDP, unemployment)
  - Google Sheets-based index data
  - Shiller's online datasets (CAPE, PE ratios, S&P data)
  - Alpha Vantage API (quotes, sentiment, economic indicators)
  - Bureau of Labor Statistics data
  - Pandas DataReader wrapper utilities

- **Development Infrastructure**:
  - GitHub Actions CI workflow (Python 3.11, 3.12, 3.13)
  - Pre-commit hooks (ruff, trailing whitespace, security checks)
  - Poetry dependency management
  - 18 initial unit tests (smoke tests and simulation math validation)

### Changed - Migration Decisions
- **Replaced numba with vectorized numpy + numpy-financial**
  - Better Python 3.12+ compatibility
  - No C compiler required
  - Improved performance for fund simulator
  - Plain Python classes instead of @jitclass decorators

- **Replaced pickle with parquet for all data serialization**
  - Faster read/write performance
  - Smaller file sizes
  - Safer (no arbitrary code execution)
  - Better interoperability with other tools

- **Replaced Scrapy with Selenium**
  - bb already had Selenium implementations for same data sources
  - Reduced dependency complexity

- **Implemented lazy API key loading**
  - Prevents import failures when API keys not needed
  - Using `APIKeyManager` with on-demand key retrieval

### Removed - Technical Debt Cleanup
- Dropped numba dependency (replaced with numpy vectorization)
- Dropped Scrapy dependency (replaced with existing Selenium code)
- Removed finbot.secrets.paths module (replaced with Dynaconf + path_constants)
- Removed backbetter repo (6 lines of dead scaffold code)

---

## Project Lineage

This repository was consolidated on 2026-02-09 from three pre-existing repositories representing the project's evolution. See [ADR-001](docs/adr/ADR-001-consolidate-three-repos.md) for the full decision record.

| Repository | Active Period | What It Contributed |
|---|---|---|
| **finbot** | 2021-2022 | Backtesting engine (Backtrader-based, 10 strategies), fund simulator, bond ladder simulator, Monte Carlo simulator, DCA optimizer, fund-specific simulations (16 funds) |
| **bb** | 2023-2024 | Modern infrastructure: Dynaconf configuration, queue-based async logging, API manager, 174-file utility library (data collection, finance, pandas, datetime, data science, plotting, request handling), constants system, environment-aware configuration |
| **backbetter** | 2022 | Scaffold only (6 LOC), fully superseded |

### Consolidation Timeline

- **2021-2022**: finbot original development (backtesting, simulation)
- **2022**: backbetter scaffold (abandoned)
- **2023-2024**: bb modern infrastructure rewrite
- **2026-02-09**: Repository consolidation (v0.1.0)
- **2026-02-10**: Bug fixes and architectural improvements (Priority 0 items)
- **2026-02-11**: Feature-complete v1.0.0 release (CLI, CI/CD, tests, docs)

### Version History Summary

| Version | Date | Description | Commits |
|---------|------|-------------|---------|
| 1.0.0 | 2026-02-11 | Feature-complete release with CLI, enhanced CI/CD, comprehensive tests, research docs | 8 |
| 0.1.0 | 2026-02-09 | Initial consolidation of three repositories into unified platform | 4 |

[Unreleased]: https://github.com/jerdaw/finbot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jerdaw/finbot/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/jerdaw/finbot/releases/tag/v0.1.0
