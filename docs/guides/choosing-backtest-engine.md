# Choosing a Backtest Engine: Backtrader vs NautilusTrader

**Last Updated:** 2026-02-17
**Decision:** [ADR-011 - Hybrid Approach](../adr/ADR-011-nautilus-decision.md)
**Evaluation:** [E6-T2 Pilot Evaluation](../research/nautilus-pilot-evaluation.md)

## Quick Decision Matrix

| Your Goal | Recommended Engine | Why |
|-----------|-------------------|-----|
| **Pure backtesting only** | Backtrader | Mature, stable, familiar |
| **Planning for live trading** | Nautilus | Live trading support built-in |
| **Quick prototyping** | Backtrader | Faster setup, simpler API |
| **Advanced order types** | Nautilus | More realistic fill simulation |
| **Event-driven strategies** | Nautilus | Native event architecture |
| **Learning/teaching** | Backtrader | Gentler learning curve |
| **Cross-validation** | Both (Hybrid) | Verify results across engines |
| **Gradual migration** | Both (Hybrid) | Use Backtrader while learning Nautilus |

## TL;DR

**Use Backtrader** if you're doing pure backtesting with no plans for live trading.
**Use Nautilus** if you're building toward live trading or need realistic fills.
**Use Both** if you want the best of both worlds (recommended for serious development).

---

## Overview

Finbot supports two backtesting engines through a unified adapter interface:

1. **Backtrader** - Mature, battle-tested, bar-based backtesting (v1.9.78+)
2. **NautilusTrader** - Modern, event-driven, live-trading capable (v1.222.0+)

Both engines implement the same `BacktestEngine` interface, so switching between them is seamless.

### Can I Use Both?

**Yes!** The hybrid approach is recommended:
- **Backtrader** for familiar backtesting workflows
- **Nautilus** for strategies you plan to take live
- **Cross-validation** to verify results match

---

## Engine Comparison

### Architecture

| Aspect | Backtrader | Nautilus |
|--------|-----------|----------|
| **Execution Model** | Bar-based (end of bar) | Event-driven (microsecond precision) |
| **Language** | Pure Python | Rust core + Python bindings |
| **Type System** | Dynamic | Strongly typed (Money, Price, Quantity objects) |
| **Fill Model** | Simplified (assumes fills) | Realistic (order matching, slippage) |
| **Order Lifecycle** | Immediate execution | NEW → SUBMITTED → FILLED with latency |
| **Live Trading** | Limited/experimental | Production-ready |

### Performance

**From E6-T2 Evaluation:**

| Metric | Backtrader | Nautilus | Winner |
|--------|-----------|----------|--------|
| **Setup Time** | 5 min | 15 hours | Backtrader |
| **Learning Curve** | Gentle | Steep | Backtrader |
| **Backtest Speed** | Fast | Fast | Tie |
| **Fill Realism** | 3/5 | 5/5 | Nautilus |
| **Live Trading** | 1/5 | 5/5 | Nautilus |
| **Documentation** | 4/5 | 3/5 | Backtrader |
| **Overall Score** | 3.30/5 | 3.95/5 | **Nautilus (+19.7%)** |

### Feature Comparison

| Feature | Backtrader | Nautilus | Notes |
|---------|-----------|----------|-------|
| **Bar data** | ✅ Yes | ✅ Yes | Both support OHLCV bars |
| **Tick data** | ⚠️ Limited | ✅ Yes | Nautilus built for tick data |
| **Commission models** | ✅ Yes | ✅ Yes | Both support custom models |
| **Slippage models** | ✅ Yes | ✅ Yes | Nautilus more realistic |
| **Order types** | ✅ Market, Limit, Stop | ✅ All types | Nautilus has more |
| **Position tracking** | ✅ Yes | ✅ Yes | Different APIs |
| **Portfolio analytics** | ✅ Yes | ✅ Yes | Similar capabilities |
| **Walk-forward** | ✅ Yes | ⚠️ Manual | Need to implement |
| **Parameter optimization** | ✅ Built-in | ⚠️ Manual | Backtrader advantage |
| **Live trading** | ⚠️ Experimental | ✅ Production | **Nautilus advantage** |
| **Paper trading** | ⚠️ Limited | ✅ Built-in | Nautilus advantage |
| **Historical replay** | ✅ Yes | ✅ Yes | Both support |
| **Data feeds** | ✅ Many | ✅ Many | Both extensible |

