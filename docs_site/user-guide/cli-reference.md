# CLI Reference

Complete command-line interface documentation for the current Finbot Click CLI.

If you are running from a source checkout without activating `.venv`, prefix commands with `uv run`, for example `uv run finbot --help`.

## Global Options

```bash
finbot [OPTIONS] COMMAND [ARGS]...
```

**Global options:**

- `--version`: Show version and exit
- `--verbose`, `-v`: Enable verbose logging output
- `--trace-id TEXT`: Attach a trace ID to audit logs
- `--disclaimer`: Print the full disclaimer and exit

`--verbose` is a global option, so it must appear before the subcommand: `finbot --verbose status`.

## Commands

### finbot simulate

Run a fund simulation from the built-in fund registry.

```bash
finbot simulate --fund FUND_TICKER [OPTIONS]
```

**Required:**

- `--fund TEXT`: Fund ticker such as `UPRO`, `TQQQ`, `TMF`, or `SPY`

**Optional:**

- `--start TEXT`: Start date in `YYYY-MM-DD` format
- `--end TEXT`: End date in `YYYY-MM-DD` format
- `--output PATH`: Save results as `.csv`, `.parquet`, or `.json`
- `--plot`: Show the interactive Plotly chart

**Examples:**

```bash
finbot simulate --fund UPRO
finbot simulate --fund TQQQ --start 2020-01-01 --end 2024-01-01
finbot simulate --fund TMF --output results/tmf.parquet --plot
```

### finbot backtest

Run a strategy backtest for a single asset.

```bash
finbot backtest --strategy STRATEGY --asset ASSET [OPTIONS]
```

**Required:**

- `--strategy TEXT`: One of `Rebalance`, `NoRebalance`, `SMACrossover`, `SMACrossoverDouble`, `SMACrossoverTriple`, `MACDSingle`, `MACDDual`, `DipBuySMA`, `DipBuyStdev`, `SMARebalMix`, `DualMomentum`, `RiskParity`
- `--asset TEXT`: Single asset ticker such as `SPY` or `QQQ`

**Optional:**

- `--start TEXT`: Start date in `YYYY-MM-DD` format
- `--end TEXT`: End date in `YYYY-MM-DD` format
- `--cash FLOAT`: Starting cash, default `100000`
- `--output PATH`: Save the one-row metrics table as `.csv`, `.parquet`, or `.json`
- `--plot`: Show the Backtrader plot

**Examples:**

```bash
finbot backtest --strategy NoRebalance --asset SPY
finbot backtest --strategy SMACrossover --asset QQQ --cash 50000 --plot
finbot backtest --strategy MACDDual --asset SPY --output results/backtest.parquet
```

`RegimeAdaptive` exists in the service layer but is not exposed by the current CLI command.

### finbot optimize

Run the built-in DCA schedule optimizer for one asset.

```bash
finbot optimize --method dca --asset ASSET [OPTIONS]
```

**Required:**

- `--method TEXT`: Currently only `dca`
- `--asset TEXT`: Single asset ticker such as `SPY`, `QQQ`, or `UPRO`

**Optional:**

- `--cash FLOAT`: Starting cash, default `1000`
- `--output PATH`: Save the raw per-trial results table as `.csv`, `.parquet`, or `.json`
- `--plot`: Show the ratio and duration charts

The current CLI runs the built-in sweep of front-loading ratios, DCA durations, purchase intervals, and trial durations. Use the Python API if you need to override those ranges directly.

**Examples:**

```bash
finbot optimize --method dca --asset SPY
finbot optimize --method dca --asset QQQ --cash 5000 --plot
finbot optimize --method dca --asset UPRO --output results/dca.parquet
```

### finbot update

Run the daily data update pipeline.

```bash
finbot update [OPTIONS]
```

**Optional:**

- `--dry-run`: Show what would run without making changes
- `--skip-prices`: Skip price and economic data updates
- `--skip-simulations`: Skip LIBOR approximation and simulation regeneration

**Examples:**

```bash
finbot update
finbot update --dry-run
finbot update --skip-simulations
```

### finbot status

Show data freshness and pipeline health.

```bash
finbot status [OPTIONS]
```

**Optional:**

- `--stale-only`: Show only stale data sources

Use `finbot --verbose status` when you want the staleness thresholds printed after the table.

**Examples:**

```bash
finbot status
finbot status --stale-only
finbot --verbose status
```

### finbot dashboard

Launch the Streamlit dashboard.

```bash
finbot dashboard [OPTIONS]
```

**Optional:**

- `--port INTEGER`: Port to bind, default `8501`
- `--host TEXT`: Host to bind, default `localhost`

**Examples:**

```bash
finbot dashboard
finbot dashboard --port 8080
finbot dashboard --host 0.0.0.0 --port 8501
```

## Output Formats

Command outputs are saved based on file extension:

- `.csv`: Comma-separated values
- `.parquet`: Apache Parquet
- `.json`: JSON serialization

## See Also

- [Getting Started](getting-started.md) - Installation and setup
- [Configuration](configuration.md) - Environment and secret management
- [API Reference](../api/index.md) - Python API documentation
