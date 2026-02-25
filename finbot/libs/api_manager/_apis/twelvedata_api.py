"""Twelve Data API configuration.

Registers the Twelve Data API for real-time quotes covering
US and Canadian (TSX/TSXV) markets.
"""

from finbot.libs.api_manager._resource_groups.api_resource_groups import twelvedata_api_resource_group
from finbot.libs.api_manager._utils.api import API

_TWELVEDATA_BASE_URL = "https://api.twelvedata.com"
_TWELVEDATA_ENDPOINTS = sorted(
    {
        "quote",
        "price",
        "time_series",
    },
)

twelvedata_api = API(
    identifier="twelvedata_api",
    resource_group=twelvedata_api_resource_group,
    base_url=_TWELVEDATA_BASE_URL,
    endpoints=_TWELVEDATA_ENDPOINTS,
)
