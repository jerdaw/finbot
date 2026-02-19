# E6: NautilusTrader Setup Guide

**Created:** 2026-02-16
**Purpose:** Step-by-step guide for installing and configuring NautilusTrader

## Prerequisites

**Python Version:** NautilusTrader requires Python 3.12-3.14
- ✅ Finbot currently uses Python 3.13 → **Compatible!**

**System:** 64-bit Linux, macOS 15.0+, or Windows Server 2022+
- Officially supported on Ubuntu 22.04+

**Package Manager:** `uv` (already used by Finbot)

## Installation Steps

### 1. Install NautilusTrader

Add to `pyproject.toml` dependencies:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "nautilus-trader>=1.222.0",  # Latest version (Jan 2026)
]
```

Then install:

```bash
uv sync
```

**Alternative manual install:**
```bash
uv pip install nautilus_trader
```

### 2. Verify Installation

Create a test script to verify NautilusTrader is working:

```python
# test_nautilus_install.py
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader import __version__

print(f"NautilusTrader version: {__version__}")
print("✅ NautilusTrader installed successfully!")

# Try creating engine
engine = BacktestEngine()
print("✅ BacktestEngine instantiated successfully!")
```

Run:
```bash
uv run python test_nautilus_install.py
```

Expected output:
```
NautilusTrader version: 1.222.0 (or newer)
✅ NautilusTrader installed successfully!
✅ BacktestEngine instantiated successfully!
```

### 3. Optional: Install Visualization Extras

If you want to visualize backtest results:

```bash
uv pip install "nautilus_trader[visualization]"
```

## Architecture Overview

Based on documentation research, here's how Nautilus backtesting works:

### Two API Levels

**1. Low-Level API (BacktestEngine)**
- Direct component setup
- Manual data loading
- Best for single backtests
- Full control

**2. High-Level API (BacktestNode)**
- Configuration-driven
- Multiple backtest runs
- Production workflows
- Less boilerplate

**For our pilot:** Start with low-level API for simplicity

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    BacktestEngine                        │
│                                                          │
│  ┌────────────┐  ┌───────────┐  ┌──────────────┐       │
│  │   Cache    │  │  Message  │  │  Portfolio   │       │
│  │ (Instruments│  │    Bus    │  │  (Positions) │       │
│  │  & State)  │  │           │  │              │       │
│  └────────────┘  └───────────┘  └──────────────┘       │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              Data Engine                        │     │
│  │  (Feeds historical data to strategies)         │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │           Execution Engine                      │     │
│  │  (Simulates order fills, manages execution)    │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              Strategy                           │     │
│  │  (User-defined trading logic)                  │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Key Differences from Backtrader

| Aspect | Backtrader | NautilusTrader |
| --- | --- | --- |
| **Architecture** | Bar-based, synchronous | Event-driven, async |
| **Data Flow** | Cerebro iterates bars | Event stream processed |
| **Strategy API** | next(), buy(), sell() | on_data(), submit_order() |
| **Performance** | Python loop | Rust core with Python bindings |
| **Execution** | Simplified fills | Realistic fill simulation |
| **Learning Curve** | Gentle | Steeper |

### Data Format

Nautilus supports (in descending order of detail):
1. **Order Book Data** (L2/L3) - Full depth
2. **Quote Ticks** (L1) - Best bid/ask
3. **Trade Ticks** - Executed trades
4. **Bars** - OHLC aggregated

**For pilot:** Use bars (OHLC) - same as Backtrader

**Important:** Bar timestamps must be close time (not open time) to avoid look-ahead bias

### Fill Simulation

- **With bars:** Processes Open → High → Low → Close sequentially
- **Slippage:** Configurable with `prob_slippage` parameter
- **Limit orders:** `prob_fill_on_limit` simulates queue position

## Minimal Example

Based on Nautilus docs:

```python
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.identifiers import Venue

# Create engine
engine = BacktestEngine()

# Add venue
venue = Venue("SIM")
engine.add_venue(
    venue=venue,
    oms_type="NETTING",  # Order Management System type
    account_type="CASH",  # or "MARGIN" for leverage
    base_currency="USD",
    starting_balances={"USD": 100000},
)

# Add instrument
# (Would load from catalog or create manually)

# Add data
# engine.add_data(bars, sort=False)

# Sort data once after loading all instruments
# engine.sort_data()

# Add strategy
# engine.add_strategy(strategy)

# Run backtest
# engine.run()

# Get results
# (TBD - need to research result extraction)
```

## Next Steps for Implementation

### Phase 1: Basic Integration ✅ (This Guide)
- [x] Research Nautilus architecture
- [x] Understand installation requirements
- [x] Document key differences from Backtrader
- [x] Create setup guide

### Phase 2: Adapter Skeleton (Next)
- [ ] Create `finbot/adapters/nautilus/` directory
- [ ] Implement `NautilusAdapter` (BacktestEngine interface)
- [ ] Map Backtrader concepts → Nautilus concepts
- [ ] Handle data conversion (our format → Nautilus format)

### Phase 3: Strategy Adaptation
- [ ] Port Rebalance strategy to Nautilus
- [ ] Test with simple 2-asset portfolio
- [ ] Debug and iterate

### Phase 4: Evaluation
- [ ] Compare results to Backtrader
- [ ] Document findings
- [ ] Make go/no-go decision

## Resources

**Official Documentation:**
- Getting Started: https://nautilustrader.io/docs/latest/getting_started/
- Backtesting Concepts: https://nautilustrader.io/docs/latest/concepts/backtesting/
- Installation: https://nautilustrader.io/docs/latest/getting_started/installation/

**GitHub:**
- Repository: https://github.com/nautechsystems/nautilus_trader
- Latest Release: v1.222.0 (Jan 1, 2026)

**PyPI:**
- Package: https://pypi.org/project/nautilus_trader/

**Community:**
- Slack: (check GitHub for invite)
- GitHub Discussions: nautechsystems/nautilus_trader/discussions

## Troubleshooting

### Issue: Python version mismatch

**Solution:** Ensure Python 3.12-3.14. Check with:
```bash
python --version
```

### Issue: Installation fails on Windows

**Cause:** Missing C++ build tools

**Solution:** Install "Desktop development with C++" via Visual Studio Build Tools 2022

### Issue: Import errors after installation

**Cause:** Virtual environment not activated or wrong environment

**Solution:** Ensure `uv` environment is active:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

---

**Status:** Setup guide complete
**Next:** Create adapter skeleton in `finbot/adapters/nautilus/`
