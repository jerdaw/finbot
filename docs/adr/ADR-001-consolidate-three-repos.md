# ADR-001: Consolidate Three Repos into One

### Status

Accepted

### Context

The project existed across three separate repositories representing its evolution:

- **finbot** (2021-2022): Working backtesting and simulation engine, but dated architecture with pickle I/O, numba JIT compilation, and hardcoded secret paths.
- **bb** (2023-2024): Modern rewrite with Dynaconf configuration, queue-based logging, API management, and 174-file utility library. Missing backtesting and simulation.
- **backbetter** (2022): Dead scaffold with 6 lines of code.

Maintaining three repos with overlapping concerns created confusion about which code was canonical and prevented using the modern infrastructure with the working simulation/backtesting code.

### Decision

Consolidate into a single repository using bb's infrastructure as the foundation and porting finbot's backtesting/simulation code on top of it. Key sub-decisions:

| Choice | Alternative Considered | Rationale |
| --- | --- | --- |
| Drop numba, use vectorized numpy + numpy-financial | Keep numba | numba has poor Python 3.12+ support and adds build complexity. Vectorized numpy is faster for the fund simulator case. |
| Drop Scrapy | Keep Scrapy for web scraping | bb already uses Selenium for the same data sources. |
| Keep quantstats | Rewrite metrics | quantstats provides comprehensive backtest analytics that would take significant effort to replicate. |
| Replace pickle with parquet | Keep pickle | Parquet is faster, smaller, interoperable, and doesn't have arbitrary code execution risks. |
| Replace finbot.secrets.paths with Dynaconf + path_constants | Keep secrets module | Dynaconf is more flexible, supports multiple environments, and is the bb standard. |
| Lazy API key loading | Eager loading (bb original) | Prevents import failures when API keys aren't needed for a given operation. |

### Consequences

| Impact | Category |
| --- | --- |
| Single source of truth for all financial tooling | Positive |
| Modern config/logging/API infrastructure for simulation and backtesting | Positive |
| Bond ladder simulator no longer requires C compiler (no numba) | Positive |
| Fund simulator is faster (numpy vectorization vs numba loop) | Positive |
| All data serialization uses parquet (safer, faster, smaller) | Positive |
| One-time migration effort to port and verify 25+ simulation files | Neutral |
| backbetter repo is now fully obsolete | Neutral |
