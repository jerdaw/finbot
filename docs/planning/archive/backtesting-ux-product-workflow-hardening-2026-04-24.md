# Backtesting UX and Product Workflow Hardening Implementation Plan

**Status:** Implemented in the 2026-04-24 autonomous pass; follow-up polish can continue from validation evidence below
**Created:** 2026-04-24
**Roadmap Item:** P12 Backtesting UX and Product Workflow Hardening
**Primary Surface:** `web/frontend/src/app/backtesting/page.tsx`
**Related Evidence:** Manual Finbot/testfol.io review on 2026-04-24

## Goal

Turn the backtesting page from a capable single-run research report into a
trustworthy portfolio backtesting workspace:

- Correct and consistent metrics across cards, full stats, tables, and charts.
- Fast portfolio construction with presets, clear allocation editing, and
  multi-portfolio comparison.
- Results organized for investigation instead of one long scroll.
- Shareable/reusable run configurations and richer chart interactions.
- Mobile behavior that remains useful with dense result data.

## Non-Goals

- Redesigning the whole Finbot shell, navigation, or visual identity.
- Replacing Backtrader as the default engine.
- Adding live trading, broker execution, or intraday data workflows.
- Matching testfol.io visually. testfol.io is a workflow reference, not a
  visual design target.
- Moving all advanced analytics into backtesting. Existing dedicated pages
  should remain dedicated pages where they are the better workflow.

## Current Baseline

### Strengths To Preserve

- Auditability: surfaced execution frictions, missing-data policy, walk-forward
  handoff, cashflow durability, allocation drift, rebalance logs, trades, and
  full stats.
- Existing exports: CSV/JSON and saved experiment flow.
- Backend is already rich enough for many display changes without immediate
  service rewrites.
- Mocked Chromium workflow coverage already exists for the backtesting page.

### Confirmed Problems

- The summary `Max Drawdown` card can disagree materially with the drawdown
  chart and full result interpretation. Manual review saw `-90.84%` in the card
  while the chart bottomed near `-34%`.
- The post-run UI is a long vertical report. This hides high-value sections and
  makes mobile review painful.
- Portfolio setup feels like a parameter form, not a portfolio construction
  workspace.
- Presets exist but are shallow and not discoverable compared with public
  backtesters.
- Users cannot compare multiple portfolios in one run.
- Chart controls are minimal: no obvious log-scale toggle, benchmark overlay
  controls, series visibility, or per-chart download affordances.
- Mobile tables are very long and often clipped or hard to scan.
- The educational disclaimer modal blocks first use and can feel heavier than
  necessary after acknowledgement.

## Implementation Order

This plan is intentionally sequenced. Do not start with broad UI refactors until
metric correctness is fixed, because incorrect top-line results undermine every
later UI improvement.

1. P12.1 Metric trust and correctness.
2. P12.2 Results workspace structure.
3. P12.3 Portfolio builder and presets.
4. P12.3 multi-portfolio comparison.
5. P12.4 sharing/export/chart controls.
6. P12.5 mobile and dense-output ergonomics.
7. Final product polish, docs, and browser regression pass.

## Execution Guardrails

- **Metric trust is a hard gate:** Workstreams 2-7 should not ship user-visible
  product changes until Workstream 1 is complete or the remaining metric issue
  is explicitly scoped and documented as non-blocking.
- **Architecture work must stay bounded:** Workstream 0 exists to make later
  changes safer, not to redesign the page. Stop extraction once the next
  milestone can be implemented safely.
- **Comparison ships in two phases:** Start with frontend orchestration over the
  existing `/api/backtesting/run` endpoint. Add a backend batch endpoint only if
  runtime, error handling, or auditability requires it.
- **Presets must be honest:** Do not silently substitute simulated,
  unavailable, or methodology-specific assets. Preset cards must label their
  assumptions and limitations.
- **Chart controls are intentionally minimal:** Ship log scale, benchmark/series
  visibility, tooltip inspection, and data/image download for core charts before
  considering advanced chart-builder behavior.
- **Mobile is a structure test:** Mobile work should validate the information
  architecture and dense-output patterns, not become a separate visual redesign.

## Autonomous Execution Contract

This section defines how an autonomous coding agent should execute the whole
plan when asked to "implement P12" or "implement the backtesting UX plan."

### Default Autonomy Level

- Proceed without asking for confirmation for implementation details that are
  already constrained by this plan.