---

## Use Cases

### Use Backtrader When...

✅ **You're doing pure backtesting**
- No plans for live trading
- Evaluating strategy performance historically
- Research and analysis only

✅ **You want quick prototyping**
- Testing ideas rapidly
- Simple bar-based logic
- Minimal setup overhead

✅ **You prefer familiar tools**
- Already know Backtrader
- Team has Backtrader expertise
- Don't want to learn new type system

✅ **You're teaching/learning**
- Educational context
- Introducing backtesting concepts
- Simpler mental model

✅ **You have existing Backtrader strategies**
- Already invested in Backtrader
- Working code you don't want to migrate
- No compelling reason to switch

**Example Scenario:**
> "I want to backtest a simple SMA crossover strategy to see if it works on SPY. I don't plan to trade it live."
>
> **→ Use Backtrader** (quick setup, familiar, sufficient for the task)

### Use Nautilus When...

✅ **You're planning for live trading**
- Strategy will eventually trade live
- Need production-ready infrastructure
- Want seamless backtest → paper → live progression

✅ **You need realistic fill simulation**
- Order matching algorithms
- Realistic latency modeling
- Slippage simulation
- Partial fills

✅ **You're building event-driven strategies**
- React to market events in real-time
- Need microsecond precision
- Complex order logic

✅ **You want advanced order types**
- OCO (One-Cancels-Other)
- Bracket orders
- Trailing stops
- Conditional orders

✅ **You need professional-grade execution**
- Multiple brokers/exchanges
- FIX protocol support
- Institutional-grade features

**Example Scenario:**
> "I'm developing a mean-reversion strategy that I plan to deploy live on Interactive Brokers. I need realistic fill simulation and want a smooth path from backtest to production."
>
> **→ Use Nautilus** (built for live trading, realistic fills, production-ready)

### Use Both (Hybrid) When...

✅ **You want the best of both worlds**
- Backtrader for familiar backtesting
- Nautilus for strategies going live
- Engine-specific strengths for each use case

✅ **You're doing cross-validation**
- Verify results across engines
- Catch implementation bugs
- Ensure strategy robustness

✅ **You're migrating gradually**
- Keep using Backtrader for existing strategies
- Start new live-trading strategies in Nautilus
- No "big bang" migration

✅ **You're building a production system**
- Backtest in Backtrader (faster iteration)
- Validate in Nautilus (realistic fills)
- Deploy Nautilus to production

**Example Scenario:**
> "I have 5 working strategies in Backtrader. I want to take 2 of them live eventually. I don't want to rewrite everything."
>
> **→ Use Hybrid** (keep 3 in Backtrader, migrate 2 to Nautilus gradually)

---

## Migration Guide

### Migrating from Backtrader to Nautilus

**Step 1: Understand the Differences**
- Read the [E6-T2 Evaluation](../research/nautilus-pilot-evaluation.md)
- Understand Nautilus's type system (Money, Price, Quantity)
- Learn event-driven architecture

**Step 2: Start with Simple Strategy**
- Pick a simple strategy for first migration
- Avoid complex strategies for first attempt
- Focus on core logic, not edge cases

**Step 3: Implement Strategy**
- Adapt to Nautilus `Strategy` class
- Convert bar-based logic to event-driven
- Handle Nautilus types (Money in cents, Currency objects)

**Step 4: Validate with Parity Testing**
- Run both Backtrader and Nautilus on same data
- Compare results (returns, trades, metrics)
- Investigate discrepancies

**Step 5: Iterate**
- Fix bugs found in parity testing
- Refine fill models
- Tune parameters if needed

