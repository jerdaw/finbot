# Mypy Strict Module Tracker

Tracks package scopes where stricter function-signature rules are enforced.

## Enforced Scopes

The following module scopes are enforced via `pyproject.toml` overrides:

1. `finbot.core.*`
2. `finbot.services.execution.*`
3. `finbot.services.backtesting.*`
4. `finbot.libs.api_manager.*`
5. `finbot.libs.logger.*`
6. `finbot.services.data_quality.*`
7. `finbot.services.health_economics.*`
8. `finbot.services.optimization.*`
9. `finbot.utils.request_utils.*`
10. `finbot.utils.pandas_utils.*`

Enforced flags:

- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`

## Current Status (2026-02-20)

| Scope | Strict Status | Notes |
| --- | --- | --- |
| `finbot.core.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.execution.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.backtesting.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.libs.api_manager.*` | ✅ Enabled | Typed APIs/resource groups/manager helpers |
| `finbot.libs.logger.*` | ✅ Enabled | Typed formatters/audit/queue setup helpers |
| `finbot.services.data_quality.*` | ✅ Enabled | Validators and freshness checks pass strict signatures |
| `finbot.services.health_economics.*` | ✅ Enabled | QALY/CEA/optimization service signatures clean |
| `finbot.services.optimization.*` | ✅ Enabled | DCA optimizer helper signatures completed |
| `finbot.utils.request_utils.*` | ✅ Enabled | Request handler + retry config signatures hardened |
| `finbot.utils.pandas_utils.*` | ✅ Enabled | Typed loader/saver/frequency/sorting helper signatures |
| `finbot.utils.*` | ⏳ Pending | Large legacy surface; staged rollout needed |

## Policy for New Code

For new modules in strict-enabled namespaces:

1. All function signatures must include argument and return types.
2. Partial signatures are not allowed.
3. New `# type: ignore` comments require justification and should be scoped narrowly.
4. Changes should keep `uv run mypy finbot/` clean.

For new modules outside strict-enabled namespaces:

1. Prefer complete signatures by default.
2. If untyped signatures are introduced for practical reasons, add a follow-up task to type them.

## Validation Commands

```bash
uv run mypy finbot/
uv run mypy \
  finbot/libs/api_manager \
  finbot/libs/logger \
  finbot/services/data_quality \
  finbot/services/health_economics \
  finbot/services/optimization \
  finbot/utils/request_utils \
  finbot/utils/pandas_utils \
  --disallow-untyped-defs --disallow-incomplete-defs
```
