"""Aggregates all pre-configured API instances for bulk registration."""

from finbot.libs.api_manager._apis.alpaca_api import alpaca_api
from finbot.libs.api_manager._apis.alpha_vantage_api import alpha_vantage_api
from finbot.libs.api_manager._apis.alpha_vantage_rapidapi import alpha_vantage_rapidapi
from finbot.libs.api_manager._apis.fred_api import fred_api
from finbot.libs.api_manager._apis.twelvedata_api import twelvedata_api
from finbot.libs.api_manager._utils.api import API


def get_all_apis() -> dict[str, API]:
    """Return all pre-configured API instances keyed by identifier.

    Returns:
        Dictionary mapping API identifier strings to API instances.
    """
    apis = [alpaca_api, alpha_vantage_api, alpha_vantage_rapidapi, fred_api, twelvedata_api]
    return {api.identifier: api for api in apis}
