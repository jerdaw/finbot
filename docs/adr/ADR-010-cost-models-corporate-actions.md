# ADR-010: Cost Models and Corporate Actions

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Development team
**Epic:** E3 (Backtesting Fidelity Improvements)

## Context

Accurate backtesting requires two critical fidelity improvements:

1. **Realistic cost modeling** - Trading costs significantly impact strategy performance, yet most backtests either ignore them or use oversimplified models. Real trading incurs:
   - Commission costs (per-share or percentage-based)
   - Bid-ask spread costs (execution at worse-than-midpoint prices)
   - Slippage (price movement during order execution)
   - Borrowing costs (for leveraged or margin positions)
   - Market impact (large orders moving prices)

2. **Corporate action adjustments** - Historical price data requires adjustment for:
   - Stock splits (2:1, 3:1, reverse splits)
   - Dividend payments (cash distributions)
   - Spin-offs and mergers
   Without proper adjustments, backtests use incorrect prices and produce misleading results.

### Current State Problems

**Before E3-T1 (Cost Models):**
- Commission costs hardcoded in BacktestRunner (0.1 bps default)
- No spread or slippage modeling
- No borrowing cost tracking
- Costs embedded in fill execution (not separately observable)
- Can't compare strategy performance under different cost regimes

**Before E3-T2 (Corporate Actions):**
- Backtrader used unadjusted Close prices
- Stock splits distorted returns
- Dividend payments ignored
- No validation of price discontinuities
- Missing data gaps caused backtest failures

### Requirements

**Cost Models:**
- Pluggable cost models (zero/flat/percentage/complex)
- Separate cost tracking from execution (observability)
- Support commission, spread, slippage, borrow costs
- Backward compatible (default to zero costs for parity)
- Cost breakdown by type and symbol

**Corporate Actions:**
- Use adjusted prices by default (Adj Close)
- Proportionally adjust OHLC to maintain price relationships
- Preserve original prices for reference (Close_Unadjusted)
- Handle missing data gracefully (forward-fill, drop, error, interpolate)
- Validate price data before backtest execution

## Decision

We will implement:

### 1. Separate CostEvent Tracking

Costs are modeled as discrete events, separate from order fills:

```python
@dataclass(frozen=True, slots=True)
class CostEvent:
    """Single cost event during backtesting."""
    timestamp: pd.Timestamp
    symbol: str
    cost_type: CostType  # COMMISSION | SPREAD | SLIPPAGE | BORROW | MARKET_IMPACT
    amount: float  # Dollar amount (always positive)
    basis: str  # Human-readable calculation description
```

**Rationale:**
- Observability: Inspect all costs in isolation
- Debuggability: Verify cost calculations separately from fills
- Flexibility: Change cost models without changing execution logic
- Analysis: Aggregate costs by type, symbol, time period

### 2. Pluggable CostModel Protocol

All cost models implement a common interface:

```python
class CostModel(Protocol):
    """Interface for cost calculation models."""

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate cost for a trade.

        Returns:
            Cost in dollars (always positive, even for sells)
        """
        ...

    def get_name(self) -> str:
        """Return human-readable name of this cost model."""
        ...
```

**Implementations:**
- **ZeroCommission**: Free trading (default for parity)
- **FlatCommission**: Per-share commission (e.g., $0.001/share)
- **PercentageCommission**: Percentage of trade value (e.g., 0.1%)
- **FixedCommission**: Fixed cost per trade
- **SqrtCommission**: √(shares) scaling (models market impact)

**Spread Models:**
- **ZeroSpread**: No spread cost (default)
- **PercentageSpread**: Fixed percentage spread (e.g., 5 bps)

**Slippage Models:**
- **ZeroSlippage**: No slippage (default)
- **PercentageSlippage**: Fixed percentage (e.g., 2 bps)
- **SqrtSlippage**: √(shares) scaling (models market impact)

### 3. Cost Summary in Results

Backtest results include comprehensive cost breakdown:

```python
@dataclass(frozen=True, slots=True)
class CostSummary:
    """Summary of all costs incurred during a backtest."""
    total_commission: float
    total_spread: float
    total_slippage: float
    total_borrow: float
    total_market_impact: float
    cost_events: tuple[CostEvent, ...]  # All individual cost events

    @property
    def total_costs(self) -> float:
        """Total of all costs."""
        return (
            self.total_commission + self.total_spread + self.total_slippage
            + self.total_borrow + self.total_market_impact
        )

    def costs_by_type(self) -> dict[CostType, float]:
        """Return costs broken down by type."""
        ...

    def costs_by_symbol(self) -> dict[str, float]:
        """Return costs broken down by symbol."""
        ...
```

**Integration:**
- `BacktestRunResult.costs` field (optional, None for legacy runs)
- TradeTracker analyzer captures all fills
- Cost models applied to each fill
- JSON serialization/deserialization support

