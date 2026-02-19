# Finbot Web Frontend

Professional web application for Finbot's financial simulation, backtesting, and analysis platform.

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Pydantic v2 + uvicorn |
| Frontend | Next.js 15 (App Router) + TypeScript |
| Styling | Tailwind CSS v4 + shadcn/ui |
| Financial Charts | TradingView Lightweight Charts v5 |
| General Charts | Recharts |
| Data Fetching | TanStack Query v5 |
| State | Zustand |
| Animations | Framer Motion |
| Deployment | Docker Compose |

## Quick Start

### Development (local)

```bash
# Terminal 1: Start backend API
DYNACONF_ENV=development uv run uvicorn web.backend.main:app --reload --port 8000

# Terminal 2: Start frontend dev server
cd web/frontend
pnpm dev
```

Open http://localhost:3000

### Docker

```bash
docker compose up finbot-api finbot-web
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/simulations/funds` | GET | List available funds |
| `/api/simulations/run` | GET | Run fund simulations |
| `/api/backtesting/strategies` | GET | List strategies |
| `/api/backtesting/run` | POST | Run backtest |
| `/api/optimizer/run` | POST | DCA optimizer |
| `/api/monte-carlo/run` | POST | Monte Carlo simulation |
| `/api/health-economics/qaly` | POST | QALY simulation |
| `/api/health-economics/cea` | POST | Cost-effectiveness analysis |
| `/api/health-economics/treatment-optimizer` | POST | Treatment optimizer |
| `/api/health-economics/scenarios` | POST | Clinical scenarios |
| `/api/experiments/list` | GET | List experiments |
| `/api/experiments/compare` | POST | Compare experiments |
| `/api/walk-forward/run` | POST | Walk-forward analysis |
| `/api/data-status/` | GET | Data freshness |

Swagger UI available at http://localhost:8000/docs

## Pages

- **Dashboard** (`/`) — Overview with summary stats and quick links
- **Simulations** (`/simulations`) — Fund simulation with overlay charts
- **Backtesting** (`/backtesting`) — 12 strategies with dynamic parameter forms
- **Monte Carlo** (`/monte-carlo`) — Percentile fan charts and histograms
- **Optimizer** (`/optimizer`) — DCA grid search with heatmaps
- **Walk-Forward** (`/walk-forward`) — Out-of-sample validation
- **Health Economics** (`/health-economics`) — QALY, CEA, treatment optimization, clinical scenarios
- **Experiments** (`/experiments`) — Compare backtest runs
- **Data Status** (`/data-status`) — Data freshness monitoring

## Environment Variables

### Backend
- `DYNACONF_ENV` — `development` or `production`
- `FINBOT_API_CORS_ORIGINS` — Allowed origins (default: `["http://localhost:3000"]`)
- `FINBOT_API_HOST` — Bind host (default: `0.0.0.0`)
- `FINBOT_API_PORT` — Port (default: `8000`)

### Frontend
- `NEXT_PUBLIC_API_URL` — Backend API URL (default: `http://localhost:8000`)

## Project Structure

```
web/
  backend/
    main.py              # FastAPI app
    config.py            # Settings
    dependencies.py      # Shared deps
    routers/             # 8 API routers
    schemas/             # Pydantic request/response models
    services/
      serializers.py     # DataFrame→JSON helpers
  frontend/
    src/
      app/               # 9 route pages
      components/
        layout/          # Sidebar, header, providers
        charts/          # TradingView + Recharts wrappers
        common/          # Stat card, table, skeleton, error boundary
        ui/              # shadcn components
      lib/               # API client, formatting, constants
      hooks/             # Theme hook
      stores/            # Zustand stores
      types/             # TypeScript type definitions
  Dockerfile.backend
  Dockerfile.frontend
```
