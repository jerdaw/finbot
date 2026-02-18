# Migrating Strategies from Backtrader to NautilusTrader

**Version:** 1.0
**Created:** 2026-02-17
**Audience:** Developers familiar with Backtrader who want to move strategies to NautilusTrader
**Prerequisites:** Python 3.12+, NautilusTrader installed (`uv add nautilus-trader`)

This guide walks through the complete process of migrating a strategy from Backtrader to NautilusTrader using Finbot's `NoRebalance` (buy-and-hold) strategy as the concrete example.

For context on *when* to migrate (vs when to stay with Backtrader), see [ADR-011](../adr/ADR-011-nautilus-decision.md) and [docs/guides/choosing-backtest-engine.md](choosing-backtest-engine.md).

---

## The Core Shift: Bar-Based → Event-Driven

Before looking at code, understand the fundamental architectural difference.

**Backtrader** (bar-based): your strategy's `next()` method is called once per bar. At that point, all data for the bar is available. You decide to trade; the trade is filled (usually at the next bar's open, though this is configurable).

```python
# Backtrader: synchronous, bar-at-a-time
def next(self):
    if not self.position:
        self.buy()  # Filled at next bar open by default
```

**NautilusTrader** (event-driven): your strategy receives events. A `BarEvent` fires for each bar. An `OrderFilled` event fires asynchronously when the exchange fills your order. These are explicitly separate events.

```python
# Nautilus: asynchronous, event-at-a-time
def on_bar(self, bar: Bar) -> None:
    if not self.portfolio.is_flat(self.instrument_id):
        return
    order = self.order_factory.market(
        instrument_id=self.instrument_id,
        order_side=OrderSide.BUY,
        quantity=self.instrument.make_qty(100),
    )
    self.submit_order(order)

def on_order_filled(self, event: OrderFilled) -> None:
    # Fill confirmed — update your state here
    pass
```

This separation is not cosmetic. It reflects how real markets work: submitting an order and having it filled are asynchronous events separated by network latency, matching engine time, and queue position. For backtesting daily bars, the difference is invisible. For intraday or live trading, it matters enormously.

---

## The Backtrader Strategy

Here's the `NoRebalance` strategy in Backtrader — Finbot's buy-and-hold implementation:

```python
import backtrader as bt


class NoRebalance(bt.Strategy):
    """Buy and hold across multiple assets at specified proportions."""

    def __init__(self, equity_proportions):
        self.equity_proportions = equity_proportions  # e.g., [0.6, 0.4] for 60/40
        self.dataclose = self.datas[0].close
        self.order = None

    def notify_order(self, order):
        # Clear pending order reference when order completes or cancels
        self.order = None

    def next(self):
        if self.order:
            return  # Wait for pending order to complete

        if not self.getposition():  # Not yet invested
            n_stocks = len(self.datas)
            cur_tot_cash = self.broker.get_cash()

            # Calculate target shares for each asset
            des_values = [self.equity_proportions[i] * cur_tot_cash for i in range(n_stocks)]
            des_n_stocks = [round(des_values[i] // self.datas[i].close) for i in range(n_stocks)]

            for d_idx in range(n_stocks):
                des_n = des_n_stocks[d_idx]
                self.buy(data=self.datas[d_idx], size=abs(round(des_n)))
```

### What This Strategy Does

1. On the first bar where no position exists, calculate how many shares of each asset to buy
2. Buy those shares at each asset's current price
3. Hold forever (no rebalancing, no selling)

It's minimal — no parameters, no signals, no rebalancing. This makes it a good migration target because the port reveals the structural differences cleanly.

---

## The NautilusTrader Equivalent

Here's the same strategy in NautilusTrader. Note it's longer — not because the strategy is more complex, but because Nautilus makes more explicit what Backtrader hides implicitly.

```python
from decimal import Decimal

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy


class NoRebalanceConfig(StrategyConfig, frozen=True):
    """Configuration for NoRebalance strategy."""
    instrument_id: str
    bar_type: str
    equity_proportion: Decimal = Decimal("1.0")  # Fraction to invest (0.0-1.0)


class NoRebalanceNautilus(Strategy):
    """Buy and hold strategy — NautilusTrader version.

    Buys a fixed quantity on first bar and holds indefinitely.
    """

    def __init__(self, config: NoRebalanceConfig):
        super().__init__(config)
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.bar_type = BarType.from_str(config.bar_type)
        self.equity_proportion = config.equity_proportion
        self._invested = False

    def on_start(self) -> None:
        """Subscribe to data feeds on strategy start."""
        # Tell Nautilus we want bar data for this instrument
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar: Bar) -> None:
        """Process each bar — buy once on first bar."""
        if self._invested:
            return  # Already bought; hold forever

        # Determine how many shares to buy
        instrument = self.cache.instrument(self.instrument_id)
        account = self.portfolio.account("SIM")
        available_cash = account.balance_free("USD").as_decimal()

        invest_amount = available_cash * self.equity_proportion
        close_price = bar.close.as_decimal()
        shares = int(invest_amount / close_price)

        if shares <= 0:
            return

        # Submit market order
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=instrument.make_qty(shares),
        )
        self.submit_order(order)
        self._invested = True

    def on_order_filled(self, event) -> None:
        """Log fills for observability."""
        self.log.info(f"Order filled: {event}")

    def on_stop(self) -> None:
        """Unsubscribe on stop."""
        self.unsubscribe_bars(self.bar_type)
```

