# Snapshot Replay Guide

This guide explains how to run a backtest from a pinned snapshot ID for deterministic reproducibility.

## Prerequisites

- A `DataSnapshotRegistry` with at least one snapshot.
- `BacktraderAdapter` configured with:
  - `snapshot_registry=...`
  - `enable_snapshot_replay=True`

## Example

```python
import pandas as pd

from finbot.core.contracts import BacktestRunRequest
from finbot.services.backtesting.adapters import BacktraderAdapter
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry

registry = DataSnapshotRegistry("finbot/data/backtests/snapshots")
adapter = BacktraderAdapter(
    price_histories={},
    snapshot_registry=registry,
    enable_snapshot_replay=True,
)

request = BacktestRunRequest(
    strategy_name="NoRebalance",
    symbols=("SPY",),
    start=pd.Timestamp("2019-01-01"),
    end=pd.Timestamp("2020-12-31"),
    initial_cash=100_000.0,
    parameters={"equity_proportions": [1.0]},
    data_snapshot_id="snap-abc123...",
)

result = adapter.run(request)
print(result.metadata.data_snapshot_id)
```

## Replay Behavior

- If `enable_snapshot_replay=True` and `request.data_snapshot_id` is set, the adapter loads bars from the snapshot.
- If replay is enabled but no request snapshot is set, the adapter uses in-memory histories.
- `auto_snapshot` is skipped during replay mode for that run.

## Failure Modes

- Missing registry with replay enabled: `ValueError`
- Unknown snapshot ID: `FileNotFoundError`
- Missing symbol in snapshot payload: `ValueError`

## Notes

- Replay is opt-in and does not change default backtesting behavior.
- Use replay mode for research reproducibility and auditability workflows.