- Prefer finishing the next dependency-unblocked milestone over pausing for
  design preference questions.
- Use existing project patterns, components, and API conventions unless a new
  abstraction clearly reduces risk or duplication.
- Keep all changes in the shared working tree; do not revert unrelated user or
  prior-agent changes.
- Make incremental, testable changes. Each milestone should leave the app in a
  runnable state.

### Default Decisions

Use these defaults unless the user gives a newer conflicting instruction:

| Decision Area | Default |
| :------------ | :------ |
| Result navigation | Use tabs for top-level result groups, with a compact sticky summary above them. |
| Component location | Prefer `web/frontend/src/app/backtesting/components/` for backtesting-specific components; promote to `src/components/` only when reused elsewhere. |
| State management | Keep state in `page.tsx` or a local hook until multi-portfolio state becomes unwieldy; do not introduce a global store unless needed. |
| Multi-portfolio implementation | Use frontend orchestration first; no backend batch endpoint unless Phase 4A proves insufficient. |
| Portfolio cap | Start with 5 portfolios. |
| Preset assumptions | Mark assets as `live/local`, `simulated`, `proxy`, or `unavailable`; block unavailable presets or require explicit replacement. |
| Share links | Start with URL-encoded configuration. Add compression only if URLs become impractically large. |
| Chart controls | Implement only log scale, benchmark/series visibility, tooltip inspection, and data/image download for core charts. |
| Mobile tables | Prefer grouped expandable rows/cards for large result tables; use horizontal scroll only when table structure is essential. |
| Disclaimer | Store acknowledgement in local storage and keep a persistent page-level disclaimer affordance. |
| External parity | Keep opt-in only; never add live testfol.io calls to default CI. |

### Stop Or Ask Conditions

Continue autonomously unless one of these occurs:

- A metric correctness issue cannot be resolved without choosing between two
  incompatible financial methodologies.
- A required dependency, package install, browser runtime, or service is missing
  and no existing repo pattern provides a fallback.
- Implementing the next step would require destructive git operations or
  reverting unrelated changes.
- The API shape would need a breaking change to existing callers.
- A preset requires assets or data that are unavailable and no honest
  simulated/proxy path is already present.
- Validation reveals a likely financial correctness regression that cannot be
  isolated.

When a stop condition occurs, leave the code in the safest runnable state,
document what was completed, document the blocker, and propose the smallest
next decision needed.

### Work Packet Sequence

Execute in these packets. A packet may include several workstreams when they are
small and dependency-compatible, but do not skip the order.

1. **Trust packet:** Workstream 1 metric consistency, tests, and manual default
   backtest verification.
2. **Architecture packet:** Workstream 0 extraction only as much as needed for
   the result workspace and portfolio builder.
3. **Results packet:** Workstream 2 tabs/summary/stale states while preserving
   every current output.
4. **Builder packet:** Workstream 3 improved builder, preset browser, and preset
   assumption labeling.
5. **Comparison packet:** Workstream 4A frontend-orchestrated multi-portfolio
   comparison. Decide whether 4B is still unnecessary.
6. **Reuse packet:** Workstream 5 share links, save/reuse, and export menu.
7. **Chart packet:** Workstream 6 minimal chart controls and downloads.
8. **Mobile packet:** Workstream 7 dense output, mobile navigation, and
   disclaimer friction.
9. **Closeout packet:** Workstream 8 full validation, screenshots, docs,
   roadmap checkoffs, and archive note if the full plan is complete.

### Progress Tracking During Implementation

- Update this plan's milestone checklist or add a short progress note only when
  a milestone is actually complete or explicitly deferred.
- Keep roadmap status honest:
  - `PLANNED` before implementation starts.
  - `IN PROGRESS` once code work starts.
  - `COMPLETE` only after Definition of Done is met.
- If a milestone is partially complete at the end of a coding session, document:
  - completed files/features
  - validation run
  - remaining tasks
  - known blockers
  - safest next command/test

### Validation Ladder

Use the cheapest relevant validation first, then widen as the blast radius grows:

1. Targeted Python unit tests for backend metric/schema changes.
2. `cd web/frontend && corepack pnpm typecheck` for frontend changes.
3. Targeted mocked Playwright tests for changed backtesting workflows.
4. Manual desktop/mobile browser screenshots for major UI milestones.
5. Opt-in testfol.io parity only after metric or external-comparison changes.
6. Broader test/build commands only when shared contracts, components, or routes
   were changed.

