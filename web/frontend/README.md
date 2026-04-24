# Finbot Frontend

Next.js App Router frontend for Finbot's quantitative research platform.

The frontend exposes 13 routes in total: the dashboard home page plus 12
task-specific pages spanning simulations, backtesting, analytics, and health
economics.

The flagship portfolio-research surfaces are intentionally broader than their
route names suggest: `simulations` includes leveraged-fund and bond-ladder
tabs, `monte-carlo` includes single-asset and correlated multi-asset tabs,
`optimizer` includes DCA, Pareto, and efficient-frontier tabs, and the
backtesting page carries cost, missing-data, experiment-lineage, and
walk-forward handoff follow-through directly in the main workspace.

## Quick Start

```bash
# From the repository root
uv sync --extra web --extra dashboard

# Terminal 1: backend API
DYNACONF_ENV=development uv run --extra web uvicorn web.backend.main:app --reload --port 8000

# Terminal 2: frontend app
cd web/frontend
corepack pnpm install
corepack pnpm dev
```

Open `http://localhost:3000` after both services are running.

## Useful Commands

```bash
cd web/frontend

corepack pnpm dev        # local development server
corepack pnpm typecheck  # TypeScript validation
corepack pnpm build      # production build
corepack pnpm test:e2e   # mocked Chromium Playwright coverage; CI-only unless explicitly needed
```

## Runtime Configuration

- `NEXT_PUBLIC_API_URL` is the browser-facing API base URL.
- The app reads that value from the server-rendered layout at runtime, so a
  deployed container can change the API origin without rebuilding the frontend
  bundle.
- For local Docker with separate published ports, use `http://localhost:8000`.
- For production, use the externally reachable API origin and make sure the
  backend allows the frontend origin through `FINBOT_API_CORS_ORIGINS`.
- The root Compose file does not require `finbot/config/.env` for basic local
  web startup; add that file only when you need real API keys or other local
  secrets inside containers.

## Health Checks

- Frontend readiness endpoint: `GET /healthz`
- Backend readiness endpoint: `GET /api/health`

## App Surfaces

- Dashboard home
- Simulations (leveraged funds + bond ladder)
- Backtesting (allocation builder + research follow-through)
- Optimizer (DCA + Pareto + efficient frontier)
- Monte Carlo (single asset + multi-asset)
- Walk-Forward
- Experiments
- Risk Analytics
- Portfolio Analytics
- Factor Analytics
- Real-Time Quotes
- Data Status
- Health Economics

## Notes

- The frontend depends on the FastAPI backend in `web/backend/`.
- `pnpm-lock.yaml` is the canonical frontend lockfile; do not add npm or yarn lockfiles.
- Shared client utilities live in `src/lib/`.
- Reusable UI components live in `src/components/`.
- Health-economics and analytics pages are part of the same product surface,
  not a separate application.