### 4. Adjusted Price Handling

**Default behavior (when Adj Close is present):**

```python
# 1. Replace Close with Adj Close
df["Close_Unadjusted"] = df["Close"]  # Preserve original
df["Close"] = df["Adj Close"]

# 2. Adjust OHLC proportionally to maintain price relationships
adj_factor = df["Adj Close"] / df["Close_Unadjusted"]
df["Open"] = df["Open"] * adj_factor
df["High"] = df["High"] * adj_factor
df["Low"] = df["Low"] * adj_factor
```

**Rationale:**
- Maintains OHLC relationships (High > Low, Close between Open and High/Low)
- Preserves intraday patterns for strategies using OHLC
- Backtrader sees consistent, split/dividend-adjusted prices
- Original prices preserved for reference

**When Adj Close is missing:**
- Use data as-is (no adjustment)
- Log warning for user awareness

### 5. Corporate Action Formulas

**Stock Split (2:1):**
```
Pre-split:  Price = $100, Shares = 100
Post-split: Price = $50,  Shares = 200
Adjustment: All historical prices ÷ 2
```

**Dividend ($2 payment):**
```
Ex-dividend date: Price drops by $2 (unadjusted)
Adjustment: All historical prices reduced by dividend amount
Formula: Adj_Price = Close - Cumulative_Dividends_After
```

**Combined (split + dividend):**
```
Adjustment_Factor = (Close - Cumulative_Dividends) / Split_Multiplier
Adj_Price = Close * Adjustment_Factor
```

**Implementation:**
- YFinance provides pre-calculated Adj Close
- Backtrader adapter applies adjustments before feeding to Cerebro
- Corporate action columns (Dividends, Stock Splits) preserved for reference

### 6. Missing Data Policies

**Policy Enum:**
```python
class MissingDataPolicy(StrEnum):
    FORWARD_FILL = "forward_fill"  # Use last known price
    DROP = "drop"                   # Remove gaps (changes date range)
    ERROR = "error"                 # Fail fast with clear error
    INTERPOLATE = "interpolate"     # Linear interpolation
    BACKFILL = "backfill"           # Use next known price
```

**Application:**
- Applied during BacktraderAdapter initialization (before validation)
- Default: FORWARD_FILL (most conservative, preserves date range)
- Policy configurable per backtest

**Edge Cases:**
- Gap at start: ERROR (no prior value for forward-fill)
- Gap at end: Forward-fill works, interpolate fails
- Multiple consecutive gaps: Policy applied iteratively

## Consequences

### Positive

✅ **Accurate cost modeling:**
- Commission, spread, slippage separately tracked
- Pluggable models support different brokers/scenarios
- Cost breakdown reveals true strategy profitability

✅ **Observable costs:**
- CostEvent stream enables detailed cost analysis
- Can verify cost calculations independently
- Cost metrics included in performance reports

✅ **Corporate action correctness:**
- Split-adjusted prices prevent distorted returns
- Dividend adjustments capture total return
- OHLC relationships preserved for pattern recognition

✅ **Backward compatible:**
- Default cost models (Zero*) maintain 100% parity
- Existing backtests work unchanged
- Costs are optional (None for legacy results)

✅ **Flexible missing data handling:**
- 5 policies cover common scenarios
- Policy choice makes assumptions explicit
- Fail-fast ERROR mode prevents silent bugs

✅ **Type-safe:**
- Full mypy compliance
- CostEvent immutable (frozen dataclass)
- Protocol-based CostModel interface

### Negative

❌ **Complexity:**
- More configuration options (cost models, missing data policy)
- Cost tracking adds computational overhead (~2-5%)
- More code to maintain and test

❌ **Storage overhead:**
- CostEvent list can be large for high-frequency strategies
- BacktestRunResult JSON files larger when costs included
- Trade-off: observability vs storage

