# testfolio (testfol.io), Portfolio Visualizer, and Finbot — Updated Competitive Analysis

**Original note:** 2026-02-18
**Updated:** 2026-04-17
**Focus:** Re-evaluate the February analysis and refresh the competitor picture with particular attention to backtesting.

---

## 1. Executive Summary

- The February thesis was directionally correct: Finbot's biggest competitive gap was not raw quantitative capability, but productizing that capability into a strong portfolio research workflow.
- Since then, Finbot has made real progress on adjacent research breadth. Portfolio analytics, factor analytics, risk analytics, walk-forward analysis, experiments, and frontend hardening are materially better than they were in February.
- The biggest remaining gap is still the core backtesting experience. Finbot is strong as a strategy research platform, but it is still weak as a portfolio construction and retirement backtesting product.
- testfolio is now the clearest direct benchmark for where Finbot should aim on allocation backtesting UX. It has turned one core backtester into a broader research hub.
- Portfolio Visualizer remains the broader suite benchmark. It still leads on workflow maturity around portfolio construction, optimization, export, saved models, and planning.
- Finbot's moat is still real: walk-forward analysis, regime-aware evaluation, experiment tracking, data snapshots, execution realism, typed contracts, and open service-layer extensibility. The problem is that too little of that moat is surfaced in the main user-facing backtesting flow.

---

## 2. Re-Evaluation of the 2026-02-18 Recommendations

The original recommendation list mostly remains valid. What changed is that Finbot closed several adjacent analytics gaps, while the primary portfolio backtesting workflow still lags both competitors.

### Status Snapshot

| Recommendation from 2026-02-18                        | Status on 2026-04-17 | Re-evaluation                                                                                                                                                                                                                                                          |
| ----------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Multi-asset portfolio builder                         | **Partial**          | Finbot's current web backtester still behaves like a strategy runner, not a general portfolio builder. The Next.js surface supports one asset plus an optional second asset for some strategies, with weights auto-filled rather than explicitly designed by the user. |
| Preset portfolio library                              | **Partial**          | A few starter presets exist in empty states, but there is no reusable library of canonical portfolios such as 60/40, Golden Butterfly, All Weather, or custom saved model portfolios.                                                                                  |
| SWR/PWR withdrawal analysis                           | **Open**             | Still absent as a product feature. There is no dedicated withdrawal engine, retirement durability workflow, or rolling survival analysis surface.                                                                                                                      |
| Bond ladder simulator page                            | **Open**             | The service exists in the repo, but it is still not surfaced as a dedicated Next.js page or backend route.                                                                                                                                                             |
| Pareto optimizer page                                 | **Open**             | The service exists in the repo, but it is still not surfaced in the current web product.                                                                                                                                                                               |
| Multi-asset Monte Carlo page                          | **Open**             | The current Monte Carlo web route is still single-asset only.                                                                                                                                                                                                          |
| Efficient frontier                                    | **Open**             | Still a competitive gap versus both testfolio and Portfolio Visualizer.                                                                                                                                                                                                |
| Asset correlation matrix                              | **Shipped**          | This gap is substantially closed by the portfolio analytics correlation and diversification page.                                                                                                                                                                      |
| Factor regression                                     | **Shipped**          | This gap is substantially closed by the factor analytics page, which now includes regression, attribution, and factor risk decomposition.                                                                                                                              |
| Rolling returns and rolling statistics charts         | **Partial**          | Rolling metrics now exist as a standalone analytics surface, but not as an integrated part of a backtest result workflow.                                                                                                                                              |
| Periodic contributions and withdrawals in backtesting | **Open**             | Still missing in the main backtesting flow.                                                                                                                                                                                                                            |
| Calendar-year returns table                           | **Open**             | Not exposed in the current Next.js or Streamlit backtesting surfaces.                                                                                                                                                                                                  |
| CSV or JSON export                                    | **Open**             | Export is still not part of the main Next.js backtesting workflow.                                                                                                                                                                                                     |
| Benchmark overlay on equity curves                    | **Partial**          | Finbot now has standalone benchmark analytics, but the backtest result itself still lacks benchmark-relative series and overlay charts.                                                                                                                                |

### What This Means