---

## Side-by-Side Comparison

| Backtrader | NautilusTrader | Notes |
|-----------|----------------|-------|
| `bt.Strategy` | `Strategy` + `StrategyConfig` | Config is a separate frozen dataclass |
| `params = (('period', 10),)` | `class Config(StrategyConfig): period: int = 10` | Modern Python `__init__` with types |
| `def next(self):` | `def on_bar(self, bar: Bar):` | Same purpose, explicit type |
| `self.datas[0].close[0]` | `bar.close.as_decimal()` | Nautilus uses strict types |
| `self.broker.get_cash()` | `account.balance_free("USD").as_decimal()` | Explicit currency |
| `self.buy(size=n)` | `self.order_factory.market(...)` then `self.submit_order(...)` | Explicit order construction |
| `self.getposition()` | `self.portfolio.is_flat(instrument_id)` | Same concept, different API |
| `def notify_order(self, order):` | `def on_order_filled(self, event):` | Explicitly named events |
| No subscription needed | `self.subscribe_bars(self.bar_type)` in `on_start()` | Explicit data subscription |

---

## Running the NautilusTrader Backtest

```python
from decimal import Decimal
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money

# 1. Create engine
engine = BacktestEngine(config=BacktestEngineConfig(logging=LoggingConfig(log_level="ERROR")))

# 2. Add venue (simulated exchange)
engine.add_venue(
    venue=Venue("SIM"),
    oms_type=OmsType.NETTING,
    account_type=AccountType.CASH,
    base_currency=USD,
    starting_balances=[Money(100_000, USD)],
)

# 3. Add instrument
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.identifiers import InstrumentId, Symbol
from nautilus_trader.model.objects import Price, Quantity

instrument = Equity(
    instrument_id=InstrumentId(Symbol("SPY"), Venue("SIM")),
    raw_symbol=Symbol("SPY"),
    currency=USD,
    price_precision=2,
    price_increment=Price.from_str("0.01"),
    lot_size=Quantity.from_int(1),
    ts_event=0,
    ts_init=0,
)
engine.add_instrument(instrument)

# 4. Load bar data (convert from pandas DataFrame)
# See NautilusAdapter._convert_dataframe_to_bars() in finbot/adapters/nautilus/
engine.add_data(bars)

# 5. Add strategy
config = NoRebalanceConfig(
    instrument_id="SPY.SIM",
    bar_type="SPY.SIM-1-DAY-LAST-EXTERNAL",
    equity_proportion=Decimal("1.0"),
)
engine.add_strategy(NoRebalanceNautilus(config=config))

# 6. Run
engine.run()

# 7. Extract results
account = engine.portfolio.account(Venue("SIM"))
final_value = account.balance_total(USD).as_double()
print(f"Final portfolio value: ${final_value:,.2f}")
```

---

## The Type System: What to Expect

The most common migration pain point is Nautilus's strict type system. Here's what to watch for:

### Price and Quantity Are Not Floats

```python
# Backtrader: everything is a Python float
close = self.data.close[0]  # float
shares = cash / close        # float division

# Nautilus: distinct types, explicit conversion
close: Price = bar.close
close_decimal: Decimal = bar.close.as_decimal()  # explicit conversion
shares: int = int(invest_amount / close_decimal)  # integer shares
qty: Quantity = instrument.make_qty(shares)       # explicit Quantity
```

**Why this matters:** You can't accidentally multiply a Price by a Quantity and get a nonsensical result. The type system catches calculation errors that would silently produce wrong numbers in Backtrader.

### Money Has a Currency

```python
# Backtrader: cash is a float with no currency
cash = self.broker.get_cash()  # just a number

# Nautilus: cash is Money with explicit currency
balance = account.balance_free("USD")  # Money(100000.00, USD)
amount = balance.as_decimal()          # Decimal, now you can do math
```

### InstrumentId Has a Venue

```python
# Nautilus: instruments are venue-qualified
instrument_id = InstrumentId.from_str("SPY.SIM")  # symbol.venue
# "SIM" is the simulated venue for backtesting
# "XNAS" would be NASDAQ for real data
```

---

## Common Migration Errors

### Error 1: Using float arithmetic on Price objects

```python
# Wrong: arithmetic on Price objects
close = bar.close
invest = cash * close  # TypeError: unsupported operand type

# Right: extract Decimal first
close = bar.close.as_decimal()
invest = cash * close
```

### Error 2: Forgetting to subscribe in on_start()