### Autonomous Closeout Format

At the end of any implementation run, report:

- completed milestones
- files changed by this run
- validation commands and outcomes
- screenshots captured, if any
- deferred items with rationale
- next safest milestone if the plan is not complete

## Phase Completion Criteria Matrix

Each phase is complete only when the listed implementation, test, and manual
review criteria are met. If any item is deferred, the closeout note must name
the deferral, rationale, and follow-up owner/scope.

| Phase | Complete When |
| :---- | :------------ |
| Workstream 0: Architecture Stabilization | Backtesting page behavior is unchanged, helpers/components are extracted, `corepack pnpm typecheck` passes, and existing mocked backtesting Playwright flows still pass. |
| Workstream 1: Metric Trust | Summary cards, full stats, chart-derived values, and exports agree for max drawdown and other headline metrics; backend unit tests and frontend mocked browser assertions protect the consistency. |
| Workstream 2: Results Workspace | Every existing result section is reachable from a tab or sticky section nav, stale/loading/error/success states are visible, and no current result data is removed. |
| Workstream 3: Portfolio Builder and Presets | Users can load/edit at least the required starter presets, invalid weights block runs with clear messages, and a 60/40 run can be configured without hidden strategy-parameter editing. |
| Workstream 4: Multi-Portfolio Comparison | Users can run at least two portfolios over one shared configuration, compare headline metrics and core charts, and inspect individual portfolio details without losing partial successes. |
| Workstream 5: Sharing, Export, and Reuse | A copied link round-trips the visible configuration, saved portfolios can be reused, and export options cover run JSON, value history, returns, trades, and comparison data where applicable. |
| Workstream 6: Chart Interaction | Core charts support the required toggles/downloads, preserve source data, and are manually verified on desktop and mobile screenshots. |
| Workstream 7: Mobile and Dense Data | A 390px-wide backtest run is navigable without scrolling through hundreds of rows, tables have card/expand/scroll affordances, and the disclaimer does not block repeat use after acknowledgement. |
| Workstream 8: Testing and Verification | Backend tests, frontend typecheck, mocked Playwright coverage, manual screenshots, and opt-in external parity guidance are recorded in the closeout note. |

## Workstream 0: Stabilize Backtesting Page Architecture

**Purpose:** De-risk the large existing page before feature work.

**Scope Constraint:** This workstream is complete when the page is safe enough
for the next milestone. Do not continue extracting components just to reduce
file size once behavior-preserving extraction has served that purpose.

### Files

- `web/frontend/src/app/backtesting/page.tsx`
- New local or shared components under one of:
  - `web/frontend/src/app/backtesting/components/`
  - `web/frontend/src/components/backtesting/`
- `web/frontend/src/types/api.ts`

### Tasks

- Extract pure helpers from `page.tsx` into local modules:
  - request construction
  - preset definitions
  - export construction
  - chart data transforms
  - allocation drift transforms
  - result metric normalization
- Split presentational sections into components:
  - `BacktestConfigurationPanel`
  - `PortfolioBuilder`
  - `BacktestResultSummary`
  - `BacktestResultWorkspace`
  - `AssumptionsPanel`
  - `ReturnsPanel`
  - `TradesPanel`
  - `AllocationPanel`
- Keep state ownership in the page until behavior is stable. Move to a store
  only if prop threading becomes the main complexity.
- Preserve current route behavior while introducing components incrementally.

### Completion Criteria

- No behavior change after extraction.
- `corepack pnpm typecheck` passes.
- Existing mocked backtesting Playwright flows pass unchanged.
- New components have stable, accessible headings and button names for tests.
- `page.tsx` remains the state owner unless a store is intentionally introduced
  and documented.
- The extracted helpers are covered by existing behavior tests or direct unit
  tests where they contain nontrivial logic.
- A short closeout note or PR summary states what was intentionally left in
  `page.tsx` to avoid refactor creep.

## Workstream 1: Metric Trust and Correctness

**Purpose:** Fix the max-drawdown mismatch and prevent future metric drift.

**Gate:** This workstream blocks user-visible P12 product changes. Later
workstreams may be prototyped locally, but they should not be considered
complete until headline metric consistency is fixed and covered.

### Files

