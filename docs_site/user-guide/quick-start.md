# Quick Start

This guide provides a rapid walkthrough of Finbot's core features.

## 5-Minute Quick Start

### 1. Simulate a Fund

```bash
# Simulate UPRO (3x leveraged S&P 500)
uv run finbot simulate --fund UPRO --start 2010-01-01 --plot
```

### 2. Backtest a Strategy

```bash
# Test a single-asset strategy with the current CLI
uv run finbot backtest --strategy NoRebalance --asset SPY --plot
```

### 3. Optimize Allocation

```bash
# Find an optimal DCA schedule for one asset
uv run finbot optimize --method dca --asset SPY --plot
```

## Detailed Workflows

See [Getting Started](getting-started.md) for comprehensive documentation.