- Finbot closed more of the "research breadth" gaps than the "portfolio backtesting UX" gaps.
- Delivery skewed toward analytics, robustness, testing, and platform hardening rather than toward the flagship allocation backtester experience.
- That was not wasted work. It improved the technical foundation and gave Finbot deeper differentiators.
- But the next competitive step still has to be a stronger portfolio backtesting product surface, not another adjacent analytics module.

### Lower-Priority February Items

Most lower-priority items remain open: Black-Litterman, fund screening, autocorrelation, cointegration, PCA, and dynamic glidepath allocation. Tactical capability improved somewhat at the strategy level, but Finbot still does not have a dedicated tactical allocation workbench comparable to either competitor.

---

## 3. Competitor Refresh: testfolio (testfol.io)

### Positioning

testfolio now looks like the most direct benchmark for Finbot's future portfolio backtesting product. It is not trying to be a giant general-purpose analytics catalog first. It is trying to make portfolio research fast, repeatable, and easy to inspect from one central backtester.

### Backtesting Workflow Strengths

- The portfolio backtester is the center of the product, not just one tool among many.
- The run model is broad: start and end dates, starting value, inflation adjustment, rolling window choice, benchmark selection, recurring cashflow legs, one-time cashflows, drag, dividend settings, glidepaths, and multiple portfolio cards.
- Portfolio construction is flexible. Users can define multiple portfolios in one run, assign weights directly, use negative weights, choose rebalance frequency, add rebalance offsets, and use rebalance bands.
- Data flexibility is unusually strong. testfolio supports ordinary tickers, simulated extended-history tickers, custom leveraged expressions, custom bond ticker syntax, uploaded series, and backfilled series.
- The platform treats a backtest as one run with many views rather than many separate tools. A single run can be inspected through summary metrics, withdrawals, rolling metrics, returns tables, correlations, regression, allocation views, rebalancing logs, and cashflow logs.

### Backtesting Output Depth

The current testfolio backtester is best understood as a research workspace rather than a chart and a stat table.

- Summary and statistics tabs provide headline comparison across portfolios.
- Withdrawal views cover retirement-style durability, SWR, PWR, survival, preservation, and curve views across multiple horizons.
- Rolling metrics show stability rather than just point-in-time outcomes.
- Returns views include daily, monthly, and annual behavior.
- Correlation and beta views make benchmark-relative diagnostics a first-class part of the workflow.
- Rebalancing and cashflow tabs expose operational details rather than treating them as hidden assumptions.
- Allocation and portfolio pie views make weight drift and glidepath behavior inspectable over time.

### Adjacent Tools

testfolio has continued building a cohesive ecosystem around the backtester:

- Asset Analyzer
- Portfolio Optimizer
- Backtest Optimizer
- Efficient Frontier
- Tactical Allocation
- Tactical Grid Search
- Rebalancing Sensitivity Analysis
- Factor Regression
- Principal Component Analysis
- Signal analyzers
- LETF analysis
- Calculator suite

### Pricing and Workflow Maturity

testfolio's pricing page is informative because it shows how productized the workflow already is.

- Public access already includes the core backtester, asset analyzer, and calculator suite.
- Higher tiers increase portfolio counts, ticker counts, cashflow limits, Monte Carlo limits, factor coverage, uploads, saved runs, and optimization access.
- Public and free tiers are constrained by explicit workflow limits, not by a lack of product definition.
- Save, local persistence, cloud persistence, and repeated workflow support are built into the product model.

### Why testfolio Matters

testfolio is the strongest direct comparator for Finbot's backtesting future because it has solved the exact product problem Finbot still has: how to turn quantitative logic into a portfolio research workflow that is wide, inspectable, and repeatable.

---

## 4. Competitor Refresh: Portfolio Visualizer

### Portfolio Visualizer Positioning

Portfolio Visualizer remains the broader benchmark. It is still less of a single-workflow allocation lab than testfolio, but it remains ahead of Finbot in the depth of portfolio construction, saved models, imports, exports, and surrounding planning or institutional-style tooling.

### Current Backtesting and Portfolio Research Surface

Portfolio Visualizer still exposes multiple distinct backtesting modes:

- Backtest Portfolio
- Backtest Asset Class Allocation
- Backtest Dynamic Allocation
- Tactical Asset Allocation Models
- Manager Performance Analysis

That split matters. Portfolio Visualizer treats portfolio research as a family of related problems: static allocations, asset-class models, time-varying allocations, tactical rules, and manager evaluation.