- `finbot/services/backtesting/compute_stats.py`
- `web/backend/routers/backtesting.py`
- `web/backend/schemas/backtesting.py`
- `web/frontend/src/app/backtesting/page.tsx`
- `web/frontend/src/types/api.ts`
- `tests/unit/test_backtest_runner_e2e.py`
- `tests/unit/test_web_backend_routers.py`
- `web/frontend/tests/e2e/app-smoke.spec.ts`

### Tasks

- Audit how each displayed metric is computed:
  - `stats["Max Drawdown"]`
  - drawdown chart series
  - full statistics table
  - result summary cards
  - exported CSV/JSON
- Fix `compute_stats.py` so max drawdown is computed from portfolio value levels
  using a single helper, for example:
  - cumulative peak: `value / value.cummax() - 1`
  - max drawdown: minimum of that series
- Add or reuse a canonical helper for drawdown series generation so backend
  stats and chart transforms share the same basis.
- Normalize percent formatting in frontend cards so all percentage metrics use
  consistent sign and scale.
- Add backend response fields only if needed to avoid recomputing critical
  metrics differently in the frontend.
- Add regression tests with deterministic price data where expected drawdown is
  known.
- Extend mocked Playwright response to include a drawdown value that should
  match the chart-derived value, then assert visible consistency.

### Completion Criteria

- Summary max drawdown, full statistics max drawdown, and chart minimum agree
  within a documented tolerance.
- The default SPY page run no longer shows a trust-breaking mismatch.
- Finbot/testfol.io parity test remains useful; any tolerance update is
  documented in the test file.
- At least one deterministic backend test validates a known drawdown path.
- At least one mocked frontend/browser test asserts the visible result card and
  chart-backed/full-stat value use the same normalized metric.
- The closeout note documents the canonical metric basis for max drawdown and
  whether the metric is computed from value levels, returns, or a shared helper.

## Workstream 2: Results Workspace

**Purpose:** Convert the result experience from a long report into a workspace.

### Files

- `web/frontend/src/app/backtesting/page.tsx`
- `web/frontend/src/components/ui/tabs.tsx`
- `web/frontend/src/components/common/stat-card.tsx`
- `web/frontend/src/components/common/chart-card.tsx`
- `web/frontend/src/components/common/data-table.tsx`
- New backtesting result components from Workstream 0.

### Target Result Tabs

- `Summary`: headline metrics, portfolio value, drawdown, benchmark delta,
  success/stale state, run metadata.
- `Charts`: value, real value, drawdown, benchmark overlay, rolling diagnostics.
- `Returns`: monthly and annual returns.
- `Risk`: rolling metrics, regime summaries, drawdown episodes if available.
- `Allocation`: allocation drift, latest weights, rebalance log.
- `Trades`: trades, cashflow events, cost events.
- `Assumptions`: missing data, cost model, methodology, request payload summary.
- `Full Stats`: complete raw metrics table for power users.

### Tasks

- Add a sticky or near-top result summary header after successful run.
- Group existing output cards and tables into tabs without deleting data.
- Add stale-run detection:
  - If inputs change after a run, show "Inputs changed since last run".
  - Keep previous results visible but mark them stale until rerun.
- Preserve export and save actions at the result level.
- Add a compact "Run complete" state with runtime, date range, portfolio count,
  data source assumption, and run id if available.
- Ensure tab labels are short enough for desktop and mobile.

### Completion Criteria

- After running a backtest, users can reach every current result section without
  scrolling through unrelated tables.
- Result tabs are keyboard accessible.
- Existing exports and save experiment actions still work.
- Mobile shows navigable result sections without a single endless table-first
  page.
- Inputs changed after a run produce a visible stale-result state.
- The Summary, Charts, Returns, Risk, Allocation, Trades, Assumptions, and Full
  Stats destinations are present or explicitly deferred in the closeout note.

## Workstream 3: Portfolio Builder and Preset Browser

**Purpose:** Make the input side feel like building portfolios, not filling a
generic strategy form.

**Preset Integrity Rule:** Every preset must use available assets directly or
clearly mark any simulated ticker, proxy, or methodology limitation before the
user runs it.

### Files

- `web/frontend/src/app/backtesting/page.tsx`
- New `PortfolioBuilder` and `PresetBrowser` components.
- `web/frontend/src/lib/constants.ts` or a new
  `web/frontend/src/app/backtesting/presets.ts`
- `web/backend/schemas/backtesting.py` if request metadata needs expansion.

### Presets

