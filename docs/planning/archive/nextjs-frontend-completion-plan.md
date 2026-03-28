# Finbot Frontend Redesign Plan

## Context

The Streamlit dashboard (`finbot/dashboard/`) has 12 pages but is constrained by Streamlit's limited styling and interactivity. A modern Next.js frontend already exists at `web/frontend/` (~85% complete) with a professional tech stack: Next.js 16, React 19, Tailwind CSS v4, shadcn/ui, Recharts, Lightweight Charts, Framer Motion, and Zustand. However, it's missing 4 critical utility files (`src/lib/`), 4 pages (risk analytics, portfolio analytics, realtime quotes, factor analytics), corresponding backend API endpoints, and visual polish.

**Competitors**: Portfolio Visualizer is feature-rich but looks dated (Bootstrap-era). Testfolio is modern but feature-light. Our goal is to combine depth of features with a premium, dark-mode-first visual design that clearly surpasses both.

**Approach**: Complete the Next.js frontend rather than redesign Streamlit. The existing component library, design tokens, and page patterns are solid — we need to fill gaps and polish.

---

## Phase 1: Foundation — Missing Utility Files

These 4 files are imported by every existing page/component but don't exist yet.

### 1.1 `web/frontend/src/lib/utils.ts`
- Export `cn()` using `clsx` + `tailwind-merge` (both already in package.json)

### 1.2 `web/frontend/src/lib/api.ts`
- Export `apiGet<T>(url, timeout?)` and `apiPost<T>(url, body, timeout?)`
- Base URL from `NEXT_PUBLIC_API_URL` env var, default `http://localhost:8000`
- Native `fetch` with AbortController timeout (120s default)
- Parse FastAPI error `detail` field into thrown Error messages

### 1.3 `web/frontend/src/lib/format.ts`
- `formatPercent(value)` — `null` -> "N/A", else `(v*100).toFixed(2)%`
- `formatNumber(value, decimals?)` — `Intl.NumberFormat` with fixed decimals
- `formatCurrency(value)` — USD, 0 decimals
- `formatCurrencyPrecise(value)` — USD, 2 decimals
- `formatBytes(bytes)` — human-readable KB/MB/GB

### 1.4 `web/frontend/src/lib/constants.ts`
- `NavItem` interface (`label, href, icon: LucideIcon, group`)
- `NAV_GROUPS` — `["Analysis", "Risk & Portfolio", "Data & Monitoring"]`
- `NAV_ITEMS` — all 13 pages with Lucide icons, grouped:
  - Analysis: Simulations, Backtesting, Optimizer, Monte Carlo, Walk-Forward, Experiments
  - Risk & Portfolio: Risk Analytics, Portfolio Analytics, Factor Analytics, Real-Time Quotes
  - Data & Monitoring: Data Status, Health Economics
- `CHART_COLORS` — series colors matching CSS vars (`--chart-blue`, etc.)
- `DISCLAIMER_TEXT` — legal disclaimer string

---

## Phase 2: Backend API Endpoints

4 new routers + schemas following the existing pattern in `web/backend/routers/` and `web/backend/schemas/`. Each router imports from the corresponding `finbot/services/` module. Register all 4 in `web/backend/main.py`.

### 2.1 Risk Analytics (`/api/risk-analytics`)

**Files**: `web/backend/routers/risk_analytics.py`, `web/backend/schemas/risk_analytics.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/var` | POST | VaR/CVaR (historical, parametric, Monte Carlo) |
| `/stress` | POST | Stress test with built-in crisis scenarios |
| `/kelly` | POST | Single-asset Kelly criterion |
| `/kelly-multi` | POST | Multi-asset matrix Kelly |
| `/var-backtest` | POST | VaR model calibration backtest |

- Shared helper: `_load_returns(ticker, start, end)` using `get_history()` + `pct_change().dropna()`
- Imports: `finbot.services.risk_analytics.var`, `.stress`, `.kelly`

### 2.2 Portfolio Analytics (`/api/portfolio-analytics`)

**Files**: `web/backend/routers/portfolio_analytics.py`, `web/backend/schemas/portfolio_analytics.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rolling` | POST | Rolling Sharpe, vol, beta |
| `/benchmark` | POST | Alpha, beta, R-squared, tracking error, IR, capture ratios |
| `/drawdown` | POST | Drawdown period detection + underwater curve |
| `/correlation` | POST | HHI, effective N, diversification ratio, correlation matrix |

- Imports: `finbot.services.portfolio_analytics.rolling`, `.benchmark`, `.drawdown`, `.correlation`

### 2.3 Real-Time Quotes (`/api/realtime-quotes`)

**Files**: `web/backend/routers/realtime_quotes.py`, `web/backend/schemas/realtime_quotes.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/quotes` | POST | Fetch live quotes for symbols |
| `/provider-status` | GET | Provider health check |