❌ **Adjustment limitations:**
- YFinance Adj Close is pre-calculated (can't verify)
- Spin-offs and mergers not explicitly modeled
- Assumes YFinance adjustments are correct

### Neutral

⚖️ **Performance impact:**
- Cost calculation: ~2-5% overhead (acceptable)
- Adjusted price calculation: ~1% overhead (one-time)
- Overall: < 10% total backtest time increase

⚖️ **YFinance dependency:**
- Relies on YFinance for adjusted prices
- Could add other data sources (Alpha Vantage, etc.)
- Manual adjustment formulas available if needed

⚖️ **Cost model accuracy:**
- Simple models (flat, percentage) are approximations
- Real costs depend on market conditions, order size, volatility
- Good enough for most strategy comparisons

## Implementation Details

### Cost Tracking Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BacktraderAdapter.run()                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Backtrader Cerebro.run()                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Strategy executes, places orders                    │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Broker fills orders at market prices                │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  TradeTracker analyzer captures all fills            │   │
│  │  - Records (timestamp, symbol, qty, price, value)    │   │
│  └────────────────────────┬─────────────────────────────┘   │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              BacktraderAdapter._build_result()               │
│                                                              │
│  For each fill in trade_tracker.fills:                      │
│    commission = commission_model.calculate_cost(...)        │
│    spread = spread_model.calculate_cost(...)                │
│    slippage = slippage_model.calculate_cost(...)            │
│                                                              │
│    cost_events.append(CostEvent(...))                       │
│                                                              │
│  cost_summary = CostSummary(                                │
│    total_commission=sum(commission_events),                 │
│    total_spread=sum(spread_events),                         │
│    total_slippage=sum(slippage_events),                     │
│    cost_events=tuple(cost_events),                          │
│  )                                                           │
│                                                              │
│  return BacktestRunResult(..., costs=cost_summary)          │
└─────────────────────────────────────────────────────────────┘
```

### Adjusted Price Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              BacktraderAdapter.__init__()                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  1. Check for Adj Close column in price_histories           │
│     If present: Apply adjustment                            │
│     If absent: Use data as-is, log warning                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Preserve original Close as Close_Unadjusted             │
│     df["Close_Unadjusted"] = df["Close"]                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Calculate adjustment factor                             │
│     adj_factor = df["Adj Close"] / df["Close_Unadjusted"]   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Apply adjustment to OHLC                                │
│     df["Open"] *= adj_factor                                │
│     df["High"] *= adj_factor                                │
│     df["Low"] *= adj_factor                                 │
│     df["Close"] = df["Adj Close"]                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Apply missing data policy (if configured)               │
│     policy.apply(df)  # forward_fill, drop, error, etc.     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Feed adjusted prices to Backtrader Cerebro              │
│     cerebro.adddata(bt.feeds.PandasData(dataname=df))       │
└─────────────────────────────────────────────────────────────┘
```

### Example Cost Calculations

**Flat Commission ($0.001/share):**
```python
# Buy 1000 shares @ $50
commission = 1000 * 0.001 = $1.00
```

**Percentage Commission (0.1%):**
```python
# Buy 1000 shares @ $50 (trade value = $50,000)
commission = 50000 * 0.001 = $50.00
```

**Percentage Spread (5 bps):**
```python
# Buy 1000 shares @ $50 midpoint
# Execution at bid/ask: $50.025 (0.05% worse than mid)
spread_cost = 1000 * 50 * 0.0005 = $25.00
```

**Sqrt Slippage (market impact):**
```python
# Buy 1000 shares @ $50
# Impact scales with √shares
slippage = 50 * sqrt(1000) * 0.0001 = $0.158
```

## Alternatives Considered

### Alternative 1: Embedded Costs in Fills

Embed cost calculations directly in broker fill logic.

**Rejected because:**
- No cost observability (can't inspect cost breakdown)
- Hard to compare different cost models
- Tightly couples costs to execution
- Can't verify cost calculations independently

### Alternative 2: Single Cost Model

Use one combined cost model instead of separate commission/spread/slippage.

**Rejected because:**
- Less granular cost breakdown
- Can't analyze which costs dominate
- Harder to match specific broker fee schedules
- Loses educational value (understanding cost components)

### Alternative 3: Ignore Corporate Actions

Use unadjusted prices, document limitation.

**Rejected because:**
- Produces misleading backtest results
- Returns calculation incorrect across splits/dividends
- Undermines backtest credibility
- Easy to fix with existing Adj Close data

### Alternative 4: Manual Adjustment Formulas

Implement split/dividend adjustment from scratch.

**Rejected because:**
- YFinance already provides Adj Close
- Complex to implement correctly
- Requires corporate action event data
- Reinventing the wheel
- Can add later if YFinance proves insufficient

### Alternative 5: All-or-Nothing Missing Data

Require complete data, fail on any gap.

**Rejected because:**
- Too restrictive (real data has occasional gaps)
- Makes backtesting fragile
- Policy enum gives users control
- Forward-fill is reasonable default for price data

## Related

- **ADR-005:** Engine-agnostic architecture (cost contracts)
- **ADR-006:** Execution system architecture (cost tracking separate from fills)
- **E3-T1:** Cost model expansion implementation
- **E3-T2:** Corporate action + calendar correctness implementation

## References

- Epic E3 backlog: `docs/planning/backtesting-live-readiness-backlog.md`
- Cost contracts: `finbot/core/contracts/costs.py`
- Cost model implementations: `finbot/services/backtesting/costs/`
- Corporate action tests: `tests/unit/test_corporate_actions.py`
- Adjusted price tests: `tests/unit/test_adjusted_prices.py`
- Missing data tests: `tests/unit/test_missing_data_policies.py`
- User guide: `docs_site/docs/user-guide/corporate-actions-and-data-quality.md`
- Example notebook: `notebooks/cost_models_demo.ipynb`

---

**Last updated:** 2026-02-16
