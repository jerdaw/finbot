# Finbot Frontend

Next.js App Router frontend for Finbot's quantitative research platform.

The frontend exposes 13 routes in total: the dashboard home page plus 12
task-specific pages spanning simulations, backtesting, analytics, and health
economics.

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
corepack pnpm test:e2e   # Playwright smoke coverage (requires backend target)
```

## App Surfaces

- Dashboard home
- Simulations
- Backtesting
- Optimizer
- Monte Carlo
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
- Shared client utilities live in `src/lib/`.
- Reusable UI components live in `src/components/`.
- Health-economics and analytics pages are part of the same product surface,
  not a separate application.
