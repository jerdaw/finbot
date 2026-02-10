from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from config import logger
from finbot.utils.pandas_utils.get_data_mask import get_data_mask


def identify_corrupted_data(
    data: pd.Series | pd.DataFrame,
    corruption_criteria: dict[str | None, Callable[[Any], bool]],
    use_vectorization: bool = False,
) -> pd.Series | pd.DataFrame:
    """
    This function is a thin wrapper around get_data_mask that identifies corrupted data based on the given criteria.

    Parameters:
    data (Union[pd.Series, pd.DataFrame]): The DataFrame or Series to be checked for corruption.
    corruption_criteria (Dict[Union[str, None], Callable[[Any], bool]]): Criteria for identifying corrupted data.
    use_vectorization (Optional[bool]): If True, forces the use of vectorized operations. If False, uses 'apply'.
        If None, auto-detects the best approach.

    Returns:
    Union[pd.Series, pd.DataFrame]: A boolean mask indicating corrupted data.
    """
    logger.info(
        "Vectorization is %s for this operation.",
        "enabled" if use_vectorization else "disabled",
    )
    return get_data_mask(data, corruption_criteria, use_vectorization)
