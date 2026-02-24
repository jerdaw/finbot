"""FRED (Federal Reserve Economic Data) API configuration.

Registers the FRED API with its resource group, response cache directory,
and processed data directory.
"""

from finbot.constants.path_constants import FRED_DATA_DIR, FRED_RESPONSES_DATA_DIR
from finbot.libs.api_manager._resource_groups.api_resource_groups import fred_api_resource_group
from finbot.libs.api_manager._utils.api import API

fred_api = API(
    identifier="fred_api",
    resource_group=fred_api_resource_group,
    response_save_dir=FRED_RESPONSES_DATA_DIR,
    data_save_dir=FRED_DATA_DIR,
)