Start with common allocations:

- SPY buy-and-hold
- 60/40
- Three Fund
- All Weather
- Golden Butterfly
- Permanent Portfolio
- HFEA
- Risk-parity starter
- Equal-weight custom basket

Each preset should define:

- label
- description
- assets and target weights
- suggested strategy
- rebalance frequency or interval
- benchmark suggestion
- notes/assumptions if it uses simulated or unavailable tickers
- data availability status: live/local, simulated, proxy, or unavailable

### Tasks

- Build a searchable preset browser modal or panel.
- Show preset cards with asset chips and weight summaries.
- Add better asset rows:
  - ticker
  - target weight
  - delete
  - duplicate
  - validation state
- Keep total weight visible and always explain why Run is disabled.
- Add quick actions:
  - equal weight
  - normalize to 100%
  - clear
  - duplicate portfolio
- Add portfolio-level settings:
  - rebalance frequency
  - benchmark
  - drag/fee assumptions
  - optional rebalance bands when supported
- Keep simple defaults visible for users who just want a fast run.

### Completion Criteria

- A user can create or load a 60/40 allocation without manually editing hidden
  strategy parameters.
- Weight validation is visible, specific, and blocks invalid runs.
- Preset selection is reversible and editable.
- Existing one-run behavior remains available.
- The initial preset set includes SPY buy-and-hold, 60/40, Three Fund, All
  Weather, Golden Butterfly, Permanent Portfolio, HFEA, and Equal Weight, or the
  closeout note documents why any named preset was deferred.
- The mocked browser suite covers selecting a preset, editing one weight, and
  running the resulting backtest.
- Preset cards visibly disclose simulated/proxy/unavailable assets before the
  run button is used.

## Workstream 4: Multi-Portfolio Comparison

**Purpose:** Close the largest workflow gap against public backtesting tools.

### Backend Options

Start with the least risky path:

1. Frontend orchestrates multiple existing `/api/backtesting/run` requests and
   merges the results.
2. If that becomes too slow or hard to audit, add a backend batch endpoint.

### Phase 4A: Frontend-Orchestrated Comparison

- Use the existing single-run endpoint for each portfolio.
- Cap the initial UI at a practical limit, such as 5 portfolios.
- Show per-portfolio success, loading, and failure states.
- Merge successful responses into comparison charts/tables.
- Preserve single-run detail views for each successful portfolio.

### Phase 4B: Optional Backend Batch Endpoint

Add this only if Phase 4A exposes a concrete need:

- too many client-side round trips
- inconsistent error handling
- inability to produce a trustworthy shared data-snapshot/audit record
- unacceptable frontend complexity

If added, define a feature-compatible batch schema rather than breaking the
existing single-run endpoint.

### Files

- `web/backend/routers/backtesting.py`
- `web/backend/schemas/backtesting.py`
- `web/frontend/src/app/backtesting/page.tsx`
- `web/frontend/src/types/api.ts`
- `tests/unit/test_web_backend_routers.py`
- `web/frontend/tests/e2e/app-smoke.spec.ts`

### Tasks

- Add a `PortfolioConfig` frontend model:
  - id
  - name
  - assets
  - strategy
  - rebalance settings
  - costs/drag assumptions
  - benchmark
- Allow 1-N portfolios in the UI, with a practical local cap such as 5.
- Run all selected portfolios with the same date/cash/cashflow assumptions.
- Create comparison outputs:
  - metric comparison table
  - combined equity curve
  - combined drawdown
  - CAGR vs drawdown scatter
  - correlation/beta table if backend data supports it
- Preserve single-run details by letting users drill into one portfolio's tabs.
- Add request cancellation or disable repeated submissions while batch is in
  flight.

### Completion Criteria

- Phase 4A lets users compare at least two portfolios in one workflow.
- Comparison charts have clear series labels and visible toggles.
- A failed portfolio run does not discard successful portfolio results; failures
  are shown per portfolio.
- Existing single-run tests continue to pass.
- Comparison output includes at minimum a metric table, combined equity curve,
  and combined drawdown view.
- The UI clearly identifies shared settings versus per-portfolio settings.
- Tests cover a mixed success/failure comparison response.
- If Phase 4B is deferred, the closeout note states why frontend orchestration
  remains sufficient.

## Workstream 5: Sharing, Export, and Reuse

**Purpose:** Make successful work portable and repeatable.

### Files