**Parity Tolerance (from ADR-005):**
- Returns: ±0.1%
- CAGR: ±0.05%
- Trade count: Exact match
- Sharpe ratio: ±0.1

**What to Watch For:**
- **Type conversions**: Money, Price, Quantity require explicit construction
- **Fill timing**: Nautilus fills may differ slightly due to order matching
- **Event handling**: Events are asynchronous, not sequential
- **Data alignment**: Ensure timestamps match

---

## Examples

### Example 1: Simple SMA Crossover

**Backtrader Version:**
```python
import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (('fast', 50), ('slow', 200),)

    def __init__(self):
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()
```

**Nautilus Version:**
```python
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.indicators.average.sma import SimpleMovingAverage

class SMACrossover(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.fast_sma = SimpleMovingAverage(50)
        self.slow_sma = SimpleMovingAverage(200)

    def on_bar(self, bar):
        # Update indicators
        self.fast_sma.update_raw(bar.close.as_double())
        self.slow_sma.update_raw(bar.close.as_double())

        # Check crossover
        if not self.fast_sma.initialized or not self.slow_sma.initialized:
            return

        if self.fast_sma.value > self.slow_sma.value and not self.portfolio.is_flat:
            self.buy()
        elif self.fast_sma.value < self.slow_sma.value and self.portfolio.is_flat:
            self.sell()
```

**Key Differences:**
1. **Initialization**: Nautilus uses explicit indicator construction
2. **Data access**: Nautilus uses `bar.close.as_double()` for price
3. **Position checking**: Nautilus uses `portfolio.is_flat`
4. **Event handling**: Nautilus is event-driven (`on_bar` callback)

### Example 2: Using the Adapter Interface

**With Backtrader:**
```python
from finbot.adapters.backtrader import BacktraderAdapter
from finbot.core.contracts.models import BacktestRunRequest

adapter = BacktraderAdapter()
request = BacktestRunRequest(
    strategy_name="sma_crossover",
    symbols=("SPY",),
    start=pd.Timestamp("2020-01-01"),
    end=pd.Timestamp("2023-12-31"),
    initial_cash=100000.0,
    parameters={"fast": 50, "slow": 200}
)

result = adapter.run_backtest(request)
print(f"Return: {result.metrics['total_return_pct']:.2f}%")
```

**With Nautilus:**
```python
from finbot.adapters.nautilus import NautilusAdapter
from finbot.core.contracts.models import BacktestRunRequest

adapter = NautilusAdapter()
request = BacktestRunRequest(
    strategy_name="sma_crossover",
    symbols=("SPY",),
    start=pd.Timestamp("2020-01-01"),
    end=pd.Timestamp("2023-12-31"),
    initial_cash=100000.0,
    parameters={"fast": 50, "slow": 200}
)

result = adapter.run_backtest(request)
print(f"Return: {result.metrics['total_return_pct']:.2f}%")
```

**Notice:** The adapter interface is identical! Only the adapter import changes.

---

## Decision Flowchart

```
Start: I want to backtest a strategy
    |
    ├─→ Do I plan to trade this live?
    |   |
    |   ├─→ Yes → Use Nautilus
    |   |          (or Hybrid for gradual migration)
    |   |
    |   └─→ No → Continue
    |
    ├─→ Do I need realistic fill simulation?
    |   |
    |   ├─→ Yes → Use Nautilus
    |   |
    |   └─→ No → Continue
    |
    ├─→ Am I just learning/prototyping?
    |   |
    |   ├─→ Yes → Use Backtrader
    |   |          (easier learning curve)
    |   |
    |   └─→ No → Continue
    |
    ├─→ Do I already have Backtrader strategies?
    |   |
    |   ├─→ Yes → Use Hybrid
    |   |          (keep Backtrader, add Nautilus for new)
    |   |
    |   └─→ No → Continue
    |
    └─→ Default recommendation: Backtrader
        (simpler for pure backtesting)
```

---

## Getting Started

### With Backtrader

