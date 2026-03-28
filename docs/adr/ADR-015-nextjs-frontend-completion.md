# ADR-015: Complete Next.js Frontend and Add Missing Pages

**Status:** Accepted
**Date:** 2026-03-27

## Context

The Streamlit dashboard (`finbot/dashboard/`) provides 12 pages of interactive analysis but is constrained by Streamlit's limited styling, interactivity, and component model. A modern Next.js frontend was ~85% complete at `web/frontend/` with a professional stack (Next.js 16, React 19, Tailwind CSS v4, shadcn/ui, Recharts, Framer Motion, Zustand) but was missing 4 utility files (`src/lib/`), 4 pages (risk analytics, portfolio analytics, realtime quotes, factor analytics), corresponding backend API endpoints, and visual polish.

Competitors (Portfolio Visualizer, Testfolio) either have dated UIs or limited feature sets. The goal was to deliver a premium, dark-mode-first design with full analytical depth.

## Decision

Complete the existing Next.js frontend rather than redesign from scratch:

1. **Foundation** — Create 4 missing `src/lib/` utility files (utils, api, format, constants) imported by every existing component.

2. **Backend API** — Add 4 new FastAPI routers with 15 endpoints for risk analytics (VaR/CVaR, stress, Kelly), portfolio analytics (rolling, benchmark, drawdown, correlation), real-time quotes, and factor analytics (regression, attribution, risk decomposition). All routers delegate to existing `finbot/services/` modules.

3. **Frontend Pages** — Build 4 new multi-tab pages following the established pattern (ToolLayout, ConfigPanel, StatCards, ChartCards, DataTable, mutations with toast). Also add 4 supporting components (heatmap, metric-badge, line-chart-wrapper, watchlist-store).

4. **Polish** — Enhance Health Economics page with proper EmptyState/InlineError components, add new page links to the dashboard home, and add CSS enhancements (glass-card-hover, gradient-loading, staggered animations, enhanced focus rings).

## Consequences

**Positive:**
- All 12 analytical capabilities now accessible through a modern, responsive UI
- Consistent component patterns across all pages reduce maintenance burden
- Premium dark-mode-first design with glass-morphism and gradient effects
- Backend API layer provides clean separation for future mobile/API consumers
- Zustand persistent watchlist enables user workflow continuity

**Negative:**
- Two frontends (Streamlit + Next.js) coexist — Streamlit dashboard remains for backward compatibility
- Frontend requires `npm install` and Node.js in addition to Python
- Real-time quotes page depends on external API keys (Alpaca, Twelve Data) for full functionality