- `web/frontend/src/app/backtesting/page.tsx`
- `web/frontend/src/lib/api.ts`
- `web/backend/routers/experiments.py`
- `web/backend/schemas/experiments.py`
- `web/backend/routers/backtesting.py` if server-side decode/encode helpers are
  added.

### Tasks

- Add shareable configuration links:
  - encode request/config state into URL query or compressed payload
  - support loading that state on page open
  - do not encode secrets or local file paths
- Add "Copy Link" for the current configuration and optionally completed run.
- Add "Save as preset" or "Save portfolio" path for successful allocations.
- Make CSV/JSON export more task-specific:
  - full run JSON
  - value history CSV
  - returns CSV
  - trades CSV
  - comparison CSV for multi-portfolio runs
- Include methodology/assumption metadata in exported JSON.

### Completion Criteria

- A copied link reconstructs the same visible configuration.
- Saved/reused portfolios can be loaded without manually re-entering tickers and
  weights.
- Export filenames remain deterministic and readable.
- Exports do not include API keys or user-local secrets.
- Share-link round-trip is covered by a mocked browser test or focused frontend
  unit test.
- Export payloads include methodology/assumption metadata for completed runs.

## Workstream 6: Chart Interaction

**Purpose:** Make charts investigable, not just decorative.

**Scope Constraint:** Do not build a generalized chart studio. This workstream
only covers controls required to inspect and export core backtesting charts.

### Files

- `web/frontend/src/components/charts/line-chart-wrapper.tsx`
- `web/frontend/src/components/charts/drawdown-chart.tsx`
- `web/frontend/src/components/charts/lightweight-chart.tsx`
- `web/frontend/src/components/common/chart-card.tsx`
- Backtesting result chart components.

### Tasks

- Add per-chart toolbar controls:
  - log scale where meaningful
  - show/hide benchmark
  - show/hide inflation-adjusted line
  - show/hide individual portfolio series
  - download image/data
- Improve date formatting and tick density.
- Add tooltips that show date, portfolio value, return/drawdown, and benchmark
  value when available.
- Keep chart heights responsive:
  - desktop: large investigation canvas
  - mobile: compact but readable
- Use stable dimensions to prevent layout jumps during loading and data changes.

### Completion Criteria

- Charts remain readable on 390px mobile and 1440px desktop.
- Users can inspect exact values via tooltip.
- Users can download chart data for at least value and returns charts.
- Benchmark/series toggles do not mutate the underlying run result.
- Value, drawdown, and comparison charts each expose the relevant toolbar
  controls or document why a control does not apply.
- Manual screenshots for desktop and mobile are captured during closeout.
- Advanced chart-builder features such as arbitrary indicators, custom chart
  formulas, and cross-page chart composition are explicitly out of scope unless
  added to a later roadmap item.

## Workstream 7: Mobile and Dense Data

**Purpose:** Make the page useful on phones despite dense financial outputs.

**Scope Constraint:** Mobile work should reuse the same information architecture
as desktop. Do not create a separate mobile-only product path unless the shared
structure cannot support the workflow.

### Files

- `web/frontend/src/components/common/data-table.tsx`
- `web/frontend/src/app/backtesting/page.tsx`
- Backtesting result table components.
- `web/frontend/src/app/globals.css`

### Tasks

- Add a compact table mode or card mode for narrow screens.
- For large tables, default to:
  - first N rows plus expand
  - year grouping for monthly returns
  - horizontally scrollable table with a visible scroll affordance when card mode
    is not appropriate
- Use section tabs or segmented controls that remain reachable without scrolling
  past every prior result.
- Ensure top action buttons wrap cleanly and do not overflow.
- Reduce first-load modal friction:
  - store acknowledgement in local storage
  - keep a visible disclaimer/access link in the page shell
  - avoid blocking repeat visits after acknowledgement

### Completion Criteria

- Mobile backtest run does not require scrolling through hundreds of rows before
  reaching later result sections.
- No clipped table columns without a visible horizontal-scroll affordance.
- Action buttons and stat cards do not overflow at 390px width.
- Disclaimer remains visible/available but is not repeatedly obstructive.
- Monthly returns, annual returns, trades, and full stats each use a mobile-safe
  table/card/expand pattern.
- Repeat visit after acknowledgement is tested or manually verified.
- Mobile screenshots demonstrate that the results workspace structure, not a
  separate mobile-only redesign, solves the dense-output problem.

