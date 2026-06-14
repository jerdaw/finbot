# Stable Baseline Restart Guide

**Baseline date:** 2026-06-14

This guide records the state to return to if Finbot sits dormant for an
extended period.

## Baseline State

- `main` is the canonical development branch.
- The intended stable release tag is `v2026.06-stable`.
- Priorities P0-P12 are complete for the stable baseline.
- Backtrader remains the primary portfolio backtesting engine.
- NautilusTrader remains available for experimental/live-readiness exploration;
  ADR-011 keeps the production adoption decision deferred.
- The generated documentation site builds with Zensical using `mkdocs.yml` as a
  compatibility configuration file.
- The Next.js frontend has a completed 12-page research workspace baseline,
  including the decomposed backtesting route and local backtesting components.

## First Commands When Restarting

```bash
uv sync --all-extras
uv run pytest tests/unit/test_data_quality.py tests/unit/test_path_constants.py -q
uv run zensical build --clean --strict
cd web/frontend && corepack pnpm install
cd web/frontend && corepack pnpm typecheck
```

Do not run local Playwright browser tests by default. Keep those in GitHub CI
unless there is a specific browser workflow regression to debug.

## Where To Look First

- Current status and future backlog: `docs/planning/roadmap.md`
- Stable closeout record:
  `docs/planning/archive/stable-baseline-closeout-2026-06-14.md`
- Docs-platform decision: `docs/adr/ADR-016-zensical-docs-platform.md`
- Backtesting engine decision: `docs/adr/ADR-011-nautilus-decision.md`
- Frontend architecture entry points: `AGENTS.md`
- Backtesting frontend route:
  `web/frontend/src/app/backtesting/page.tsx`

## Deferred Work That Should Not Block The Baseline

- External simulation validation against trusted historical baselines, pending
  durable source data and comparison outputs.
- Human-approved logo or brand-guide work.
- Manual videos, poster, and narration-driven public media.
- Published-history rewrite work; use the existing conventional-commit guide for
  future work instead of force-rewriting old history.
- Broad dependency updates while GitHub Actions minutes are constrained; replay
  narrow dependency updates on human-reviewed branches.
- Production hosting, public domain/TLS, and secret-management decisions.
- Phase-2 real-time streaming, live execution, and intraday bar caching.

## Safe First Future Work

1. Re-enable narrow dependency maintenance once CI budget allows it.
2. Refresh local and CI validation against the current Python/Node ecosystem.
3. Pick one new product goal and create a fresh roadmap plan before coding.
4. Keep P0-P12 historical scope closed unless a new goal explicitly reopens it.
