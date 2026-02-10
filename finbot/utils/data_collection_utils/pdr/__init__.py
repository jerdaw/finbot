"""
Custom apis built on the pandas_datareader api for various endpoints.
"""

from __future__ import annotations

from finbot.utils.data_collection_utils.pdr._utils import get_pdr_base

__all__ = [
    "get_pdr_base",
]
