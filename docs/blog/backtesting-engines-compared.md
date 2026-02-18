# Backtrader vs NautilusTrader: A Hands-On Comparison for Python Quants

*Originally published: 2026-02-17*
*Reading time: ~12 minutes*

---

Choosing a backtesting engine is one of the most consequential architectural decisions you'll make in a quantitative trading project. Get it right and you have a solid foundation for years of research. Get it wrong and you'll spend hundreds of hours refactoring strategies to fit a new framework — or worse, you'll deploy a strategy that behaves differently in live trading than it did in backtest.

I've spent the last several months integrating both Backtrader and NautilusTrader into [Finbot](https://github.com/jerdaw/finbot), a quantitative analysis platform for personal research. This post is what I wish I'd read before starting.

---

## Quick Decision Matrix

If you're in a hurry:

| Situation | Recommendation |
|-----------|----------------|
| Pure backtesting, learning quant | **Backtrader** |
| Already planning to go live | **NautilusTrader** |
| Large existing Backtrader codebase | **Keep Backtrader** (migration cost high) |
| New project, performance matters | **NautilusTrader** |
| Python 3.11 required | **Backtrader** (Nautilus requires 3.12+) |
| Team unfamiliar with Rust-backed tools | **Backtrader** |

My recommendation for most projects: **start with Backtrader, migrate when you're ready to go live.**

---

## Architecture: Bar-Based vs Event-Driven

The most fundamental difference between the two engines is their execution model.

**Backtrader** uses a *bar-based* model. At each time step, it delivers a complete OHLCV bar to your strategy. You look at the data, decide what to do, and your order is filled — typically at the open of the next bar, or immediately at the current close. This is simple, predictable, and maps cleanly to the way most retail traders think about markets.

```python
# Backtrader strategy: simple and readable
class SmaCrossover(bt.Strategy):
    def next(self):
        if self.sma_fast > self.sma_slow:
            if not self.position:
                self.buy()
        elif self.position:
            self.sell()
```

**NautilusTrader** uses a *event-driven* model. Rather than processing bars, your strategy receives a stream of events: `BarEvent`, `QuoteTick`, `TradeTick`, `OrderFilled`, `PositionChanged`. This is closer to how real market microstructure works. An order isn't filled the moment you submit it — it enters a queue, gets matched, generates a fill event, updates your position.

```python
# NautilusTrader strategy: more complex, more realistic
class SmaCrossover(Strategy):
    def on_bar(self, bar: Bar) -> None:
        if self.fast_ema.value > self.slow_ema.value:
            if not self.portfolio.is_flat(self.instrument_id):
                return
            order = self.order_factory.market(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.instrument.make_qty(100),
            )
            self.submit_order(order)
```

The Nautilus version is more verbose, but it's modeling something important: the separation between *deciding to trade* and *being filled on a trade*.

---

## Fill Realism: Where Backtrader Falls Short

The bar-based model has an inherent problem: it can't realistically model what happens *inside* a bar.

Consider a strategy that buys when price drops 2% intraday. With Backtrader, you get the low of the bar — but you don't know *when* during the bar that low occurred, or whether your order would have been filled there. Backtrader's default is to fill at the open of the next bar, which assumes you had perfect timing at the close. More realistic commission schemes exist, but they're add-ons, not core.

NautilusTrader's fill simulation is more sophisticated:

- **Order queue modeling**: Market orders at the same price are filled in FIFO order
- **Probabilistic slippage**: Configurable slippage models that account for bar volatility
- **Order book simulation**: At-the-money options and spread products can be modeled
- **Latency simulation**: Configurable delay between order submission and fill

In Finbot, I ran the same no-rebalance strategy through both engines on identical data. The results were remarkably similar (within 1 basis point on most metrics) for simple bar-level strategies — which validated the parity. But for strategies with more complex execution assumptions, the gap would widen significantly.

---

## Performance: Rust vs Pure Python

NautilusTrader's core is written in Rust, compiled to a Python extension. This has concrete consequences:

| Metric | Backtrader | NautilusTrader |
|--------|-----------|----------------|
| 40-year daily backtest (single strategy) | ~2-4 seconds | <1 second |
| Memory usage (same strategy) | ~200MB | ~50MB |
| Python 3.12 compatibility | Yes (with warnings) | Yes (required) |
| Compilation required | No | No (pre-compiled wheels) |

The performance difference is meaningful if you're running parameter sweeps across thousands of configurations. If you're running one backtest at a time to understand a specific strategy, it doesn't matter.

Backtrader has its own speed issue: it uses Python inheritance deeply, which means it's slow to construct and slow to iterate. If you need high performance with Backtrader, consider running parallel instances across multiprocessing (which Finbot does with `backtest_batch.py`).

---

## Live Trading: The Most Important Difference

Here's where the architectural choice really matters.

