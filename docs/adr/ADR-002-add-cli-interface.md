# ADR-002: Add CLI Interface

### Status

Accepted (Implemented 2026-02-10)

### Context

The project existed as a Python library requiring programmatic usage through imports and function calls. While this provides maximum flexibility for advanced users, it created barriers for:

1. **Quick exploration**: Testing strategies or running simulations required writing Python scripts
2. **Daily operations**: Running the update pipeline needed `python scripts/update_daily.py`
3. **Discoverability**: Users had to read source code to understand available functions
4. **Accessibility**: Non-programmers or casual users couldn't easily experiment
5. **Automation**: Scheduled tasks required shell scripts wrapping Python

**User feedback patterns** (hypothetical, based on common library-to-CLI migration motivations):
- "How do I just run a backtest without writing code?"
- "What parameters does the fund simulator accept?"
- "Can I save simulation results to CSV?"
- "How do I visualize backtest results without Jupyter?"

### Decision

Add a comprehensive CLI using the Click framework with four main commands:

| Command | Purpose | Key Options |
| --- | --- | --- |
| `finbot simulate` | Run fund simulations | `--fund`, `--start`, `--end`, `--output`, `--plot` |
| `finbot backtest` | Run strategy backtests | `--strategy`, `--asset`, `--cash`, `--commission`, `--output`, `--plot` |
| `finbot optimize` | Run portfolio optimization | `--method`, `--assets`, `--duration`, `--interval`, `--ratios`, `--output`, `--plot` |
| `finbot update` | Run daily data pipeline | `--dry-run`, `--skip-prices`, `--skip-simulations` |

### Rationale

#### Framework Selection: Click vs Alternatives

| Framework | Pros | Cons | Decision |
| --- | --- | --- | --- |
| **Click** | Decorator-based, excellent docs, subcommands, auto-help | Learning curve | ✅ **Selected** |
| Typer | Type-hint based, modern, auto-validation | Less mature, smaller ecosystem | ❌ Considered |
| argparse | Stdlib, no dependencies | Verbose, poor subcommand support | ❌ Rejected |
| fire | Zero boilerplate | Magic behavior, hard to test | ❌ Rejected |

**Click chosen for**:
- Mature ecosystem with excellent documentation
- First-class subcommand support (perfect for our use case)
- Decorator pattern aligns with our existing code style
- Wide adoption (Flask, pandas, etc.)
- Already a transitive dependency (via other packages)

#### Design Principles

1. **Mirror library API**: CLI options match function parameters where possible
2. **Sensible defaults**: Most parameters optional, useful defaults provided
3. **Output flexibility**: Support CSV, parquet, and JSON export formats
4. **Visual feedback**: Optional plotly visualizations via `--plot` flag
5. **Help-first**: Comprehensive `--help` for each command with examples
6. **Fail-fast**: Clear error messages with suggestions

### Implementation

#### Package Structure

```
finbot/cli/
├── __init__.py              # Package initialization
├── main.py                  # Main CLI group and entry point
├── commands/
│   ├── __init__.py          # Command exports
│   ├── simulate.py          # Fund simulation command
│   ├── backtest.py          # Strategy backtest command
│   ├── optimize.py          # Portfolio optimization command
│   └── update.py            # Daily data update command
└── utils/
    ├── __init__.py          # Utils exports
    └── output.py            # Output saving utilities (CSV/parquet/JSON)
```

#### Package Entry Point

Added to `pyproject.toml`:

```toml
[project.scripts]
finbot = "finbot.cli.main:cli"
```

This registers `finbot` as a command-line executable when the package is installed.

**Note:** Originally implemented with Poetry `[tool.poetry.scripts]` in 2026-02-10, migrated to PEP 621 `[project.scripts]` with uv adoption in 2026-02-11.

#### Example Commands

```bash
# Simulate UPRO from 2010
finbot simulate --fund UPRO --start 2010-01-01 --output upro.csv --plot

# Backtest rebalancing strategy
finbot backtest --strategy Rebalance --asset SPY --asset TLT --cash 100000 --plot

# Optimize DCA portfolio
finbot optimize --method dca --assets SPY --assets TQQQ --duration 252 --plot

# Run daily update
finbot update --dry-run
```

#### Global Options

- `--verbose` / `-v`: Enable debug logging
- `--version`: Show version and exit
- `--help`: Show help message and exit

### Consequences

#### Positive

| Impact | Benefit |
| --- | --- |
| **Accessibility** | Non-programmers can use the platform through terminal commands |
| **Discoverability** | `finbot --help` reveals all capabilities without reading code |
| **Automation** | Easier to schedule tasks via cron or systemd timers |
| **Quick iteration** | Test ideas without writing Python scripts |
| **Data export** | Built-in CSV/parquet/JSON export for external tools |
| **Visualization** | Instant plotly charts with `--plot` flag |
| **Professional image** | Complete tools ship with CLIs, not just libraries |

#### Neutral

| Impact | Note |
| --- | --- |
| **Code duplication** | CLI wraps library functions (acceptable for user experience) |
| **Maintenance burden** | Need to keep CLI in sync with library API changes |
| **Testing complexity** | CLI integration tests needed alongside unit tests |

#### Negative

| Impact | Mitigation |
| --- | --- |
| **Learning curve** | Comprehensive `--help` and examples mitigate this |
| **Limited flexibility** | Advanced users still have full library access |
| **Output parsing** | Users may want structured output (JSON format available) |

### Alternatives Considered

#### 1. No CLI (library-only)

**Pros**: Simpler codebase, maximum flexibility
**Cons**: Poor accessibility, requires Python knowledge
**Verdict**: ❌ Rejected - accessibility is important

#### 2. Jupyter-only interface

**Pros**: Rich visualizations, exploratory workflow
**Cons**: Not suitable for automation, requires Jupyter setup
**Verdict**: ❌ Rejected - CLIs are better for automation

#### 3. Web dashboard (Streamlit/Dash)

**Pros**: Best user experience, no terminal knowledge needed
**Cons**: Complex setup, requires server, out of scope
**Verdict**: ⏸️ Deferred - could be added later (see Priority 4.2)

#### 4. Single-command interface (like `git`)

**Pros**: Simpler entry point
**Cons**: Subcommands provide better organization for our use case
**Verdict**: ❌ Rejected - we have 4 distinct operations

### Future Enhancements

- [ ] Add `finbot init` to create config template
- [ ] Add `finbot list` to show available funds/strategies
- [ ] Add `finbot validate` to check data integrity
- [ ] Add progress bars for long-running operations (tqdm)
- [ ] Add `--config` flag to load settings from file
- [ ] Add shell completion (bash/zsh/fish)
- [ ] Add `finbot clean` to remove cache files

### Related

- **Implementation**: Priority 2.1 (Add CLI Interface) - Completed 2026-02-10
- **Testing**: 80 tests pass including CLI smoke tests
- **Documentation**: CLI usage in README.md, example commands in notebooks
- **Dependencies**: Added `click` as explicit dependency (was transitive)

### References

- [Click Documentation](https://click.palletsprojects.com/)
- [Keep a Changelog - CLI conventions](https://keepachangelog.com/)
- [12 Factor App - Admin processes](https://12factor.net/admin-processes)