## Workstream 8: Testing and Verification

### Backend Tests

- `uv run pytest tests/unit/test_web_backend_routers.py -q`
- `uv run pytest tests/unit/test_backtest_runner_e2e.py -q`
- Add focused unit tests for drawdown helper and metric consistency.
- Keep `tests/integration/test_testfolio_backtest_parity.py` opt-in and low
  volume.

### Frontend Tests

- `cd web/frontend && corepack pnpm typecheck`
- Extend `web/frontend/tests/e2e/app-smoke.spec.ts`:
  - metric consistency after run
  - result tabs navigation
  - preset browser selection
  - multi-portfolio comparison happy path
  - stale-result indicator
  - mobile result navigation
- Continue using mocked API responses for CI-oriented browser coverage.

### Manual Browser Pass

Use the in-app browser or Playwright screenshots to inspect:

- desktop 1440x1000
- laptop 1280x800
- mobile 390x844
- dark mode
- light mode if still supported
- no-result empty state
- loading state
- success state
- stale state
- error state

### External Parity

Run sparingly:

```bash
ENV=development DYNACONF_ENV=development FINBOT_RUN_TESTFOLIO_PARITY=1 \
  uv run pytest tests/integration/test_testfolio_backtest_parity.py \
  -o addopts="" -m "slow and external" --capture=no -v
```

For fuller local comparison:

```bash
ENV=development DYNACONF_ENV=development FINBOT_RUN_TESTFOLIO_PARITY=1 \
  FINBOT_TESTFOLIO_CASE_LIMIT=2 FINBOT_TESTFOLIO_REQUEST_DELAY_SECONDS=2 \
  uv run pytest tests/integration/test_testfolio_backtest_parity.py \
  -o addopts="" -m "slow and external" --capture=no -v
```

### Completion Criteria

- Backend test commands listed above pass or any failure is documented as
  unrelated with evidence.
- Frontend typecheck passes.
- Mocked Playwright backtesting workflows cover success, stale state, preset
  selection, multi-portfolio comparison, and mobile navigation.
- Manual screenshots are captured for desktop, laptop, and mobile success
  states, plus at least one loading/error or mocked-error state.
- External parity tests remain opt-in and are not added to default CI.

## Milestones

### M1: Trust Fix

- [x] Max drawdown consistency fixed.
- [x] Backend and frontend tests protect the fix.
- [x] Representative value-path test and mocked browser workflow show consistent metric handling.

### M2: Results Workspace

- [x] Existing result sections are reorganized into navigable tabs/sections.
- [x] Summary header and stale-state behavior are shipped.
- [x] No current result data is lost.

### M3: Better Portfolio Builder

- [x] Preset browser and improved allocation editor shipped.
- [x] Current one-run flow remains simple.
- [x] Invalid allocations are clearly blocked and explained.

### M4: Multi-Portfolio Comparison

- [x] Two or more portfolios can be run and compared in one workflow.
- [x] Comparison charts/tables and per-portfolio drilldown are available.

### M5: Sharing and Chart Controls

- [x] Shareable configuration links shipped.
- [x] Per-chart controls/downloads shipped for core charts.
- [x] Export menu covers run, value history, returns, trades, and comparison data.

### M6: Mobile Polish and Closeout

- [x] Dense tables are mobile-usable.
- [x] Result navigation works on mobile.
- [x] Disclaimer no longer blocks repeat use after acknowledgement.
- [x] Roadmap docs updated with validation evidence.

## Implementation Closeout: 2026-04-24

Completed the autonomous implementation pass across P12.1-P12.5:

- Canonical max drawdown now comes from the portfolio value path, matching the drawdown chart.
- Backtesting results are grouped behind a sticky summary and tabs for Overview, Compare, Audit, Cashflows, Diagnostics, and Returns.
- Portfolio construction now includes searchable presets, assumption labels, saved local portfolios, and a comparison queue capped at five portfolios.
- Multi-portfolio comparison runs through the existing single-run API and renders normalized comparison charts plus exportable metrics.
- Share links serialize the current run configuration into the URL.
- Core charts support log scale, series visibility, PNG download, and cleaner date ticks.
- Dense tables now render as compact mobile cards and use row limits with explicit show-all controls.

Verification review follow-up on 2026-04-24 found and corrected several gaps:

