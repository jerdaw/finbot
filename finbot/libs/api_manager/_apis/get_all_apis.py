from finbot.libs.api_manager._apis.alpha_vantage_api import alpha_vantage_api
from finbot.libs.api_manager._apis.alpha_vantage_rapidapi import alpha_vantage_rapidapi
from finbot.libs.api_manager._apis.fred_api import fred_api
from finbot.libs.api_manager._utils.api import API


def get_all_apis() -> dict[str, API]:
    apis = [alpha_vantage_api, alpha_vantage_rapidapi, fred_api]
    return {api.identifier: api for api in apis}
