# Priority 4.2: Add a Streamlit Web Dashboard

## Context

All Priority 0-3 roadmap items are complete. The project has comprehensive services (simulation, backtesting, optimization, Monte Carlo, data quality) exposed only through a CLI and Python API. A web dashboard makes these capabilities accessible through an interactive UI, showcasing the platform visually. Streamlit is the natural choice: minimal code, native plotly/pandas support, built-in caching, and perfect for data-focused apps.

## File Structure

```
finbot/dashboard/
    __init__.py
    app.py                       # Main entry point + home page
    pages/
        __init__.py
        1_simulations.py         # Fund simulation explorer
        2_backtesting.py         # Strategy backtester
        3_optimizer.py           # DCA optimizer
        4_monte_carlo.py         # Monte Carlo simulator
        5_data_status.py         # Data freshness dashboard
    components/
        __init__.py
        charts.py                # Reusable plotly chart builders
        sidebar.py               # Common sidebar widgets
finbot/cli/commands/dashboard.py # CLI command: finbot dashboard
```

## Pages

### Home (`app.py`)
- `st.set_page_config(page_title="Finbot Dashboard", layout="wide")`
- Project title, brief description, quick links to each page
- Summary data status (fresh/stale count) from `check_all_freshness()`

### Page 1: Simulations
- **Sidebar**: Multi-select fund tickers from `FUND_CONFIGS.keys()`, date range, normalize toggle
- **Content**: Price chart (plotly line, optionally normalized to $1), summary metrics table (total return, CAGR, volatility, max drawdown), daily returns histogram
- **Data**: `simulate_fund(ticker, save_sim=False)` cached with `@st.cache_data(ttl=3600)`

### Page 2: Backtesting
- **Sidebar**: Asset ticker, strategy select (all 10), conditional strategy params (MA periods, intervals, etc.), initial cash, date range, run button
- **Content**: Metric cards (CAGR, Sharpe, Max DD, ROI), full stats table, portfolio value chart, drawdown chart
- **Data**: `get_history()` cached; backtest runs on button click, results stored in `st.session_state`
- **Requires**: Add `get_value_history() -> pd.DataFrame` method to `BacktestRunner` (returns Value+Cash time series that `get_test_stats()` already builds internally at line 102)

### Page 3: DCA Optimizer
- **Sidebar**: Asset ticker, starting cash, ratio subset, trial durations, run button
- **Content**: Ratio analysis bar chart, duration analysis bar chart, Sharpe heatmap, raw results table
- **Data**: `dca_optimizer(save_df=False, analyze_results=False)` + `analyze_results_helper(plot=False)`, button-triggered with `st.spinner()`

### Page 4: Monte Carlo
- **Sidebar**: Asset ticker, sim periods (default 252), num sims (default 1000, max 50000), start price, run button
- **Content**: Fan chart (all paths + median/5th/95th percentiles), final value histogram, summary stats (median, mean, VaR, P(loss))
- **Data**: `monte_carlo_simulator()` button-triggered

### Page 5: Data Status
- **No sidebar controls** (informational only)
- **Content**: Summary metrics (total files, total size, fresh/stale counts), status table with color coding, staleness bar chart, storage pie chart
- **Data**: `check_all_freshness()` cached with `@st.cache_data(ttl=300)`

## Shared Components

### `components/charts.py`
Reusable functions returning `go.Figure` objects:
- `create_time_series_chart(data: dict[str, pd.Series], title, normalize=False)`
- `create_histogram_chart(data: dict[str, pd.Series], title, bins=50)`
- `create_bar_chart(df, x_col, y_cols, title)`
- `create_heatmap(df, title)`
- `create_fan_chart(trials_df, title)`

### `components/sidebar.py`
- `fund_selector(default) -> list[str]` — multi-select from FUND_CONFIGS
- `asset_selector() -> str` — single asset with common presets + custom input
- `date_range_selector() -> tuple[date, date]`

## Key Modifications to Existing Files

| File | Change |
|------|--------|
| `pyproject.toml` | Add `"streamlit>=1.40,<2"` to dependencies |
| `finbot/services/backtesting/backtest_runner.py` | Add `get_value_history() -> pd.DataFrame` public method (extracts existing logic from `get_test_stats()` lines 100-104) |
| `finbot/cli/commands/__init__.py` | Add `dashboard` import |
| `finbot/cli/main.py` | Add `cli.add_command(dashboard)` and update help text |
| `Makefile` | Add `dashboard` and `dashboard-dev` targets |
| `docker-compose.yml` | Add `finbot-dashboard` service on port 8501 |
| `docs/planning/roadmap.md` | Mark 4.2 complete |

## CLI Command (`finbot/cli/commands/dashboard.py`)

Launches Streamlit via `subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, ...])`.
Options: `--port` (default 8501), `--host` (default localhost).

## Caching Strategy

| Data | Method | TTL |
|------|--------|-----|
| Fund simulations | `@st.cache_data` | 1h |
| Price history | `@st.cache_data` | 1h |
| Data freshness | `@st.cache_data` | 5min |
| Backtest/DCA/Monte Carlo results | `st.session_state` | Per-session (button-triggered) |

## Implementation Order

1. Add streamlit dependency, `uv sync`
2. Create `finbot/dashboard/` package with `app.py` (home page)
3. Add CLI command + Makefile targets
4. Create `components/charts.py` and `components/sidebar.py`
5. Page 5 (Data Status) — simplest, validates infrastructure
6. Page 1 (Simulations) — core visualization
7. Add `get_value_history()` to BacktestRunner
8. Page 2 (Backtesting) — most complex
9. Page 3 (DCA Optimizer)
10. Page 4 (Monte Carlo)
11. Docker service, tests, roadmap update

## Testing

- Import smoke tests for dashboard modules (add to `tests/unit/test_imports.py`)
- Unit tests for `components/charts.py` (returns `go.Figure`, testable without Streamlit)
- CLI command registration test
- Manual verification: `finbot dashboard` starts, all 5 pages render without errors

## Verification

```bash
uv sync                          # Install streamlit
finbot dashboard                 # Starts at localhost:8501
# Navigate each page, verify charts render
DYNACONF_ENV=development uv run pytest tests/ -q  # All tests pass
uv run mypy finbot/dashboard/    # No type errors
uv run ruff check finbot/dashboard/  # No lint errors
```