- Module-level `CompositeQuoteProvider` singleton for accumulated stats
- Imports: `finbot.services.realtime_data.composite_provider`

### 2.4 Factor Analytics (`/api/factor-analytics`)

**Files**: `web/backend/routers/factor_analytics.py`, `web/backend/schemas/factor_analytics.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/regression` | POST | OLS factor regression (auto-detect CAPM/FF3/FF5) |
| `/attribution` | POST | Per-factor return contribution decomposition |
| `/risk-decomposition` | POST | Systematic/idiosyncratic variance split |
| `/rolling-r-squared` | POST | Rolling R-squared time series |

- Imports: `finbot.services.factor_analytics.factor_regression`, `.factor_attribution`, `.factor_risk`

### 2.5 Router Registration

**Modify**: `web/backend/main.py` — add 4 imports and 4 `app.include_router(...)` calls.

---

## Phase 3: New Frontend Pages

All 4 pages follow the established pattern: `"use client"`, `ToolLayout` + `ConfigPanel` for config-driven tools, `StatCard` grids, `ChartCard` wrappers, `DataTable`, `EmptyState`, `InlineError`, `useMutation`, `toast`.

### 3.1 Risk Analytics Page (`src/app/risk-analytics/page.tsx`)

**3 tabs using `Tabs` component:**

**Tab 1 — VaR/CVaR**:
- Config: ticker, confidence slider (0.90–0.99), horizon select (1/5/10/21 days), optional portfolio value, date range
- Results: 4 StatCards (Historical VaR, Parametric VaR, MC VaR, CVaR)
- Charts: Returns histogram with VaR lines (BarChartWrapper), method comparison bar chart
- Expandable VaR backtest section

**Tab 2 — Stress Testing**:
- Config: ticker, scenario checkboxes (4 built-in), portfolio value, date range
- Results: Scenario summary DataTable, worst-scenario StatCards
- Charts: Comparison bar chart, expandable per-scenario price paths

**Tab 3 — Kelly Criterion**:
- Toggle: Single-asset / Multi-asset mode
- Single: ticker, date range -> Kelly fraction StatCards + bar chart
- Multi: comma-separated tickers -> weights DataTable, correlation table, per-asset bar chart

### 3.2 Portfolio Analytics Page (`src/app/portfolio-analytics/page.tsx`)

**4 tabs:**

**Tab 1 — Rolling Metrics**: Config (ticker, benchmark, window, rfr, dates) -> line chart of rolling Sharpe/vol/beta, mean StatCards

**Tab 2 — Benchmark Analysis**: Config (portfolio, benchmark, rfr, dates) -> 6 StatCards (alpha, beta, R2, TE, IR, capture), scatter chart

**Tab 3 — Drawdown Analysis**: Config (ticker, top-N, dates) -> underwater curve area chart, drawdown periods bar chart, periods DataTable

**Tab 4 — Correlation**: Config (comma-separated tickers, optional weights, dates) -> 4 StatCards (HHI, effective N, div ratio, avg corr), correlation heatmap, per-asset vol DataTable

### 3.3 Real-Time Quotes Page (`src/app/realtime-quotes/page.tsx`)

**3 tabs:**

**Tab 1 — Live Quotes**: Symbol input, Fetch button -> quote cards grid with gain/loss coloring, full DataTable

**Tab 2 — Watchlist**: Persistent watchlist (new zustand store `src/stores/watchlist-store.ts` with localStorage persist), add/remove symbols, Refresh All

**Tab 3 — Provider Status**: Status check button -> 3 provider cards (Alpaca, Twelve Data, yfinance) with availability badge, request counts, error info

### 3.4 Factor Analytics Page (`src/app/factor-analytics/page.tsx`)

**3 tabs** (Tab 2 and 3 depend on Tab 1 results — shared state in parent):

**Tab 1 — Factor Regression**: Config (ticker, model type select, factor data JSON input, dates) -> loadings DataTable + bar chart, 4 StatCards (alpha, R2, adj-R2, model type)

**Tab 2 — Return Attribution**: Reuses regression data -> stacked contribution bar chart, 3 StatCards (total/explained/residual return), breakdown DataTable

**Tab 3 — Risk Decomposition**: Reuses regression data -> systematic vs idiosyncratic bar chart, 3 StatCards, marginal contributions DataTable

### New Supporting Files

| File | Purpose |
|------|---------|
| `src/components/common/heatmap.tsx` | Correlation heatmap (CSS grid + gradient coloring) |
| `src/components/common/metric-badge.tsx` | Inline gain/loss colored badge |
| `src/components/charts/line-chart-wrapper.tsx` | Recharts LineChart wrapper (matching existing Bar/Area/Scatter wrappers) |
| `src/stores/watchlist-store.ts` | Zustand persistent watchlist for realtime quotes |

### Type Additions

