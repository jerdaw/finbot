# Changelog

All notable changes to Finbot are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For the full changelog, see [CHANGELOG.md](https://github.com/jerdaw/finbot/blob/main/CHANGELOG.md) in the repository.

## [1.0.0] - 2026-02-10

### Added
- CLI interface with 4 commands (simulate, backtest, optimize, update)
- Comprehensive test suite (80 tests, 444% increase)
- 5 example Jupyter notebooks
- 3 research documents (~50 pages)
- Documentation (README expansion, utils overview, ADRs)
- Performance benchmarks
- CI/CD pipeline with 8 checks
- Dependabot configuration
- Makefile with 14 targets
- Pre-commit hooks (17 total)

### Changed
- Consolidated dual config system to Dynaconf only
- Refactored fund simulations to data-driven config
- Updated ruff to v0.11.13 with expanded rules
- Modernized pyproject.toml to PEP 621

### Fixed
- Logger code duplication
- Import-time side effects in constants
- Dangerous error handling (bare except, assert)
- 103 lint violations → 0

## [0.1.0] - 2026-02-09

### Added
- Initial consolidated release
- Merged three repos (finbot, bb, backbetter)
- 10 backtesting strategies
- Fund, bond ladder, and Monte Carlo simulators
- 160+ utility functions
- Comprehensive data collection
- CI workflow

### Changed
- Replaced numba with vectorized NumPy
- Replaced pickle with parquet
- Lazy API key loading

## Project Lineage

Finbot consolidates work from three repositories:

- **finbot** (2021-2022): Original backtesting and simulation code
- **bb** (2023-2024): Data collection and utilities
- **backbetter** (2022): Enhanced backtesting features

See [ADR-001](https://github.com/jerdaw/finbot/blob/main/docs/adr/ADR-001-consolidate-three-repos.md) for consolidation rationale.
