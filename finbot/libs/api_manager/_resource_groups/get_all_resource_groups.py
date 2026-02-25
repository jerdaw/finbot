"""Aggregates all pre-configured resource group instances for bulk registration."""

from finbot.libs.api_manager._resource_groups.api_resource_groups import (
    alpaca_api_resource_group,
    alpha_vantage_api_resouce_group,
    alpha_vantage_rapidapi_resouce_group,
    bureau_of_labour_statistics_api_2_resource_group,
    fred_api_resource_group,
    nasdaq_quandl_api_resource_group,
    oanda_api_resource_group,
    twelvedata_api_resource_group,
)
from finbot.libs.api_manager._utils.api_resource_group import APIResourceGroup


def get_all_resource_groups() -> dict[str, APIResourceGroup]:
    """Return all pre-configured resource groups keyed by identifier.

    Returns:
        Dictionary mapping resource group identifier strings to
        APIResourceGroup instances.
    """
    resource_groups = [
        alpha_vantage_api_resouce_group,
        alpha_vantage_rapidapi_resouce_group,
        alpaca_api_resource_group,
        bureau_of_labour_statistics_api_2_resource_group,
        fred_api_resource_group,
        nasdaq_quandl_api_resource_group,
        oanda_api_resource_group,
        twelvedata_api_resource_group,
    ]
    return {rg.identifier: rg for rg in resource_groups}
