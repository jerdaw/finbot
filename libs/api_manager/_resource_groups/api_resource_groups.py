from limits import RateLimitItemPerDay, RateLimitItemPerMinute, RateLimitItemPerSecond

from finbot.utils.request_utils.rate_limiter import RateLimiter
from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS
from libs.api_manager._utils.api_resource_group import APIResourceGroup

alpha_vantage_rapidapi_resouce_group = APIResourceGroup(
    identifier="alpha_vantage_rapidapi_resouce_group",
    rate_limit=RateLimiter(rate_limits="5/minute;500/day"),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
)

alpha_vantage_api_resouce_group = APIResourceGroup(
    identifier="alpha_vantage_api_resouce_group",
    rate_limit=RateLimiter(rate_limits="5/minute;25/day"),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
)

fred_api_resource_group = APIResourceGroup(
    identifier="fred_api_resource_group",
    rate_limit=RateLimiter(rate_limits="120/minute"),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
)

oanda_api_resource_group = APIResourceGroup(
    identifier="oanda_api_resource_group",
    rate_limit=RateLimiter(rate_limits="120/minute"),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
)

nasdaq_quandl_api_resource_group = APIResourceGroup(
    identifier="nasdaq_quandl_api_resource_group",
    rate_limit=RateLimiter(
        rate_limits=[RateLimitItemPerSecond(300, 10), RateLimitItemPerMinute(2000, 10), RateLimitItemPerDay(50000)],
    ),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
    concurrency_limit=1,
)

bureau_of_labour_statistics_api_2_resource_group = APIResourceGroup(
    identifier="bureau_of_labour_statistics_api_2_resource_group",
    rate_limit=RateLimiter(rate_limits=[RateLimitItemPerSecond(50, 10), RateLimitItemPerDay(500)]),
    retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
)
