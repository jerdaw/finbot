"""Stub module for batch yfinance data collection.

This module provides a convenience function for collecting all tracked
yfinance data. Currently a placeholder - implement as needed.
"""

from __future__ import annotations


def get_all_yfinance_datas() -> None:
    """Collect all tracked yfinance price histories.

    This is a convenience function that would typically:
    1. Read list of tracked tickers
    2. Fetch price histories for each
    3. Save to appropriate data directory

    Note:
        This is currently a placeholder stub. Implement as needed
        or use individual get_history() calls instead.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "get_all_yfinance_datas() is not implemented. "
        "Use finbot.utils.data_collection_utils.yfinance.get_history() for individual tickers."
    )
