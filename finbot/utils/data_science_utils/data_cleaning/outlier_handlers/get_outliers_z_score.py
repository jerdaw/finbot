"""Z-score based outlier detection for normally distributed data.

Detects outliers using standardized scores (Z-scores), which measure how many
standard deviations a value is from the mean. Best suited for data that
approximately follows a normal distribution.

**STATUS: NOT IMPLEMENTED** - This module raises NotImplementedError and has
not been confirmed to work as intended. Use get_outliers_quantile for a
working alternative.

Typical usage (when implemented):
    ```python
    # Detect outliers using standard threshold (3 sigma)
    mask = get_outliers_z_score(df, threshold=3.0)

    # More aggressive outlier detection (2 sigma)
    mask = get_outliers_z_score(df, threshold=2.0)

    # Detect and remove outliers
    df_clean = get_outliers_z_score(df, threshold=3.0, remove=True)
    ```

Z-score outlier detection:
    1. Calculate mean (mu) and standard deviation (sigma) for each column
    2. Compute Z-score for each value: Z = (X - mu) / sigma
    3. Flag values with |Z| > threshold as outliers
    4. Common thresholds:
       - 2.0: ~5% of normal distribution (95% within +/-2 sigma)
       - 3.0: ~0.3% of normal distribution (99.7% within +/-3 sigma)
       - 4.0: ~0.006% of normal distribution (very conservative)

Parameters (when implemented):
    - threshold: Z-score threshold for outlier detection (default: 3.0)
    - remove: If True, remove outliers; if False, return boolean mask
    - inplace: Modify data in-place when remove=True

Assumptions:
    - Data is approximately normally distributed
    - Mean and standard deviation are meaningful for the data
    - Outliers are defined by distance from mean in standard deviations

Advantages:
    - Simple and interpretable (standard deviations from mean)
    - Well-suited for normally distributed data
    - Computationally efficient
    - Familiar to statisticians

Disadvantages:
    - **Assumes normal distribution** (may fail for skewed data)
    - Mean and std are sensitive to outliers (circular problem)
    - May miss outliers in heavy-tailed distributions
    - Less robust than quantile-based methods

When to use (once implemented):
    - Data is approximately normally distributed
    - You need standardized measure of deviation
    - Statistical analysis requires normality assumption

When NOT to use:
    - **Currently: Never (not implemented)**
    - Skewed or heavy-tailed distributions → use quantile method
    - Small sample sizes (unstable mean/std estimates)
    - Data with extreme outliers (contaminate mean/std)

Alternative: get_outliers_quantile
    - Use IQR method instead (robust, non-parametric)
    - Works with any distribution shape
    - Not affected by extreme outliers
    - Currently implemented and tested

Dependencies: scipy (scipy.stats), numpy

Related modules: get_outliers_quantile (robust alternative - RECOMMENDED),
treat_outliers_cap (capping outliers), treat_outliers_remove (removal).
"""

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_detection_to_pandas
from finbot.utils.pandas_utils.remove_masked_data import remove_masked_data


def _z_score_detection_logic(data: pd.Series, **kwargs: Any) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    threshold = kwargs.get("threshold", 3)  # type: ignore[unreachable]
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
    return _apply_detection_to_pandas(  # type: ignore[unreachable]
        data=data,
        method=_z_score_detection_logic,
        threshold=threshold,
        remove=remove,
        inplace=inplace,
    )