```python
# Wrong: subscribes in __init__ (too early)
def __init__(self, config):
    self.subscribe_bars(self.bar_type)  # AttributeError

# Right: subscribe in on_start()
def on_start(self) -> None:
    self.subscribe_bars(self.bar_type)  # Correct
```

### Error 3: Wrong timestamp format for bars

```python
# Wrong: datetime objects in bar ts_event
ts_event = datetime(2020, 1, 2)  # TypeError

# Right: nanosecond integers
ts_event = int(pd.Timestamp("2020-01-02").value)  # nanoseconds since epoch
```

### Error 4: Missing unsubscribe in on_stop()

```python
# Always unsubscribe in on_stop() to avoid resource leaks
def on_stop(self) -> None:
    self.unsubscribe_bars(self.bar_type)
```

---

## Multi-Asset Strategies

Backtrader handles multiple assets by iterating `self.datas`. In Nautilus, you subscribe to multiple bar types and track each instrument separately:

```python
class MultiAssetConfig(StrategyConfig, frozen=True):
    instrument_ids: list[str]
    bar_types: list[str]
    proportions: list[float]

class MultiAssetNoRebalance(Strategy):
    def __init__(self, config: MultiAssetConfig):
        super().__init__(config)
        self.instrument_ids = [InstrumentId.from_str(i) for i in config.instrument_ids]
        self.bar_types = [BarType.from_str(b) for b in config.bar_types]
        self.proportions = config.proportions
        self._invested = False
        self._received_bars: set[InstrumentId] = set()

    def on_start(self) -> None:
        for bar_type in self.bar_types:
            self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar) -> None:
        if self._invested:
            return

        # Track which instruments have delivered a bar
        self._received_bars.add(bar.bar_type.instrument_id)

        # Only trade once all instruments have data
        if len(self._received_bars) < len(self.instrument_ids):
            return

        account = self.portfolio.account("SIM")
        total_cash = account.balance_free("USD").as_decimal()

        for inst_id, bar_type, proportion in zip(
            self.instrument_ids, self.bar_types, self.proportions
        ):
            instrument = self.cache.instrument(inst_id)
            current_bar = self.cache.bar(bar_type)
            if current_bar is None:
                continue

            invest_amount = total_cash * Decimal(str(proportion))
            shares = int(invest_amount / current_bar.close.as_decimal())

            if shares > 0:
                order = self.order_factory.market(
                    instrument_id=inst_id,
                    order_side=OrderSide.BUY,
                    quantity=instrument.make_qty(shares),
                )
                self.submit_order(order)

        self._invested = True
```

---

## Validation: Parity Testing

After migrating, verify that results match Backtrader on the same data. Finbot's parity harness does this:

```bash
# Run parity tests
uv run pytest tests/ -k "parity" -v

# Or run the golden strategy parity gate
uv run pytest tests/unit/test_strategies.py -v
```

**Expected parity tolerance:** For bar-level strategies with identical data, expect within 1 basis point on CAGR, Sharpe ratio, and max drawdown. Larger differences indicate a bug in the migration.

The parity harness (`tests/unit/test_backtrader_adapter.py`) provides the reference implementation for setting up these comparisons.

---

## When to Use Each Engine

| Use Case | Recommendation |
|----------|---------------|
| Research backtesting | Backtrader — lower learning curve |
| Strategy going live | NautilusTrader — same code path |
| Tick-level simulation | NautilusTrader — native support |
| Parameter sweeps (thousands) | Backtrader — faster per-run for simple strategies |
| Realistic fill modeling | NautilusTrader — order queue, slippage |
| Existing Backtrader codebase | Keep Backtrader — migration cost is real |

For Finbot's hybrid approach rationale, see [ADR-011](../adr/ADR-011-nautilus-decision.md).

---

## Checklist for Migration

- [ ] Install `nautilus-trader` with Python 3.12+ (`uv add nautilus-trader`)
- [ ] Create `StrategyConfig` subclass (frozen=True) with all parameters
- [ ] Implement `on_start()` with data subscriptions
- [ ] Implement `on_bar()` with event-driven logic
- [ ] Implement `on_stop()` with unsubscriptions
- [ ] Replace float arithmetic with Decimal-based arithmetic
- [ ] Use `instrument.make_qty()` for Quantity creation
- [ ] Replace `self.buy()` with `order_factory.market()` + `self.submit_order()`
- [ ] Test parity against Backtrader on 1+ year of daily data
- [ ] Verify CAGR, Sharpe, and max drawdown match within 1bp

---

## Resources

- [NautilusTrader documentation](https://nautilustrader.io/docs/) — official docs
- [Finbot NautilusAdapter](../../finbot/adapters/nautilus/nautilus_adapter.py) — full implementation
- [Finbot backtesting engines comparison](../blog/backtesting-engines-compared.md) — architecture overview
- [ADR-011: NautilusTrader Adoption Decision](../adr/ADR-011-nautilus-decision.md) — decision rationale
- [NautilusTrader Discord](https://discord.com/invite/AUWVs3XaCS) — active community support
