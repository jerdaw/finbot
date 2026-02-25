"""Alpaca Market Data API configuration.

Registers the Alpaca data API for real-time stock snapshots
via the IEX feed (free tier).
"""

from finbot.libs.api_manager._resource_groups.api_resource_groups import alpaca_api_resource_group
from finbot.libs.api_manager._utils.api import API

_ALPACA_DATA_BASE_URL = "https://data.alpaca.markets"
_ALPACA_ENDPOINTS = sorted(
    {
        "v2/stocks/snapshots",
        "v2/stocks/quotes/latest",
        "v2/stocks/trades/latest",
    },
)

alpaca_api = API(
    identifier="alpaca_api",
    resource_group=alpaca_api_resource_group,
    base_url=_ALPACA_DATA_BASE_URL,
    endpoints=_ALPACA_ENDPOINTS,
)
