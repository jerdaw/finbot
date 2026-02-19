# Data Quality Guide

This guide covers data freshness monitoring and operational response using Finbot's data quality service.

## Core components

- Registry: `finbot/services/data_quality/data_source_registry.py`
- Freshness checker: `finbot/services/data_quality/check_data_freshness.py`
- DataFrame validator: `finbot/services/data_quality/validate_dataframe.py`
- CLI entrypoint: `finbot status`

## Routine checks

Run a full freshness check:

```bash
uv run finbot status
```

Only show stale sources:

```bash
uv run finbot status --stale-only
```

## How to interpret status output

Each source includes:

- file count
- total size
- latest update timestamp
- data age
- stale/ok status

A source is stale when age exceeds its configured max age in the registry.

## Recommended operating cadence

1. Check `finbot status` daily.
2. Run `finbot update` when stale sources are detected.
3. Re-run `finbot status --stale-only` to verify recovery.
4. Investigate repeated failures with CLI/pipeline logs and trace IDs.

## Incident triage

When stale data persists:

1. Confirm environment variables and API keys are set.
2. Run targeted collectors manually to isolate failing source.
3. Review JSONL logs for `error_type` and failing operation.
4. Re-run update pipeline after remediation.

## Validation and schema checks

For batch data validation, use `validate_dataframe.py` in service-level workflows to detect:

- empty files
- missing columns
- duplicates
- null-heavy columns

## Follow-up actions

- Add alerting hooks (future): report stale sources to external channels.
- Add scheduled quality report generation in CI-heavy workflow (future).
