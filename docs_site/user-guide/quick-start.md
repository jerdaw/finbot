# Quick Start

This guide provides a rapid walkthrough of Finbot's core features.

## 5-Minute Quick Start

### 1. Simulate a Fund

```bash
# Simulate UPRO (3x leveraged S&P 500)
finbot simulate --fund UPRO --start 2010-01-01 --plot
```

### 2. Backtest a Strategy

```bash
# Test 60/40 rebalancing strategy
finbot backtest --strategy Rebalance --asset SPY,TLT --plot
```

### 3. Optimize Allocation

```bash
# Find optimal SPY/TLT ratio
finbot optimize --method dca --assets SPY,TLT --plot
```

## Detailed Workflows

See [Getting Started](getting-started.md) for comprehensive documentation.