### Documentation and Workflow Depth

Its documentation still signals mature workflow coverage around portfolio research:

- Saving portfolio and simulation models
- Importing portfolios
- Importing cashflows
- Importing correlations
- Custom data series and benchmarks
- Backfilling asset returns
- Modeling advisor fees
- Expense ratios, dividends, and short positions
- Customizing reports

This is not just feature-list depth. It is workflow depth. Portfolio Visualizer assumes users need to save, import, compare, and report on work, not only run a calculation.

### Adjacent Tooling

Portfolio Visualizer still leads on surrounding breadth:

- Portfolio optimization
- Efficient frontier
- Black-Litterman
- Rolling optimization
- Monte Carlo simulation
- Financial goals
- Asset liability modeling
- Factor regression and factor attribution tools
- Risk factor allocation and factor matching
- Fund screener, rankings, and fund performance analysis
- Asset correlations, autocorrelation, and cointegration
- Live market and macro dashboards

### Pricing and Product Maturity

The pricing model reinforces the same point.

- Free users get core analysis tools, but not save and import workflows, export, configurable backfills, management fees, or custom data series.
- Paid plans unlock save and import, Excel or CSV or PDF export, backfills, management fees, custom data series, capital market assumptions, and team synchronization.
- The free tier is limited, but the product itself is fully articulated.

### Why Portfolio Visualizer Matters

Portfolio Visualizer is still the broader suite benchmark, especially for users who think in terms of portfolio design, advisory workflows, import and export maturity, and optimization or planning coverage. It is less focused than testfolio around a single backtesting hub, but much farther along than Finbot in portfolio workflow completeness.

---

## 5. Backtesting-Focused Comparison Matrix

| Dimension                            | testfolio                                                                                                                       | Portfolio Visualizer                                                                      | Finbot today                                                                                                                                         |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Primary product shape                | One central portfolio backtester with many adjacent diagnostics                                                                 | Broad modular portfolio-analysis suite                                                    | Strategy backtester plus strong adjacent analytics pages                                                                                             |
| Portfolio construction               | Multiple portfolios, many tickers, direct weights, negative weights, glidepaths                                                 | Multiple backtest modes, imported portfolios, asset-class and dynamic allocation variants | Current product surfaces behave more like strategy runners than portfolio builders                                                                   |
| Cashflows and retirement modeling    | Recurring and one-time cashflows, inflation adjustment, withdrawal analysis, SWR and PWR                                        | Contributions and withdrawals, Monte Carlo planning, goals and liability modeling         | No backtesting cashflow or retirement workflow in the main product                                                                                   |
| Rebalancing controls                 | Frequency, offset, bands, drift inspection, event logs                                                                          | Frequency, multiple backtest modes, tactical variants                                     | Limited to strategy parameters such as rebalance interval for selected strategies                                                                    |
| Benchmarking                         | Explicit benchmark in the run plus correlation and beta diagnostics                                                             | Benchmark comparisons, custom benchmarks, imported and custom data series                 | Separate benchmark analytics page exists, but backtests do not currently behave as benchmark-relative workflows                                      |
| Output depth from one run            | Summary, metrics, withdrawals, rolling metrics, returns tables, correlation, regression, rebalancing, allocation, cashflow logs | Broad reports across backtesting, optimization, factor, and planning tools                | Stats, value chart, drawdown, trades; deeper analysis is split into separate pages                                                                   |
| Save, share, export                  | Local and cloud save workflows, saved runs, saved portfolios as tickers, shareable workflows                                    | Saved models, import and export, report customization, team sync on higher tiers          | Experiment comparison exists, but current backtest pages are not save-first or export-first workflows                                                |
| Data modeling flexibility            | Simulated tickers, custom leverage, custom bonds, uploads, backfills                                                            | Backfills, custom data series, custom benchmarks, fee and expense modeling                | Good internal data pipeline, but thin user-facing modeling options in the backtest UI                                                                |
| Realism and research differentiation | Strong allocation research ergonomics                                                                                           | Strong workflow maturity and tool breadth                                                 | Strongest technical moat: walk-forward, regime analysis, experiment tracking, snapshots, execution realism, cost and corporate-action infrastructure |

### Core Interpretation

