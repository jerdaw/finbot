# Compute Stats

The `compute_stats` helper converts a backtest value history into a compact
summary table of return, risk, drawdown, and metadata fields.

## What It Does

- records run metadata such as dates, stocks, strategy, broker, and sizer,
- computes return and risk metrics using QuantStats extensions,
- summarizes cash utilization,
- and returns a one-row pandas DataFrame suitable for comparison or export.

## Quick Example

```python
from finbot.services.backtesting.compute_stats import compute_stats

stats = compute_stats(
    value_history=value_history,
    cash_history=cash_history,
    stocks=["SPY", "TLT"],
    strat=strategy_cls,
    strat_kwargs={"rebal_proportions": [0.6, 0.4], "rebal_interval": 63},
    broker=broker_cls,
    broker_kwargs={},
    broker_commission=None,
    sizer=None,
    sizer_kwargs={},
)

print(stats[["CAGR", "Sharpe", "Max Drawdown"]])
```

## API Reference

::: finbot.services.backtesting.compute_stats.compute_stats
options:
show_root_heading: true
show_source: true
heading_level: 3

## See Also

- [BacktestRunner](backtest-runner.md)
- [Trading Strategies](strategies.md)
- [Strategy Backtesting Research](../../../research/strategy-backtesting.md)
