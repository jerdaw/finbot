import numpy as np
import pandas as pd
from scipy import stats

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_detection_to_pandas
from finbot.utils.pandas_utils.remove_masked_data import remove_masked_data


def _z_score_detection_logic(data: pd.Series, **kwargs) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    threshold = kwargs.get("threshold", 3)
    z_scores = np.abs(stats.zscore(data, nan_policy="omit"))
    mask = z_scores > threshold

    if kwargs.get("remove"):
        return remove_masked_data(data=data, mask=mask, inplace=kwargs.get("inplace"))
    return mask


def get_outliers_z_score(
    data: pd.Series,
    threshold: float = 3.0,
    remove: bool = False,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_detection_to_pandas(
        data=data,
        method=_z_score_detection_logic,
        threshold=threshold,
        remove=remove,
        inplace=inplace,
    )
