# Backtesting Follow-Through and Adjacent Research Closeout

**Status:** ✅ Complete
**Date:** 2026-04-18
**Roadmap Item:** P10.4 Allocation Backtester and Portfolio Research Workflow
**Related ADRs:** None

## Context

The 2026-04-17 workspace-expansion tranche intentionally left a small set of
high-signal follow-through items open: surfaced cost assumptions, explicit
missing-data handling, walk-forward handoff from a completed backtest, and the
adjacent research workspaces already supported by Finbot's service layer.

This closeout pass completed those items without widening scope into the
deferred long-tail research backlog.

## Implementation Scope

### Backtesting Workflow Follow-Through

- Added configurable missing-data policy handling and estimated trade-friction
  assumptions to the main backtesting request/response surface.
- Surfaced the applied assumptions, estimated cost summary, and missing-data
  handling details directly in the backtesting UI.
- Added a prefilled walk-forward handoff so a completed backtest can move into
  the existing walk-forward page without re-entering the configuration.

### Adjacent Research Workspaces

- Expanded the simulations workspace with a bond-ladder tab and supporting API
  route.
- Expanded the Monte Carlo workspace with a correlated multi-asset tab and API
  route.
- Expanded the optimizer workspace with Pareto and efficient-frontier tabs.
- Added a new `finbot.services.optimization.efficient_frontier` module so the
  efficient-frontier workspace uses a typed service instead of route-local math.

### Validation and Frontend Hardening

- Added focused backend router coverage and import smoke coverage for the new
  routes and modules.
- Extended the mocked browser smoke suite so the new research tabs are covered
  by the existing CI-oriented Playwright path.
- Fixed the walk-forward page's `useSearchParams()` usage so the Next.js 16
  production build succeeds under the required `Suspense` boundary.
- Updated roadmap, archive, AGENTS, and README surfaces so the shipped scope is
  reflected consistently.

## Verification

- `uv run pytest tests/unit/test_web_backend_routers.py -q`
- `uv run pytest tests/unit/test_imports.py -q`
- `cd web/frontend && pnpm typecheck`
- `cd web/frontend && pnpm build`

Browser-workflow depth remains intentionally CI-oriented. The mocked Playwright
smoke suite was expanded during the implementation tranche, but local reruns
are not required for this closeout pass.

## Outcome

- The main backtesting page now carries its remaining workflow follow-through
  instead of punting users to hidden assumptions or manual re-entry.
- The simulations, Monte Carlo, and optimizer routes now expose more of
  Finbot's existing research capability without adding more top-level pages.
- P10.4 is reduced to deferred long-tail research plus the broader frontend
  remaining work on responsive/mobile behavior, deeper browser workflows, and
  production deployment.

## Remaining Follow-Up

- Keep long-tail institutional-style research additions deferred until the core
  frontend finish work is complete.
- Continue broader frontend completion through responsive/mobile fixes, deeper
  browser-flow coverage, and production deployment configuration.
