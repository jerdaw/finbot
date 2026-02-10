from libs.api_manager._resource_groups.api_resource_groups import alpha_vantage_api_resouce_group
from libs.api_manager._utils.api import API

# AlphaVantage API constants
_ALPHA_VANTAGE_API_BASE_URL = "https://www.alphavantage.co/query"
_ALPHA_VANTAGE_API_ENDPOINTS = sorted(
    {
        "NEWS_SENTIMENT",
        "REAL_GDP",
        "REAL_GDP_PER_CAPITA",
        "TREASURY_YIELD",
        "FEDERAL_FUNDS_RATE",
        "CPI",
        "INFLATION",
        "RETAIL_SALES",
        "DURABLES",
        "UNEMPLOYMENT",
        "NONFARM_PAYROLL",
    },
)

alpha_vantage_api = API(
    identifier="alpha_vantage_api",
    resource_group=alpha_vantage_api_resouce_group,
    base_url=_ALPHA_VANTAGE_API_BASE_URL,
    endpoints=_ALPHA_VANTAGE_API_ENDPOINTS,
)