```bash
# Already installed - ready to use!
# See existing strategies in finbot/services/backtesting/strategies/
```

**Documentation:**
- [Backtrader Official Docs](https://www.backtrader.com/)
- [Finbot Backtesting Guide](../user-guide/backtesting.md)

### With Nautilus

```bash
# Already installed (as of E6 pilot)
# See adapter: finbot/adapters/nautilus/nautilus_adapter.py
```

**Documentation:**
- [NautilusTrader Official Docs](https://nautilustrader.io/)
- [E6 Pilot Evaluation](../research/nautilus-pilot-evaluation.md)
- [E6 Implementation Guide](../planning/e6-t1-implementation-guide.md)

### With Both (Hybrid)

Use the adapter interface to switch seamlessly:

```python
# Choose your engine
from finbot.adapters.backtrader import BacktraderAdapter as Adapter
# Or: from finbot.adapters.nautilus import NautilusAdapter as Adapter

# Rest of code is identical
adapter = Adapter()
result = adapter.run_backtest(request)
```

---

## Frequently Asked Questions

### Q: Which engine is faster?

**A:** Both are fast for bar-based backtesting. Nautilus may be faster for tick data due to Rust core, but for typical daily bar strategies, performance is similar.

### Q: Can I run the same strategy on both engines?

**A:** Not directly - strategies must be adapted to each engine's API. However, the adapter interface provides a common way to *run* strategies, so you can compare results.

### Q: Which engine is more accurate?

**A:** Nautilus has more realistic fill simulation (order matching, latency, slippage). For most bar-based strategies, differences are small. For high-frequency or market-making strategies, Nautilus is more accurate.

### Q: Is Nautilus production-ready for live trading?

**A:** Yes! Nautilus is designed for production live trading and is used by professional trading firms. Backtrader's live trading is experimental and not recommended for production.

### Q: Can I use Backtrader for some strategies and Nautilus for others?

**A:** Absolutely! This is the hybrid approach recommended in ADR-011. Use each engine where it excels.

### Q: What's the migration path from Backtrader to Nautilus?

**A:** See the Migration Guide section above. Start with simple strategies, use parity testing, and migrate gradually. No need to migrate everything at once.

### Q: Do I need to choose one engine forever?

**A:** No! The adapter pattern means you can switch engines without changing infrastructure. Your data pipeline, results storage, and analytics work with both.

---

## References

**Decision Documents:**
- [ADR-011: NautilusTrader Adoption Decision](../adr/ADR-011-nautilus-decision.md)
- [ADR-005: Adapter-First Architecture](../adr/ADR-005-adapter-first-backtesting-live-readiness.md)

**Evaluation:**
- [E6-T2: NautilusTrader Pilot Evaluation](../research/nautilus-pilot-evaluation.md) (685 lines, comprehensive)
- [Backtesting Baseline Report](../research/backtesting-baseline-report.md)

**Implementation:**
- [E6-T1 Implementation Guide](../planning/e6-t1-implementation-guide.md)
- [Backtrader Adapter](../../finbot/adapters/backtrader/)
- [Nautilus Adapter](../../finbot/adapters/nautilus/)

**External:**
- [Backtrader Official Site](https://www.backtrader.com/)
- [NautilusTrader Official Site](https://nautilustrader.io/)
- [NautilusTrader GitHub](https://github.com/nautechsystems/nautilus_trader)

---

## Summary

**Backtrader:** Mature, familiar, great for pure backtesting
**Nautilus:** Modern, realistic, built for live trading
**Hybrid:** Best of both worlds (recommended)

**Next Steps:**
1. Read this guide to understand trade-offs
2. Pick the engine that matches your goals
3. Start with simple strategies
4. Use parity testing if using both
5. Refer to evaluation docs for detailed comparison

**Questions?** See the [E6-T2 Evaluation](../research/nautilus-pilot-evaluation.md) for 685 lines of detailed analysis, or check the [ADR-011 Decision](../adr/ADR-011-nautilus-decision.md) for strategic context.
