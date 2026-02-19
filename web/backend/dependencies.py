"""Shared FastAPI dependencies."""

from pathlib import Path

from finbot.constants.path_constants import BACKTESTS_DATA_DIR

EXPERIMENT_DIR = Path(BACKTESTS_DATA_DIR) / "experiments"
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