**Backtrader** was designed for backtesting. It has a live trading mode, but it's grafted on — a separate execution path that doesn't share code with the backtest path. This means your strategy behaves slightly differently in backtest vs live, which is exactly the kind of subtle discrepancy that causes live trading disasters.

**NautilusTrader** was designed from the ground up for live trading first, with backtesting as a secondary use case. This means:

1. The same strategy code runs in both backtest and live modes
2. The execution infrastructure (order routing, fills, position tracking) is identical
3. The risk controls you test in backtest are the ones that fire in production

For anyone serious about eventually running strategies live, this is a massive practical advantage. Finbot's ADR-011 documents our decision to adopt a hybrid approach: Backtrader for research, Nautilus for strategies intended for live deployment.

---

## Ecosystem and Documentation

Backtrader wins on documentation. It has a comprehensive website, multiple books written about it, hundreds of blog posts, and a large Stack Overflow presence. When you get stuck, you can usually find an answer in 5 minutes.

NautilusTrader's documentation is more uneven. The API reference is auto-generated from type stubs, which means it exists but isn't always illuminating. For some features, you'll need to read the source code (which is well-organized Rust + Python). The Discord community is active and the maintainers respond quickly to issues.

One practical difference: Backtrader's strategy parameters use a declarative `params` tuple, while Nautilus uses standard Python `__init__` with type annotations. Nautilus feels more like modern Python, while Backtrader reflects its older heritage:

```python
# Backtrader: params declared at class level (old-style)
class MyStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
    )

# NautilusTrader: standard Python __init__ (modern)
class MyStrategy(Strategy):
    def __init__(self, fast_period: int = 10, slow_period: int = 30):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
```

---

## Type System: A Double-Edged Sword

NautilusTrader has a strict type system that catches many real trading errors at compile time. Prices, quantities, and instruments are distinct types that can't be mixed:

```python
# This won't compile — you can't multiply a Price by a Quantity without specifying
# what kind of value you want (notional value, etc.)
price = Price.from_str("450.25")
qty = Quantity.from_str("100")
notional = price * qty  # Type error: must use Money.from_raw() etc.
```

For a seasoned developer, this is excellent. For someone learning both the domain and the framework simultaneously, it's frustrating. I spent 2 hours on type-related issues in my first Nautilus session.

Backtrader uses plain Python floats for everything. This is more accessible, but it means you can silently do nonsensical things like adding a price to a quantity.

---

## My Migration Experience: Finbot Case Study

I migrated the `NoRebalance` strategy (buy and hold) from Backtrader to NautilusTrader as the first pilot. Here's what I learned:

**Time investment**: ~15 hours for the initial Nautilus integration (pilot beat the 12-26 hour estimate). Full migration of 12 strategies would take ~40 hours additional.

**Hardest parts**:
1. Understanding Nautilus's instrument/venue/client_id hierarchy
2. Mapping Backtrader's `self.data.close[0]` to Nautilus's bar event model
3. Typing issues with `Money`, `Currency`, `Price`, and `Quantity` types

**Easiest parts**:
1. The adapter pattern (Finbot's engine-agnostic contracts made this easy)
2. Performance — Nautilus is measurably faster on first run
3. Order lifecycle — Nautilus's event model makes fills and rejections explicit

The parity testing was revealing: 100% parity on CAGR, Sharpe, max drawdown on all three golden strategies. The execution model differs, but the outcomes align for bar-level strategies.

---

## My Recommendation

For **pure research and backtesting**: Backtrader. Lower learning curve, better documentation, plenty of examples online. If you're building a systematic trading research workflow and live trading is 2+ years away, the simplicity pays off.

For **teams planning to go live within 12 months**: NautilusTrader. Yes, the learning curve is steeper. Yes, the type system is strict. But the payoff is a single codebase that runs in both backtest and live modes, with realistic fill simulation that reduces the gap between paper and live performance.

For **existing Backtrader projects**: Think carefully before migrating. If your strategies are working and you're not planning to go live, the migration cost probably isn't worth it. If you are planning to go live, migrate one strategy at a time using an adapter pattern (which is exactly what Finbot does).

---

## Further Reading

- [Finbot GitHub repository](https://github.com/jerdaw/finbot) — includes both Backtrader and Nautilus adapters
- [ADR-011: NautilusTrader Adoption Decision](https://github.com/jerdaw/finbot/blob/main/docs/adr/ADR-011-nautilus-decision.md) — full decision rationale with tradeoff analysis
- [Choosing a Backtest Engine guide](https://github.com/jerdaw/finbot/blob/main/docs/guides/choosing-backtest-engine.md) — Finbot's internal guide
- [NautilusTrader documentation](https://nautilustrader.io)
- [Backtrader documentation](https://backtrader.com)

---

*Have you migrated from Backtrader to NautilusTrader, or vice versa? I'd love to hear about your experience. Open an issue on the Finbot repo or reach out directly.*

---

**Tags:** Python, backtesting, Backtrader, NautilusTrader, quantitative finance, algorithmic trading
