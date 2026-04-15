# Audit Remediation and Frontend Hardening

**Status:** ✅ Complete
**Date:** 2026-04-15
**Roadmap Item:** P10.2
**Related ADRs:** `docs/adr/ADR-014-runtime-surfaces-and-image-specific-dependencies.md`, `docs/adr/ADR-015-nextjs-frontend-completion.md`

## Context

The post-P10.1 audit identified four concrete quality gaps:

1. Frequency-aware missing-date detection chose the wrong fallback business day.
2. `uv run mypy finbot/` was no longer green on the pinned toolchain.
3. Host probing still ran eagerly on the settings import path.
4. The Next.js frontend had no automated build/type/browser gate despite now being a first-class product surface.

This batch was scoped to fix those issues without broadening into unrelated feature work.

## Implementation Scope

### Datetime Correctness

- Correct the frequency-aware comparator in `get_missing_us_business_dates()`.
- Add focused weekly, monthly, and yearly regression tests for `detect_frequency=True`.

### Type and Import Hardening

- Refactor dashboard pages so mypy can see non-optional values after Streamlit stop paths.
- Limit Nautilus typing workarounds to narrow inline ignores on the three `StrategyConfig` subclasses that depend on third-party typing gaps.
- Replace eager host snapshot construction with `get_current_host_info()`, a cached accessor that tolerates missing DNS, subprocess, and psutil data.

### Frontend Quality Gate

- Add `pnpm typecheck` and `pnpm test:e2e`.
- Add mocked Playwright smoke coverage for the dashboard landing page, all 12 frontend routes, and one mobile navigation path.
- Add a `frontend-quality` CI job that runs typecheck, build, and browser smoke tests.
- Constrain that job to frontend-relevant file changes so browser minutes are not spent on Python-only changes while the repository remains on the GitHub free tier.

## Verification

- `/home/jer/.local/bin/uv run ruff check finbot web tests .github`
- `/home/jer/.local/bin/uv run mypy finbot/`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_datetime_utils.py tests/unit/test_config.py -q --capture=no`
- `cd web/frontend && corepack pnpm typecheck`
- `cd web/frontend && NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api corepack pnpm build`

## Outcome

- Frequency-aware gap detection now selects the correct last business day at or before each expected anchor.
- The Python codebase is back to a clean mypy baseline on the pinned toolchain.
- Settings initialization no longer depends on eager hostname/IP/CPU probing succeeding.
- The Next.js frontend now has deterministic mocked browser smoke coverage and a CI gate that is practical to keep enabled on a limited Actions budget.
