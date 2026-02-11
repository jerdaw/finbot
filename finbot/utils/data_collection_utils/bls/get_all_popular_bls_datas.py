"""Fetch all popular BLS economic data series.

Retrieves all series IDs marked as "popular" by the BLS API and fetches
their complete historical data. This provides a comprehensive snapshot of
key labor market and economic indicators tracked by BLS.

Popular series typically include:
    - Consumer Price Index (CPI)
    - Unemployment rates by region
    - Employment cost index
    - Producer price indexes

Data source: U.S. Bureau of Labor Statistics API
Update frequency: Varies by series (monthly, quarterly)
API endpoint: /timeseries/popular
"""

import json

from finbot.config import settings_accessors
from finbot.utils.data_collection_utils.bls.get_bls_data import get_bls_data
from finbot.utils.request_utils.request_handler import RequestHandler


def _get_popular_bls_series_ids():
    headers = {"Content-type": "application/json"}
    payload = json.dumps({"registrationkey": settings_accessors.get_us_bureau_of_labor_statistics_api_key()})
    json_data = RequestHandler().make_json_request(
        url="https://api.bls.gov/publicAPI/v2/timeseries/popular",
        payload_kwargs={"data": payload},
        headers=headers,
        request_type="POST",
    )
    popular_series_ids = [d["seriesID"] for d in json_data["Results"]["series"]]
    return popular_series_ids


def get_all_popular_bls_datas(start_date=None, end_date=None, check_update=False, force_update=False):
    popular_series = _get_popular_bls_series_ids()
    return get_bls_data(
        popular_series,
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


if __name__ == "__main__":
    print(get_all_popular_bls_datas())
