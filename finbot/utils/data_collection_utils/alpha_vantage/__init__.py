"""
The alpha_vantage module provides a simplified interface to the Alpha Vantage API for
retrieving a wide range of financial and economic data. It encapsulates the complexity
of making API calls, handling responses, and managing errors, offering easy-to-use
functions for accessing various data endpoints.

Key Features:
- Simplified access to a variety of economic and financial data points.
- Functions are pre-decorated with logging for transparent and traceable API interactions.
- Error handling is built into the functions, ensuring robustness in API usage.

The module includes functions for retrieving data such as stock quotes, economic indicators,
forex rates, and more. Each function corresponds to a specific Alpha Vantage API endpoint
and is designed for ease of use.

Usage Example:

    from alpha_vantage import get_global_quote

    quote_data = get_global_quote('MSFT')

Note: A valid Alpha Vantage API key is required to authenticate requests. For detailed
information on available endpoints and data formats, refer to the Alpha Vantage
documentation at: https://www.alphavantage.co/documentation/
"""
from __future__ import annotations

from finbot.utils.data_collection_utils.alpha_vantage.cpi import get_cpi
from finbot.utils.data_collection_utils.alpha_vantage.daily_sentiment import get_daily_sentiment
from finbot.utils.data_collection_utils.alpha_vantage.durables import get_durables
from finbot.utils.data_collection_utils.alpha_vantage.federal_funds_rate import get_federal_funds_rate
from finbot.utils.data_collection_utils.alpha_vantage.global_quote import get_global_quote
from finbot.utils.data_collection_utils.alpha_vantage.inflation import get_inflation
from finbot.utils.data_collection_utils.alpha_vantage.nonfarm_payroll import get_nonfarm_payroll
from finbot.utils.data_collection_utils.alpha_vantage.real_gdp import get_real_gdp
from finbot.utils.data_collection_utils.alpha_vantage.real_gdp_per_capita import get_real_gdp_per_capita
from finbot.utils.data_collection_utils.alpha_vantage.retail_sales import get_retail_sales
from finbot.utils.data_collection_utils.alpha_vantage.sentiment import get_sentiment
from finbot.utils.data_collection_utils.alpha_vantage.time_series_daily_adjusted import get_time_series_daily_adjusted
from finbot.utils.data_collection_utils.alpha_vantage.time_series_intraday import get_time_series_intraday
from finbot.utils.data_collection_utils.alpha_vantage.treasury_yields import get_treasury_yields
from finbot.utils.data_collection_utils.alpha_vantage.unemployment import get_unemployment

__all__ = [
    "get_cpi",
    "get_daily_sentiment",
    "get_durables",
    "get_federal_funds_rate",
    "get_global_quote",
    "get_inflation",
    "get_time_series_intraday",
    "get_nonfarm_payroll",
    "get_real_gdp_per_capita",
    "get_real_gdp",
    "get_retail_sales",
    "get_sentiment",
    "get_time_series_intraday",
    "get_time_series_daily_adjusted",
    "get_treasury_yields",
    "get_unemployment",
]
