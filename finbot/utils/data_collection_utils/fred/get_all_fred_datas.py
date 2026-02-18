"""Stub module for batch FRED data collection.

This module provides a convenience function for collecting all tracked
FRED economic data. Currently a placeholder - implement as needed.
"""

from __future__ import annotations


def get_all_fred_datas() -> None:
    """Collect all tracked FRED economic data series.

    This is a convenience function that would typically:
    1. Read list of tracked FRED symbols
    2. Fetch data for each series
    3. Save to appropriate data directory

    Note:
        This is currently a placeholder stub. Implement as needed
        or use individual get_fred_data() calls instead.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "get_all_fred_datas() is not implemented. "
        "Use finbot.utils.data_collection_utils.fred.get_fred_data() for individual series."
    )