- testfolio wins the most important direct comparison: portfolio backtesting as a coherent, inspectable research workflow.
- Portfolio Visualizer wins the broadest comparison: portfolio research as a mature tool platform with imports, exports, saved workflows, and planning modules.
- Finbot wins the technical depth comparison in several areas that matter to serious research, but those wins are mostly below the product surface.

---

## 6. Finbot's Position Today

### Where Finbot Is Strong

- Backtesting architecture is substantially more interesting than the current UI suggests.
- Walk-forward analysis is a real differentiator and is already exposed.
- Regime-aware evaluation exists in the service layer and in the broader product story.
- Experiment tracking and snapshot-oriented reproducibility are stronger than what either competitor visibly emphasizes.
- Cost-model, corporate-action, missing-data, and execution-simulation infrastructure create a more realistic foundation than a simple allocation calculator.
- Finbot now has serious adjacent analytics breadth: risk, portfolio, factor, real-time data, and health economics.

### Where Finbot Is Still Behind

- The main backtesting surfaces are still too narrow. They are optimized for "run this strategy" rather than "design and study this portfolio."
- There is still no true arbitrary portfolio builder with explicit weights and multiple asset rows.
- Cashflows, retirement durability, and withdrawal analysis are still missing from the core backtesting experience.
- Result inspection is still thin compared with either competitor: no annual and monthly return tables, no allocation drift view, no rebalance log, no cashflow log, and no benchmark-relative dashboard from the same run.
- Save, export, and share workflows remain underdeveloped.
- Several strengths are still under-exposed in the main product. Finbot's service layer includes more than the current web and Streamlit backtesting pages allow users to configure or inspect.

### The Important Nuance

Finbot is stronger as a quantitative research platform than as a turnkey portfolio backtesting product. That is an encouraging problem because the core substance exists. But it is also the main reason the competitor gap still feels larger from the outside than it really is under the hood.

---

## 7. Updated Recommendation Priority

The strategic priority has not changed: backtesting needs to become the flagship portfolio research workflow.

### Priority 1: Build a True Allocation Backtester

1. Replace the current one-asset or two-asset backtest form with an arbitrary asset table.
2. Let users set explicit weights, validate totals, and choose benchmarks directly in the run.
3. Add a real preset portfolio library with canonical allocation models and user-saveable presets.
4. Make this the primary workflow, not a side feature attached to strategy selection.

### Priority 2: Add Cashflows and Retirement Modeling

1. Add recurring contributions and withdrawals.
2. Add one-time cashflow events.
3. Add inflation-adjusted viewing.
4. Add withdrawal durability outputs before building more exotic optimizers.

### Priority 3: Turn One Backtest Into a Research Workspace

1. Add rolling metrics from the same run.
2. Add monthly and annual returns tables.
3. Add benchmark-relative metrics and overlay charts.
4. Add allocation drift and rebalance-event inspection.
5. Add export for metrics, trades, and time series.

### Priority 4: Connect Backtesting to Finbot's Existing Moat

1. Make saved backtests first-class experiments.
2. Surface cost assumptions, missing-data policy, and snapshot lineage.
3. Expose regime-aware and walk-forward follow-ups from the same backtest result.
4. Surface more of the service-layer capability that already exists, instead of hiding it behind separate tooling or code-only entry points.

### Priority 5: Surface Existing Services That Reinforce the Story

1. Add bond ladder as a dedicated web surface.
2. Add Pareto optimization as a dedicated web surface.
3. Add multi-asset Monte Carlo rather than keeping Monte Carlo single-asset only.

### What to Defer

Finbot should not prioritize Black-Litterman, fund screening, autocorrelation, cointegration, PCA, or other long-tail institutional-style tools until the core backtesting workflow becomes competitive with testfolio and meaningfully closer to Portfolio Visualizer.

---

## 8. Final Assessment

The February analysis still holds up. Finbot's biggest challenge is not finding more quantitative ideas to build. It is turning its existing technical depth into a coherent portfolio research product.

The most important updated conclusion is this:

- If Finbot wants to compete most directly on backtesting, testfolio is the right product benchmark.
- If Finbot wants to benchmark the outer limit of workflow maturity and research breadth, Portfolio Visualizer is still the better comparison.
- If Finbot wants to win on its own terms, it should combine a modern allocation backtester UX with the realism and reproducibility features that neither competitor currently makes central.

In practical terms, that means the next major move should be an Allocation Backtester 2.0, not another isolated analytics page.
