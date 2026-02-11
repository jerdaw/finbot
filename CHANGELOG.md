# Changelog

All notable changes to this project will be documented in this file.

## Project Lineage

This repository was consolidated on 2026-02-09 from three pre-existing repositories representing the project's evolution. See [ADR-001](docs/adr/ADR-001-consolidate-three-repos.md) for the full decision record.

| Repository | Active Period | What It Contributed |
|---|---|---|
| **finbot** | 2021-2022 | Backtesting engine (Backtrader-based, 10 strategies), fund simulator, bond ladder simulator, Monte Carlo simulator, DCA optimizer, fund-specific simulations (16 funds) |
| **bb** | 2023-2024 | Modern infrastructure: Dynaconf configuration, queue-based async logging, API manager, 174-file utility library (data collection, finance, pandas, datetime, data science, plotting, request handling), constants system, environment-aware configuration |
| **backbetter** | 2022 | Scaffold only (6 LOC), fully superseded |

### Key changes made during consolidation

- Replaced numba JIT compilation with vectorized numpy (better Python 3.12+ compatibility, faster fund simulation)
- Replaced pickle serialization with parquet throughout (safer, faster, smaller, interoperable)
- Replaced hardcoded secret paths with Dynaconf + path_constants
- Dropped Scrapy dependency (bb's Selenium-based scrapers used instead)
- Dropped backbetter entirely
- Added lazy API key loading to prevent import failures
- Added numpy-financial for bond present value calculations (replaced custom numba PV function)
- Unified all imports under a single package structure

---

## [Unreleased]

### Added
- CHANGELOG.md documenting project lineage and history

## [0.1.0] - 2026-02-09

Initial consolidated release.

### Added
- Consolidated codebase from three repositories (finbot, bb, backbetter)
- Backtesting engine with 10 strategies (rebalance, buy-and-hold, SMA crossover variants, MACD variants, dip buying variants, SMA/rebalance mix)
- Fund simulator with realistic cost modeling (expense ratios, LIBOR borrowing, swap spreads)
- Bond ladder simulator with numpy-financial PV calculations
- Monte Carlo simulator with normal distribution support
- DCA optimizer with grid search and multiprocessing
- 16 fund-specific simulations (SPY, SSO, UPRO, QQQ, QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, 2x/3x short-term treasuries, NTSX)
- Index simulators for S&P 500 TR, Nasdaq 100 TR, ICE US Treasury indexes (1Y, 7Y, 20Y)
- Daily data update pipeline (Yahoo Finance, Google Finance, FRED, Shiller)
- Dynaconf-based environment configuration (development, production, staging, testing)
- Queue-based async logging with rotating file handlers
- API manager with lazy key loading (FRED, Alpha Vantage, NASDAQ Data Link, Google Finance, BLS)
- 174-file utility library (data collection, finance, pandas, datetime, data science, plotting, request handling)
- Constants system with auto-creating path management
- CI/CD with GitHub Actions (lint, format, test across Python 3.11-3.13)
- Pre-commit hooks (ruff, trailing whitespace, security checks)
- 18 unit tests (import smoke tests, simulation math correctness)
- Architectural decision record (ADR-001)
