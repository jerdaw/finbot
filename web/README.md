# Finbot Web Frontend

Professional web application for Finbot's financial simulation, backtesting,
analytics, and health-economics research workflows.

## Architecture

| Layer            | Technology                           |
| ---------------- | ------------------------------------ |
| Backend API      | FastAPI + Pydantic v2 + uvicorn      |
| Frontend         | Next.js 16 (App Router) + TypeScript |
| Styling          | Tailwind CSS v4 + shadcn/ui          |
| Financial Charts | TradingView Lightweight Charts v5    |
| General Charts   | Recharts                             |
| Data Fetching    | TanStack Query v5                    |
| State            | Zustand                              |
| Animations       | Framer Motion                        |
| Deployment       | Docker Compose                       |

## Quick Start

### Development (local)

```bash
# Install backend/frontend extras once
uv sync --extra web --extra dashboard

# Terminal 1: Start backend API
DYNACONF_ENV=development uv run --extra web uvicorn web.backend.main:app --reload --port 8000

# Terminal 2: Start frontend dev server
cd web/frontend
pnpm dev
```

Open http://localhost:3000

### Docker

```bash
docker compose up finbot-api finbot-web
```

## Representative API Endpoints

| Endpoint                                    | Method | Description                        |
| ------------------------------------------- | ------ | ---------------------------------- |
| `/api/health`                               | GET    | Health check                       |
| `/api/simulations/funds`                    | GET    | List available funds               |
| `/api/simulations/run`                      | GET    | Run fund simulations               |
| `/api/simulations/bond-ladder/run`          | POST   | Run bond ladder research           |
| `/api/backtesting/strategies`               | GET    | List strategies                    |
| `/api/backtesting/run`                      | POST   | Run backtest                       |
| `/api/optimizer/run`                        | POST   | DCA optimizer                      |
| `/api/optimizer/pareto/run`                 | POST   | Strategy Pareto sweep              |
| `/api/optimizer/efficient-frontier/run`     | POST   | Efficient frontier analysis        |
| `/api/monte-carlo/run`                      | POST   | Monte Carlo simulation             |
| `/api/monte-carlo/multi-asset/run`          | POST   | Correlated multi-asset Monte Carlo |
| `/api/health-economics/qaly`                | POST   | QALY simulation                    |
| `/api/health-economics/cea`                 | POST   | Cost-effectiveness analysis        |
| `/api/health-economics/treatment-optimizer` | POST   | Treatment optimizer                |
| `/api/health-economics/scenarios`           | POST   | Clinical scenarios                 |
| `/api/experiments/list`                     | GET    | List experiments                   |
| `/api/experiments/compare`                  | POST   | Compare experiments                |
| `/api/walk-forward/run`                     | POST   | Walk-forward analysis              |
| `/api/data-status/`                         | GET    | Data freshness                     |
| `/api/risk-analytics/var`                   | POST   | VaR and CVaR analysis              |
| `/api/portfolio-analytics/rolling`          | POST   | Rolling portfolio metrics          |
| `/api/realtime-quotes/quote`                | GET    | Quote lookup                       |
| `/api/factor-analytics/regression`          | POST   | Factor regression                  |

Swagger UI available at http://localhost:8000/docs

## Pages

- **Dashboard** (`/`) — Overview with summary stats and quick links
- **Simulations** (`/simulations`) — Leveraged-fund and bond-ladder research with overlay charts
- **Backtesting** (`/backtesting`) — 13 strategies with allocation builder, benchmark/cashflow diagnostics, and walk-forward handoff
- **Monte Carlo** (`/monte-carlo`) — Single-asset and multi-asset percentile fan charts with correlation views
- **Optimizer** (`/optimizer`) — DCA grids, Pareto sweeps, and efficient-frontier research
- **Walk-Forward** (`/walk-forward`) — Out-of-sample validation
- **Health Economics** (`/health-economics`) — QALY, CEA, treatment optimization, clinical scenarios
- **Experiments** (`/experiments`) — Compare backtest runs
- **Risk Analytics** (`/risk-analytics`) — VaR, stress, Kelly, and related diagnostics
- **Portfolio Analytics** (`/portfolio-analytics`) — Rolling metrics, benchmark, drawdown, and diversification views
- **Factor Analytics** (`/factor-analytics`) — Factor regression, attribution, and risk decomposition
- **Real-Time Quotes** (`/realtime-quotes`) — Multi-provider market quote view
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
    routers/             # 12 API routers
    schemas/             # Pydantic request/response models
    services/
      serializers.py     # DataFrame→JSON helpers
  frontend/
    src/
      app/               # 13 route pages (dashboard + 12 task pages)
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
