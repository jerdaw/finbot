# Backtesting Workflow Expansion and Research Workspace Pass

**Status:** ✅ Complete
**Date:** 2026-04-17
**Roadmap Item:** P10.4 Allocation Backtester and Portfolio Research Workflow
**Related ADRs:** None

## Context

The 2026-04-17 competitive-analysis refresh confirmed that Finbot had closed
several surrounding analytics gaps but still trailed testfolio and Portfolio
Visualizer in the core portfolio-backtesting workflow. This pass focused on
turning the existing Next.js backtesting page into a stronger single-run
research workspace instead of adding more disconnected analytics pages.

## Implementation Scope

### Allocation, Benchmark, and Return Inspection

- Expanded the main backtesting page into an editable allocation builder with
  canonical presets for `NoRebalance` and `Rebalance`.
- Added optional benchmark selection, benchmark-relative stats, and overlay
  series in the main backtest result.
- Added monthly and annual return tables plus exportable one-run time-series
  output.

### Experiment and Diagnostics Integration

- Added saved-run experiment persistence from the backtesting page.
- Recorded data snapshot lineage for saved backtests so comparisons can retain
  reproducibility context.
- Added rolling diagnostics and regime-aware summaries to the main backtest
  result without moving users to separate research pages.

### Cashflow Planning and Portfolio Behavior

- Introduced a generic strategy wrapper so recurring contributions,
  recurring withdrawals, and one-time events can be applied without rewriting
  each existing strategy class.
- Added inflation-adjusted value history, a single-path withdrawal-durability
  summary, allocation-history capture, and grouped rebalance logs.
- Exposed the resulting cashflow log, nominal vs real portfolio views,
  allocation drift, and rebalance inspection directly in the main UI.

### Documentation and Roadmap Hygiene

- Preserved the 2026-02-18 competitor-analysis document as historical context
  and recorded the refreshed assessment in a new 2026-04-17 research note.
- Updated the roadmap checklist for the shipped P10.4 slices and archived this
  implementation pass for future handoff/reference.
- Re-verified the human-only authorship policy and the canonical agent-file
  symlink arrangement.

## Verification

- `cd /home/jer/repos/finbot/web/frontend && corepack pnpm typecheck`
- `/home/jer/repos/finbot/.venv/bin/python -m pytest tests/unit/test_web_backend_routers.py -q`
- `/home/jer/repos/finbot/.venv/bin/python -m pytest tests/unit/test_rolling_metrics.py -q`
- `/home/jer/repos/finbot/.venv/bin/python -m pytest tests/unit/test_backtest_runner_e2e.py -q`
- `/home/jer/repos/finbot/.venv/bin/python -m pytest tests/unit/test_imports.py -q`

Playwright was intentionally not run locally. The repo already scopes browser
workflow depth to GitHub Actions while the project remains on the free-tier CI
budget.

## Outcome

- Finbot's main backtesting page now behaves much more like a portfolio
  research workspace instead of a narrow strategy runner.
- The implementation reused existing service-layer analytics and added a thin
  generic strategy wrapper, preserving backward compatibility while surfacing
  more of Finbot's underlying moat.
- P10.4 remains open, but the highest-priority workflow slices from the
  competitor analysis are now shipped and validated.

## Follow-Up Status

- The originally deferred cost-assumption, missing-data, walk-forward, and
  adjacent research-surface items were completed in
  `docs/planning/archive/backtesting-followthrough-and-adjacent-research-closeout-2026-04-18.md`.
- The remaining deferred scope is the long-tail suite expansion kept out of
  P10.4 until the core workflow, responsive/mobile work, and deployment pass are
  finished.
