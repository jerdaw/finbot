# Audit Logging Guide

This guide describes Finbot's structured audit trail format and how to use trace IDs across CLI and automation workflows.

## What gets logged

Audit events are emitted with these fields:

- `timestamp`
- `trace_id`
- `operation`
- `component`
- `outcome` (`success` / `failure` / `partial`)
- `duration_ms`
- `parameters_hash`
- `error_type` (when failure)

Audit events are written into the JSONL log stream (`logs/<logger>.log.jsonl`).

## Trace IDs

`finbot` CLI now supports an optional root `--trace-id` option. If omitted, a trace ID is generated automatically.

Examples:

```bash
finbot --trace-id run-20260219-001 status
finbot --trace-id run-20260219-002 backtest --strategy Rebalance --asset SPY
```

## Sensitive data handling

Raw command parameters are not logged directly in audit fields.

- A deterministic hash is stored in `parameters_hash`.
- Sensitive key names (`token`, `password`, `secret`, `api_key`, etc.) are redacted before hashing.

## CLI operations instrumented

- `simulate`
- `backtest`
- `optimize`
- `update`
- `status`
- `dashboard`

## Daily pipeline instrumentation

`scripts/update_daily.py` emits:

- one pipeline-level event (`update_daily`)
- one step-level event per retry attempt (`update_daily_step`)

## Operational usage

1. Pick a trace ID per run and pass it at CLI root.
2. Filter JSONL logs by `trace_id`.
3. Correlate failures by `operation` + `error_type` + `parameters_hash`.
4. Use retry attempt records for incident analysis in update pipelines.
