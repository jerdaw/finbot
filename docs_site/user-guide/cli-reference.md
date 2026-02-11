# CLI Reference

Complete command-line interface documentation for Finbot.

## Global Options

```bash
finbot [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--version`: Show version and exit
- `--verbose`, `-v`: Enable verbose output
- `--help`: Show help message

## Commands

### finbot simulate

Simulate leveraged funds:

```bash
finbot simulate --fund FUND_TICKER [OPTIONS]
```

**Required:**
- `--fund TEXT`: Fund ticker (SPY, UPRO, TQQQ, etc.)

**Optional:**
- `--start TEXT`: Start date (YYYY-MM-DD)
- `--end TEXT`: End date (YYYY-MM-DD)
- `--output PATH`: Save results (CSV, parquet, JSON)
- `--plot`: Show interactive plot

**Examples:**

```bash
# Basic simulation
finbot simulate --fund UPRO

# Historical extension
finbot simulate --fund TQQQ --start 1990-01-01 --end 2024-01-01

# Save and plot
finbot simulate --fund TMF --output results/tmf.parquet --plot
```

### finbot backtest

Run strategy backtests:

```bash
finbot backtest --strategy STRATEGY --asset ASSETS [OPTIONS]
```

**Required:**
- `--strategy TEXT`: Strategy name (Rebalance, SMACrossover, etc.)
- `--asset TEXT`: Comma-separated tickers (SPY,TLT)

**Optional:**
- `--start TEXT`: Start date
- `--end TEXT`: End date
- `--cash FLOAT`: Starting cash (default: 100000)
- `--commission FLOAT`: Commission rate (default: 0.001)
- `--output PATH`: Save results
- `--plot`: Show portfolio value chart

**Examples:**

```bash
# 60/40 portfolio
finbot backtest --strategy Rebalance --asset SPY,TLT

# Custom parameters
finbot backtest --strategy SMACrossover --asset QQQ \
  --start 2010-01-01 --cash 50000 --commission 0.0005 --plot
```

### finbot optimize

Portfolio optimization:

```bash
finbot optimize --method METHOD --assets ASSETS [OPTIONS]
```

**Required:**
- `--method TEXT`: Optimization method (dca)
- `--assets TEXT`: Comma-separated tickers

**Optional:**
- `--duration INTEGER`: DCA duration in days
- `--interval INTEGER`: Purchase interval in days
- `--ratios TEXT`: Ratio range (start,stop,num)
- `--output PATH`: Save results
- `--plot`: Show optimization charts

**Examples:**

```bash
# Default optimization
finbot optimize --method dca --assets SPY,TLT

# Custom parameters
finbot optimize --method dca --assets UPRO,TMF \
  --duration 1095 --interval 30 --ratios 0.3,0.7,9 --plot
```

### finbot update

Update all data:

```bash
finbot update [OPTIONS]
```

**Optional:**
- `--dry-run`: Show what would be updated
- `--skip-prices`: Skip price history updates
- `--skip-simulations`: Skip simulation updates

**Examples:**

```bash
# Full update
finbot update

# Dry run (no changes)
finbot update --dry-run

# Update prices only
finbot update --skip-simulations
```

## Output Formats

Specify output format via file extension:

- `.csv`: Comma-separated values
- `.parquet`: Apache Parquet (recommended)
- `.json`: JSON format

## See Also

- [Getting Started](getting-started.md) - Installation and setup
- [Configuration](configuration.md) - Advanced settings
- [API Reference](../api/index.md) - Python API documentation
