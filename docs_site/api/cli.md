# CLI Reference

The Finbot CLI provides the current Click-based interface for simulations, backtesting, optimization, data refresh, status reporting, and dashboard launch.

## Overview

The current CLI provides:

- **6 main commands**: `simulate`, `backtest`, `optimize`, `update`, `status`, `dashboard`
- **Global runtime flags**: `--verbose`, `--trace-id`, `--disclaimer`, `--version`
- **Flat command structure**: no command subtrees under `simulate` or `optimize`
- **File output helpers**: save `.csv`, `.parquet`, or `.json` from commands that emit tables

If you are running from a source checkout without activating `.venv`, prepend examples with `uv run`, for example `DYNACONF_ENV=development uv run finbot --help`.

## Installation

The core CLI is installed with the main package:

```bash
uv sync
```

Optional surfaces use extras:

```bash
uv sync --extra dashboard  # required for `finbot dashboard`
uv sync --extra web        # backend/API support
```

## Global Options

```bash
DYNACONF_ENV=development finbot --help
DYNACONF_ENV=development finbot --version
```

Available global options:

- `--verbose`, `-v`: enable verbose logging
- `--trace-id TEXT`: attach a trace ID to audit logs
- `--disclaimer`: print the full disclaimer and exit
- `--version`: show the CLI version

`--verbose` is global and must appear before the command, for example `finbot --verbose status`.

## Commands

### CLI Module

Main CLI entry point and command definitions:

::: finbot.cli.main
options:
show_root_heading: true
show_source: true
heading_level: 3

## Command Reference

### 1. simulate

Run a simulation from the built-in fund registry.

```bash
finbot simulate --fund FUND [OPTIONS]
```

**Options:**

- `--fund TEXT` required: fund ticker such as `UPRO`, `TQQQ`, `TMF`, or `SPY`
- `--start DATE`: inclusive start date in `YYYY-MM-DD`
- `--end DATE`: inclusive end date in `YYYY-MM-DD`
- `--output PATH`: save the DataFrame as `.csv`, `.parquet`, or `.json`
- `--plot`: display the Plotly line chart

**Examples:**

```bash
finbot simulate --fund UPRO
finbot simulate --fund TQQQ --start 2020-01-01 --end 2024-01-01
finbot simulate --fund TMF --output tmf.parquet --plot
```

### 2. backtest

Run a strategy backtest for one asset.

```bash
finbot backtest --strategy STRATEGY --asset ASSET [OPTIONS]
```

**Options:**

- `--strategy TEXT` required: one of `Rebalance`, `NoRebalance`, `SMACrossover`, `SMACrossoverDouble`, `SMACrossoverTriple`, `MACDSingle`, `MACDDual`, `DipBuySMA`, `DipBuyStdev`, `SMARebalMix`, `DualMomentum`, `RiskParity`
- `--asset TEXT` required: single asset ticker such as `SPY` or `QQQ`
- `--start DATE`: inclusive start date in `YYYY-MM-DD`
- `--end DATE`: inclusive end date in `YYYY-MM-DD`
- `--cash FLOAT`: starting cash, default `100000`
- `--output PATH`: save the one-row metrics DataFrame
- `--plot`: display the Backtrader plot

**Examples:**

```bash
finbot backtest --strategy NoRebalance --asset SPY
finbot backtest --strategy SMACrossover --asset QQQ --cash 50000 --plot
finbot backtest --strategy MACDDual --asset SPY --output backtest.parquet
```

The service layer contains `RegimeAdaptive`, but the current CLI does not expose it.

### 3. optimize

Run the built-in DCA optimizer sweep for one asset.

```bash
finbot optimize --method dca --asset ASSET [OPTIONS]
```

**Options:**

- `--method TEXT` required: currently only `dca`
- `--asset TEXT` required: single asset ticker
- `--cash FLOAT`: starting cash, default `1000`
- `--output PATH`: save the raw trial table
- `--plot`: display the ratio and duration charts

The CLI uses the package defaults for front-loading ratios, DCA durations, purchase intervals, and trial durations. Use the Python API when you need to override those ranges.

**Examples:**

```bash
finbot optimize --method dca --asset SPY
finbot optimize --method dca --asset QQQ --cash 5000 --plot
finbot optimize --method dca --asset UPRO --output dca.parquet
```

### 4. update

Run the daily data update pipeline.

```bash
finbot update [OPTIONS]
```

**Options:**

- `--dry-run`: print the update plan without making changes
- `--skip-prices`: skip price and economic data updates
- `--skip-simulations`: skip LIBOR approximation and simulation regeneration

**Examples:**

```bash
finbot update
finbot update --dry-run
finbot update --skip-simulations
```

### 5. status

Check data freshness and pipeline health.

```bash
finbot status [OPTIONS]
```

**Options:**

- `--stale-only`: show only stale data sources

Use `finbot --verbose status` when you also want the per-source staleness thresholds printed.

**Examples:**

```bash
finbot status
finbot status --stale-only
finbot --verbose status
```

### 6. dashboard

Launch the Streamlit dashboard.

```bash
finbot dashboard [OPTIONS]
```

**Options:**

- `--port INTEGER`: port to bind, default `8501`
- `--host TEXT`: host to bind, default `localhost`

**Examples:**

```bash
finbot dashboard
finbot dashboard --port 8080
finbot dashboard --host 0.0.0.0 --port 8501
```

## Workflows

### Daily Refresh Workflow

```bash
finbot status --stale-only
finbot update
finbot --verbose status
```

### Basic Research Workflow

```bash
finbot simulate --fund UPRO --output upro.parquet
finbot backtest --strategy NoRebalance --asset SPY --output spy_backtest.parquet
finbot optimize --method dca --asset SPY --output spy_dca.parquet
```

## Environment Variables

Set `DYNACONF_ENV` explicitly and export any required data-source credentials in the shell. For local development, you can also place them in `finbot/config/.env`, which is auto-loaded in `development` mode.

```bash
export DYNACONF_ENV=development
export ALPHA_VANTAGE_API_KEY=your_key
export NASDAQ_DATA_LINK_API_KEY=your_key
export US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

## Testing

CLI smoke coverage lives in the Python test suite:

```bash
uv run pytest tests/unit/test_imports.py::test_cli_import -v
```

## See Also

- [User Guide: Quick Start](../user-guide/quick-start.md) - CLI walkthrough
- [Configuration](../user-guide/configuration.md) - Environment setup
- [Data Quality](../user-guide/data-quality-guide.md) - Status monitoring
- [BacktestRunner](services/backtesting/backtest-runner.md) - Python backtest API
- [DCA Optimizer](services/optimization/dca-optimizer.md) - Python optimizer API
