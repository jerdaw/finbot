"""Quantile-based outlier detection using Interquartile Range (IQR) method.

Detects outliers using the IQR (Interquartile Range) method, which is robust
to extreme values and non-normal distributions. Identifies values falling
outside the range [Q1 - k*IQR, Q3 + k*IQR] as outliers, where k is typically
1.5 (Tukey's fences) or 3.0 (far outliers).

Typical usage:
    ```python
    # Detect outliers using standard IQR (1.5x rule)
    mask = get_outliers_quantile(df, iqr_multiplier=1.5)

    # Detect and remove outliers
    df_clean = get_outliers_quantile(df, iqr_multiplier=1.5, remove=True)

    # Custom quantiles (10th-90th percentile range)
    mask = get_outliers_quantile(df, lower_quantile=0.1, upper_quantile=0.9)

    # Stricter outlier detection (3.0x IQR for far outliers)
    mask = get_outliers_quantile(df, iqr_multiplier=3.0)
    ```

IQR outlier detection:
    1. Calculate Q1 (25th percentile) and Q3 (75th percentile)
    2. Calculate IQR = Q3 - Q1
    3. Define outlier bounds:
       - Lower bound: Q1 - k * IQR
       - Upper bound: Q3 + k * IQR
    4. Values outside bounds are flagged as outliers

IQR multiplier guidelines:
    - 1.5: Standard Tukey fences (moderate outlier detection)
      - Flags ~0.7% of normal distribution as outliers
      - Good for data cleaning and EDA

    - 3.0: Far outliers only (conservative detection)
      - Flags ~0.0027% of normal distribution as outliers
      - Use when avoiding false positives is critical

Parameters:
    - lower_quantile: Lower percentile (default: 0.25 = Q1)
    - upper_quantile: Upper percentile (default: 0.75 = Q3)
    - iqr_multiplier: Multiplier for IQR bounds (default: 1.5)
    - remove: If True, remove outliers; if False, return boolean mask
    - inplace: Modify data in-place when remove=True

Features:
    - Robust to extreme values (uses quantiles, not mean/std)
    - Works with both DataFrames and Series
    - Column-wise detection for DataFrames
    - Optional in-place removal
    - Customizable quantile ranges and multipliers

Use cases:
    - Exploratory data analysis (identify unusual values)
    - Data cleaning before statistical analysis
    - Outlier removal before machine learning
    - Financial data (detect abnormal returns, volumes)
    - Sensor data (detect equipment malfunctions)

Advantages over Z-score method:
    - Does not assume normal distribution
    - More robust to extreme outliers
    - Works well with skewed distributions
    - Interpretable in terms of data quartiles

Trade-offs:
    - May miss outliers in heavy-tailed distributions
    - Less sensitive than Z-score method for normal data
    - Requires sufficient data for stable quantile estimation

Best practices:
    - Start with 1.5x multiplier, adjust based on domain knowledge
    - Visualize data before/after outlier removal (box plots)
    - Consider data context (outliers may be legitimate extreme events)
    - Document outlier removal decisions for reproducibility

Related modules: get_outliers_z_score (parametric alternative),
treat_outliers_cap (capping instead of removal), treat_outliers_transform
(transformation-based treatment).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_detection_to_pandas
from finbot.utils.pandas_utils.remove_masked_data import remove_masked_data


def _quantile_detection_logic(data: pd.Series, **kwargs: Any) -> pd.Series | None:
    q1 = data.quantile(kwargs["lower_quantile"])
    q3 = data.quantile(kwargs["upper_quantile"])
    iqr = q3 - q1
    lower_bound = q1 - kwargs["iqr_multiplier"] * iqr
    upper_bound = q3 + kwargs["iqr_multiplier"] * iqr
    mask = ~((data >= lower_bound) & (data <= upper_bound))
    if kwargs["remove"]:
        return remove_masked_data(data=data, mask=mask, inplace=kwargs["inplace"])
    return mask


def get_outliers_quantile(
    data: pd.DataFrame | pd.Series,
    lower_quantile: float = 0.25,
    upper_quantile: float = 0.75,
    iqr_multiplier: float = 1.5,
    remove: bool = False,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Detects and optionally removes outliers from a pandas Series using quantile-based method.

    Parameters:
        data (pd.DataFrame | pd.Series): The input data.
        lower_quantile (float, optional): The lower quantile threshold. Defaults to 0.25.
        upper_quantile (float, optional): The upper quantile threshold. Defaults to 0.75.
        iqr_multiplier (float, optional): The multiplier to calculate the interquartile range. Defaults to 1.5.
        remove (bool, optional): Whether to remove the outliers from the data. Defaults to False.
        inplace (bool, optional): Whether to modify the input data in-place. Defaults to False.

    Returns:
        pd.Series: The input data with outliers removed if `remove=True`, otherwise the input data as-is.
    """
    return _apply_detection_to_pandas(
        data=data,
        method=_quantile_detection_logic,
        lower_quantile=lower_quantile,
        upper_quantile=upper_quantile,
        iqr_multiplier=iqr_multiplier,
        remove=remove,
        inplace=inplace,
    )
