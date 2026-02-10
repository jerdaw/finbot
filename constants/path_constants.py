"""
Path Constants

Centralizes filesystem path constants for the application.
"""
from __future__ import annotations

import logging as logger
from pathlib import Path


def _process_dir(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    return d.resolve()


# Root directory
ROOT_DIR = _process_dir(Path(__file__).parent.parent.resolve(strict=True))

# Subdirectories under ROOT_DIR
ASSETS_DIR = _process_dir(ROOT_DIR / "assets")
BACKUPS_DIR = _process_dir(ROOT_DIR / "backups")
CONFIG_DIR = _process_dir(ROOT_DIR / "config")
CONSTANTS_DIR = _process_dir(ROOT_DIR / "constants")
DOCS_DIR = _process_dir(ROOT_DIR / "docs")
LOGS_DIR = _process_dir(ROOT_DIR / "logs")
NOTEBOOKS_DIR = _process_dir(ROOT_DIR / "notebooks")
SCRIPTS_DIR = _process_dir(ROOT_DIR / "scripts")
TESTS_DIR = _process_dir(ROOT_DIR / "tests")

# Main package directory
FINBOT_DIR = _process_dir(ROOT_DIR / "finbot")

# Subdirectories under FINBOT_DIR
DATA_DIR = _process_dir(FINBOT_DIR / "data")
MODELS_DIR = _process_dir(FINBOT_DIR / "models")
SERVICES_DIR = _process_dir(FINBOT_DIR / "services")
UTILS_DIR = _process_dir(FINBOT_DIR / "utils")

# Subdirectories under CONSTANTS_DIR
TRACKED_COLLECTIONS_DIR = _process_dir(CONSTANTS_DIR / "tracked_collections")

# Subdirectories under DATA_DIR
ALPHA_VANTAGE_DATA_DIR = _process_dir(DATA_DIR / "alpha_vantage_data")
BLS_DATA_DIR = _process_dir(DATA_DIR / "bls_data")
CUSTOM_DATA_DIR = _process_dir(DATA_DIR / "custom_data")
FRED_DATA_DIR = _process_dir(DATA_DIR / "fred_data")
GOOGLE_FINANCE_DATA_DIR = _process_dir(DATA_DIR / "google_finance_data")
MSCI_DATA_DIR = _process_dir(DATA_DIR / "msci_data")
MULTPL_DATA_DIR = _process_dir(DATA_DIR / "multpl_data")
RESPONSES_DATA_DIR = _process_dir(DATA_DIR / "responses")
SHILLER_DATA_DIR = _process_dir(DATA_DIR / "shiller_data")
YFINANCE_DATA_DIR = _process_dir(DATA_DIR / "yfinance_data")

# New data directories (from finbot's secrets.paths)
SIMULATIONS_DATA_DIR = _process_dir(DATA_DIR / "simulations")
BACKTESTS_DATA_DIR = _process_dir(DATA_DIR / "backtests")
PRICE_HISTORIES_DATA_DIR = _process_dir(DATA_DIR / "price_histories")
LONGTERMTRENDS_DATA_DIR = _process_dir(DATA_DIR / "longtermtrends_data")

# Subdirectories under RESPONSES_DATA_DIR
FRED_RESPONSES_DATA_DIR = _process_dir(RESPONSES_DATA_DIR / "fred_responses")
ALPHA_VANTAGE_RESPONSES_DATA_DIR = _process_dir(RESPONSES_DATA_DIR / "alpha_vantage_responses")
BLS_RESPONSES_DATA_DIR = _process_dir(RESPONSES_DATA_DIR / "bls_responses")

# Subdirectories under TESTS_DIR
UNIT_TESTS_DIR = _process_dir(TESTS_DIR / "unit")


if __name__ == "__main__":
    try:
        cur_globals = list(globals().items())
        for name, value in cur_globals:
            if not name.startswith("_"):
                print(f"{name}: {value}")
    except Exception as e:
        logger.error(f"Failed to initialize directories: {e}")
        raise
