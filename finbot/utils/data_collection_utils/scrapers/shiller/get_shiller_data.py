"""Compatibility alias: get_shiller_data -> get_shiller_ie_data."""

from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_ch26 import get_shiller_ch26
from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_ie_data import get_shiller_ie_data

# Alias for code ported from old finbot that used `get_shiller_data`
get_shiller_data = get_shiller_ie_data

__all__ = ["get_shiller_ch26", "get_shiller_data"]