**Modify**: `src/types/api.ts` — add ~40 new interfaces for all 4 API domains (VaR, stress, Kelly, rolling, benchmark, drawdown, correlation, quotes, provider status, factor regression/attribution/risk).

---

## Phase 4: Health Economics Page Polish

**Modify**: `web/frontend/src/app/health-economics/page.tsx`

- Wrap tab content in `ToolLayout` + `ConfigPanel` (currently uses manual grid)
- Replace plain empty divs with `EmptyState` component + preset buttons
- Add `InlineError` for API failures (currently toast-only)
- Standardize spacing to `space-y-8`

---

## Phase 5: Visual Polish & UX Enhancements

### 5.1 Dashboard Home (`src/app/page.tsx`)
- Add 4 new tool links for the new pages (risk analytics, portfolio analytics, realtime quotes, factor analytics)
- Add animated counters on stat cards using Framer Motion `animate`
- Add "Quick Actions" row with preset buttons ("Backtest SPY", "Monte Carlo QQQ", etc.)

### 5.2 Chart Styling
- Consistent glass-morphism tooltips across all Recharts wrappers
- Animated chart entry using Recharts `animationDuration`/`animationEasing`
- Reference lines for key thresholds (zero line on drawdown, confidence on VaR)

### 5.3 Loading & Transitions
- Framer Motion `AnimatePresence` for tab transitions
- Staggered fade-in for StatCard grids
- Skeleton-to-content transition animations

### 5.4 Micro-interactions
- Enhanced hover glow on StatCards
- Subtle scale animation on Run buttons
- Count-up number animation when stat values change

### 5.5 CSS Additions (`globals.css`)
- `.glass-card-hover` variant with stronger backdrop blur
- Gradient animation for loading states
- Enhanced focus-visible ring styles

---

## Phase 6: Verification

1. **TypeScript**: `npx tsc --noEmit` — no type errors
2. **Build**: `npm run build` — successful production build
3. **Backend smoke**: `curl` each new endpoint with sample payloads
4. **Page navigation**: Visit all 13 pages, verify rendering + empty states
5. **Command palette**: Cmd+K search finds all 13 pages
6. **Responsive**: Test sidebar collapse, mobile menu, grid breakpoints
7. **Dark/light mode**: All new components respect theme tokens
8. **Error states**: Test with backend down, invalid inputs, empty results

---

## File Summary

### New Files (24)

| File | Phase |
|------|-------|
| `web/frontend/src/lib/utils.ts` | 1 |
| `web/frontend/src/lib/api.ts` | 1 |
| `web/frontend/src/lib/format.ts` | 1 |
| `web/frontend/src/lib/constants.ts` | 1 |
| `web/backend/schemas/risk_analytics.py` | 2 |
| `web/backend/schemas/portfolio_analytics.py` | 2 |
| `web/backend/schemas/realtime_quotes.py` | 2 |
| `web/backend/schemas/factor_analytics.py` | 2 |
| `web/backend/routers/risk_analytics.py` | 2 |
| `web/backend/routers/portfolio_analytics.py` | 2 |
| `web/backend/routers/realtime_quotes.py` | 2 |
| `web/backend/routers/factor_analytics.py` | 2 |
| `web/frontend/src/app/risk-analytics/page.tsx` | 3 |
| `web/frontend/src/app/portfolio-analytics/page.tsx` | 3 |
| `web/frontend/src/app/realtime-quotes/page.tsx` | 3 |
| `web/frontend/src/app/factor-analytics/page.tsx` | 3 |
| `web/frontend/src/components/common/heatmap.tsx` | 3 |
| `web/frontend/src/components/common/metric-badge.tsx` | 3 |
| `web/frontend/src/components/charts/line-chart-wrapper.tsx` | 3 |
| `web/frontend/src/stores/watchlist-store.ts` | 3 |

### Modified Files (5)

| File | Phase | Changes |
|------|-------|---------|
| `web/backend/main.py` | 2 | Add 4 router imports + registrations |
| `web/frontend/src/types/api.ts` | 3 | Add ~40 type interfaces for 4 new domains |
| `web/frontend/src/app/page.tsx` | 5 | Add 4 new tool links, quick actions, animated counters |
| `web/frontend/src/app/health-economics/page.tsx` | 4 | ToolLayout refactor, EmptyState, InlineError |
| `web/frontend/src/app/globals.css` | 5 | Glass-card-hover, gradient animation, focus rings |

---

## Execution Order

```
Phase 1 (Foundation)     ← must complete first; all code imports from lib/
    ↓
Phase 2 (Backend) + Phase 4 (Health Econ polish)    ← parallel
    ↓
Phase 3 (New Pages)      ← needs backend endpoints from Phase 2
    ↓
Phase 5 (Visual Polish)  ← final layer
    ↓
Phase 6 (Verification)   ← end-to-end testing
```