- Multi-portfolio comparison now renders even when the user has not run a single baseline backtest first.
- Comparison output now includes a combined drawdown chart in addition to the normalized equity curve and metrics table.
- Preset coverage now includes Risk Parity Starter and Equal Weight portfolios.
- Saved and comparison portfolios preserve portfolio-level rebalance interval settings.
- Share links restore visible portfolio configuration more reliably, and stale-result detection no longer falsely marks unchanged cashflow runs as stale.
- Browser coverage now exercises preset load/edit/run, stale-state display, share-link round-trip, and mixed-success comparison results.

Second verification review on 2026-04-24 found and corrected one additional
state-isolation issue:

- Running a portfolio comparison after a successful single backtest no longer mutates the single-run summary/run request context.
- Browser coverage now includes this regression path.

Validation recorded in this pass:

- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH ./node_modules/.bin/tsc --noEmit`
- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH NEXT_TELEMETRY_DISABLED=1 NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api ./node_modules/.bin/next build`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_backtest_runner_e2e.py::TestComputeStats -q -s`
- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api ./node_modules/.bin/playwright test tests/e2e/app-smoke.spec.ts -g "backtesting workflows"`
- Desktop and mobile screenshots were captured during closeout and removed
  during the maintenance cleanup pass; the durable validation record is the
  command list above.

Additional verification from the follow-up review:

- `/home/jer/.local/bin/uv run pytest tests/unit/test_backtest_runner_e2e.py -o addopts="" -q -s`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_web_backend_routers.py -o addopts="" -q -s`
- `/home/jer/.local/bin/uv run ruff check finbot/services/backtesting/compute_stats.py tests/unit/test_backtest_runner_e2e.py`
- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH ./node_modules/.bin/playwright test tests/e2e/app-smoke.spec.ts`
- `git diff --check`
- Desktop result, desktop comparison, and mobile result screenshots were
  captured during review and removed during the maintenance cleanup pass.

Second-review validation:

- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH ./node_modules/.bin/tsc --noEmit`
- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH NEXT_TELEMETRY_DISABLED=1 NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api ./node_modules/.bin/next build`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_backtest_runner_e2e.py::TestComputeStats -q -s`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_backtest_runner_e2e.py -o addopts="" -q -s`
- `/home/jer/.local/bin/uv run pytest tests/unit/test_web_backend_routers.py -o addopts="" -q -s`
- `PATH=/home/jer/.local/node-v20.19.0-linux-x64/bin:$PATH NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api ./node_modules/.bin/playwright test tests/e2e/app-smoke.spec.ts` (27 passed)
- `git diff --check`
- Desktop comparison-after-single and mobile returns-table screenshots were
  captured during second review and removed during the maintenance cleanup pass.

Explicit deferral:

- Rebalance bands remain deferred because the current backtesting request/strategy contract does not expose a banded rebalance policy.
- Broad component extraction from `web/frontend/src/app/backtesting/page.tsx` remains a maintainability follow-up. The P12 product behavior is implemented and covered, but the page should still be split into local backtesting components before the next large feature tranche.

## Rollout Strategy

- Keep each milestone mergeable independently.
- Prefer feature-compatible schema additions over breaking API changes.
- Keep old single-run request shape working while adding multi-portfolio
  orchestration.
- Avoid external API calls in default CI.
- Archive this plan into `docs/planning/archive/` when P12 closes, with a short
  completion note and validation list.

## Risks and Mitigations

- **Metric drift:** Centralize metric helpers and test representative paths.
- **Page complexity:** Extract components before adding multi-portfolio state.
- **Mobile overload:** Design mobile result views as first-class sections, not
  shrunken desktop tables.
- **Backend runtime cost:** Start multi-portfolio with a low portfolio cap and
  frontend orchestration; add batch endpoint only when needed.
- **Preset data ambiguity:** Mark simulated/unavailable ticker assumptions and
  avoid silently substituting assets.
- **Share-link size:** Use compressed config payloads only if simple query params
  become too large.

## Definition of Done

- P12.1-P12.5 roadmap checklists are complete or explicitly deferred with
  rationale.
- Backtesting page supports trusted metrics, tabbed results, richer portfolio
  construction, multi-portfolio comparison, share/reuse flows, chart controls,
  and mobile-dense output handling.
- Typecheck, focused backend tests, mocked browser tests, and manual browser
  screenshots are recorded in the closeout note.
- User-facing docs or README surfaces describe the new workflow where relevant.
