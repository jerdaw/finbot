from __future__ import annotations

import pandas as pd

from config import logger


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.
    """
    original_count = len(data)
    data = data.drop_duplicates()
    logger.info(f"Removed {original_count - len(data)} duplicates")
    return data
