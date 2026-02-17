# E6-T1 Implementation Guide: Next Steps

**Created:** 2026-02-16
**Status:** Adapter skeleton created, implementation requires manual work
**Current Phase:** E6-T1 Phase 2 - Adapter Implementation

## What I've Done

✅ **Phase 1 Complete:**
- [x] Researched NautilusTrader architecture and capabilities
- [x] Created installation guide (`e6-nautilus-setup-guide.md`)
- [x] Created implementation plan (`e6-nautilus-pilot-implementation-plan.md`)
- [x] Created adapter skeleton (`finbot/adapters/nautilus/`)

**Files Created:**
- `docs/planning/e6-nautilus-pilot-implementation-plan.md` (comprehensive plan)
- `docs/planning/e6-nautilus-setup-guide.md` (installation & architecture overview)
- `finbot/adapters/nautilus/__init__.py` (module init)
- `finbot/adapters/nautilus/nautilus_adapter.py` (skeleton with TODOs)

## What You Need to Do

I cannot complete the NautilusTrader integration autonomously because I cannot:
1. Install packages on your system
2. Run and test the code
3. Debug integration errors
4. Verify results match expectations

Here's your implementation roadmap:

---

## Step 1: Install NautilusTrader

### Add to pyproject.toml

Edit `/home/jer/localsync/finbot/pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "nautilus-trader>=1.222.0",
]
```

### Install

```bash
cd /home/jer/localsync/finbot
uv sync
```

### Verify

```bash
uv run python -c "import nautilus_trader; print(nautilus_trader.__version__)"
```

Expected: `1.222.0` or newer

---

## Step 2: Study Nautilus Examples

Before implementing the adapter, familiarize yourself with Nautilus:

### Create a learning script

```bash
mkdir -p /home/jer/localsync/finbot/scratch/
```

Create `scratch/nautilus_hello_world.py`:

```python
"""Minimal Nautilus example to understand the basics."""

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.identifiers import Venue

# Create engine
engine = BacktestEngine()
print("✅ BacktestEngine created")

# Add venue
venue = Venue("SIM")
engine.add_venue(
    venue=venue,
    oms_type="NETTING",
    account_type="CASH",
    base_currency="USD",
    starting_balances={"USD": 100000},
)
print("✅ Venue configured")

# TODO: Add instrument
# TODO: Add data
# TODO: Add strategy
# TODO: Run engine

print("\n🎯 Next: Learn how to add instruments and data")
print("See: https://nautilustrader.io/docs/latest/getting_started/backtest_low_level/")
```

Run:
```bash
uv run python scratch/nautilus_hello_world.py
```

### Work through Nautilus tutorials

1. **Backtest Low-Level Tutorial**
   - URL: https://nautilustrader.io/docs/latest/getting_started/backtest_low_level/
   - Learn: How to add instruments, data, and strategies
   - Time: 1-2 hours

2. **Strategy Tutorial**
   - Learn how Nautilus strategies work (event-driven)
   - Compare to Backtrader (bar-based)
   - Time: 1-2 hours

---

## Step 3: Implement Data Conversion

The hardest part is converting our pandas DataFrames to Nautilus bar objects.

### Key Challenge

Our data format:
```python
# DataFrame with DatetimeIndex
#            Open    High     Low   Close  Volume
# 2020-01-02  100.0   102.0   99.0  101.0  1000000
# 2020-01-03  101.0   103.0  100.0  102.0  1100000
```

Nautilus format:
```python
# Bar objects with specific structure
# - InstrumentId
# - BarType (time aggregation)
# - Timestamps (ts_init = close time)
# - OHLCV as price/quantity types
```

### Implementation Task

Edit `finbot/adapters/nautilus/nautilus_adapter.py`:

Find method `_convert_dataframe_to_bars()` and implement it:

```python
def _convert_dataframe_to_bars(self, symbol: str, df: pd.DataFrame):
    """Convert pandas DataFrame to Nautilus bar objects."""
    from nautilus_trader.model.data import Bar
    from nautilus_trader.model.identifiers import InstrumentId
    # ... implement conversion ...
    # Hint: Nautilus has utilities for this, check docs
```

**Resources:**
- Nautilus data models: https://nautilustrader.io/docs/latest/api_reference/model/
- Bar class documentation

**Time Estimate:** 2-4 hours (including trial and error)

---

## Step 4: Implement Minimal Adapter

Work through each TODO in `nautilus_adapter.py`:

### Priority Order

1. **`_create_engine()`** - Easiest, just instantiate BacktestEngine
2. **`_configure_venue()`** - Add venue with our settings
3. **`_load_data()`** - Use your data conversion function
4. **`_validate_request()`** - Basic checks
5. **`_add_strategy()`** - Hardest, requires strategy adaptation
6. **`_run_engine()`** - Call engine.run()
7. **`_extract_results()`** - Map Nautilus results to our contracts

### Start Simple

For the pilot, you can skip strategy adaptation entirely:

```python
def _add_strategy(self, engine, request):
    """Add strategy - PILOT: Use simple Nautilus built-in."""
    # Instead of adapting our strategy, use a Nautilus example strategy
    # This proves the adapter works without the complexity of strategy conversion
    from nautilus_trader.examples.strategies.ema_cross import EMACross

    # Use a simple EMA crossover strategy from Nautilus examples
    strategy = EMACross(...)
    engine.add_strategy(strategy)
```

This way you can get the adapter working without solving the strategy adaptation problem.

---

## Step 5: Create Test Script

Create `scripts/test_nautilus_adapter.py`:

