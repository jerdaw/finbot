"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.backend.config import settings
from web.backend.routers import (
    backtesting,
    data_status,
    experiments,
    health_economics,
    monte_carlo,
    optimizer,
    simulations,
    walkforward,
)

app = FastAPI(
    title="Finbot API",
    description="Financial simulation, backtesting, and analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulations.router, prefix="/api/simulations", tags=["simulations"])
app.include_router(backtesting.router, prefix="/api/backtesting", tags=["backtesting"])
app.include_router(optimizer.router, prefix="/api/optimizer", tags=["optimizer"])
app.include_router(monte_carlo.router, prefix="/api/monte-carlo", tags=["monte-carlo"])
app.include_router(health_economics.router, prefix="/api/health-economics", tags=["health-economics"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(walkforward.router, prefix="/api/walk-forward", tags=["walk-forward"])
app.include_router(data_status.router, prefix="/api/data-status", tags=["data-status"])


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
