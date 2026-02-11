# ADR-004: Consolidate Package Layout

## Status

Accepted

## Date

2026-02-11

## Context

The project had four top-level Python packages in `pyproject.toml`:

```toml
packages = [
    { include = "finbot" },
    { include = "config" },
    { include = "constants" },
    { include = "libs" },
]
```

This caused several issues:
- **Import ambiguity**: `from config import ...` could collide with stdlib or third-party `config` modules
- **Non-standard layout**: Python best practice is a single top-level package namespace
- **Tooling friction**: Type checkers, linters, and IDE auto-importers work best with a single namespace
- **Deployment complexity**: Packaging multiple top-level packages for distribution is error-prone

## Decision

Move `config/`, `constants/`, and `libs/` under the `finbot/` package as subpackages:

```
finbot/
  config/       (was top-level config/)
  constants/    (was top-level constants/)
  libs/         (was top-level libs/)
  services/
  utils/
  ...
```

All imports updated from `from config import ...` to `from finbot.config import ...` (and similarly for `constants` and `libs`).

## Consequences

### Positive
- Single `finbot` namespace — clean, standard Python package layout
- No import collisions with external packages
- Simpler `pyproject.toml` with one package entry
- Better IDE support for auto-imports and go-to-definition

### Negative
- ~120 import statements updated across ~100 files (one-time migration cost)
- `path_constants.py` ROOT_DIR resolution changed (one extra `.parent` level)

### Migration Details
- All `from config ` → `from finbot.config `
- All `from constants ` → `from finbot.constants `
- All `from libs ` → `from finbot.libs `
- `pyproject.toml` packages reduced to `[{ include = "finbot" }]`
- `path_constants.py` variable ordering reorganized (FINBOT_DIR before CONFIG_DIR)