```python
"""Test NautilusAdapter with minimal data."""

from decimal import Decimal
from datetime import datetime
import pandas as pd

from finbot.adapters.nautilus import NautilusAdapter
from finbot.core.contracts.models import BacktestRunRequest

# Create minimal test data
spy_data = pd.DataFrame({
    "Open": [100.0, 101.0, 102.0],
    "High": [102.0, 103.0, 104.0],
    "Low": [99.0, 100.0, 101.0],
    "Close": [101.0, 102.0, 103.0],
    "Volume": [1000000, 1100000, 1200000],
}, index=pd.date_range("2020-01-02", periods=3))

# Create request
request = BacktestRunRequest(
    strategy_name="test_strategy",
    symbols=["SPY"],
    data={"SPY": spy_data},
    start_date=datetime(2020, 1, 2),
    end_date=datetime(2020, 1, 4),
    initial_cash=Decimal("100000"),
    parameters={},
)

# Try running
adapter = NautilusAdapter()
print(f"Adapter version: {adapter.version}")

try:
    result = adapter.run_backtest(request)
    print("✅ Backtest completed!")
    print(f"Final value: {result.final_value}")
except NotImplementedError as e:
    print(f"❌ Not implemented: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

Run:
```bash
uv run python scripts/test_nautilus_adapter.py
```

Work through each `NotImplementedError` one by one.

---

## Step 6: Iterative Development

### Workflow

1. Run test script
2. Hit `NotImplementedError` or error
3. Implement the TODO function
4. Re-run test script
5. Repeat until backtest completes

### Expected Challenges

**Challenge 1: Data format conversion**
- Nautilus has specific requirements for timestamps
- Solution: Read Nautilus bar documentation carefully

**Challenge 2: Instrument creation**
- Need to create InstrumentId and Instrument objects
- Solution: Check Nautilus examples for instrument creation

**Challenge 3: Strategy API**
- Nautilus strategies are event-driven, not bar-based
- Solution: Use a Nautilus example strategy for pilot (skip our strategy for now)

**Challenge 4: Result extraction**
- Nautilus stores results differently than Backtrader
- Solution: Print engine internals to find where metrics are stored

### Getting Help

- **Nautilus Docs:** https://nautilustrader.io/docs/latest/
- **API Reference:** https://nautilustrader.io/docs/latest/api_reference/
- **GitHub Issues:** https://github.com/nautechsystems/nautilus_trader/issues
- **Examples:** https://github.com/nautechsystems/nautilus_trader/tree/develop/examples

---

## Step 7: Basic Testing

Once you get a backtest to complete:

### Verify Results

```python
# Does it return a BacktestRunResult?
assert isinstance(result, BacktestRunResult)

# Does it have valid metadata?
assert result.metadata.engine == "nautilus"

# Does final value make sense?
assert result.final_value > 0
```

### Compare to Backtrader (informal)

Run same strategy with Backtrader and Nautilus:
- Are returns in the same ballpark?
- Do trade counts make sense?
- Major discrepancies indicate bugs

**Don't expect exact parity** - that's Phase 3, not Phase 2.

---

## Step 8: Document Findings

Create `docs/research/nautilus-pilot-findings.md`:

```markdown
# NautilusTrader Pilot Findings

## Installation
- Time spent: X hours
- Issues encountered: ...
- Resolution: ...

## Integration
- Time spent: Y hours
- Major challenges: ...
- What worked well: ...

## Initial Results
- Backtest completed: Yes/No
- Returns: X%
- Compared to Backtrader: Similar/Different (explain)

## First Impressions
- Learning curve: Easy/Medium/Hard
- Documentation quality: Good/Fair/Poor
- Would use for production: Yes/No/Maybe

## Recommendations
- Proceed to E6-T2 (evaluation): Yes/No
- Key concerns: ...
```

---

## Success Criteria (E6-T1)

You've completed E6-T1 when:

- [x] NautilusTrader installed
- [x] Adapter skeleton created (already done)
- [ ] Adapter functions implemented (TODOs replaced with code)
- [ ] At least one backtest completes without errors
- [ ] Results returned in BacktestRunResult format
- [ ] Basic findings documented

**Don't aim for perfection** - this is a pilot. Get something working, document findings, then decide if it's worth continuing.

---

## Time Estimates

Based on research:

- **Install & Setup:** 1-2 hours
- **Learning Nautilus:** 2-4 hours
- **Data Conversion:** 2-4 hours
- **Adapter Implementation:** 4-8 hours
- **Testing & Debugging:** 2-6 hours
- **Documentation:** 1-2 hours

**Total: 12-26 hours** (realistic: 16-20 hours)

---

## When to Stop

### Red Flags (Consider No-Go)

- Can't get basic example working after 4 hours
- Data conversion too complex (>8 hours and still failing)
- Documentation too sparse to figure out basics
- Major bugs that block progress
- Integration cost clearly exceeding value

### Green Flags (Consider continuing)

- Installation smooth
- Examples work as expected
- Data conversion straightforward
- Results look reasonable
- Learning curve manageable

---

## Next Steps After E6-T1

**If successful:**
- Proceed to E6-T2 (Evaluation report)
- Compare Nautilus vs Backtrader systematically
- Make go/no-go decision

**If blocked:**
- Document what didn't work
- Write E6-T3 decision memo (No-Go)
- Return to Backtrader improvements

---

## Questions?

If you get stuck:

1. Check Nautilus docs first
2. Search GitHub issues
3. Try Nautilus examples to see working code
4. Ask on Nautilus Slack/discussions
5. If fundamentally blocked, document and move to No-Go decision

---

**Status:** Ready for manual implementation
**Next:** Install Nautilus and start working through Step 1-8
**Owner:** You (cannot be automated by Claude)
