"""Remove outliers by deleting rows containing outlier values.

Treats outliers by completely removing rows that contain outlier values.
This is the most aggressive outlier treatment method and results in data loss.

**STATUS: NOT IMPLEMENTED** - This module raises NotImplementedError and has
not been confirmed to work as intended. Use get_outliers_quantile with
remove=True for working alternative.

Typical usage (when implemented):
    ```python
    # Detect outliers first
    mask = get_outliers_quantile(df, iqr_multiplier=1.5)

    # Remove rows containing outliers
    df_clean = remove_outliers(df, mask=mask)
    ```

Outlier removal strategy:
    - Takes boolean mask identifying outliers
    - Removes entire rows where mask is True
    - Reduces dataset size
    - Completely eliminates outlier influence

Parameters (when implemented):
    - data: DataFrame to treat
    - mask: Boolean Series/DataFrame identifying outliers

Advantages:
    - Completely eliminates outlier influence
    - Simplest outlier treatment approach
    - No bias introduced (unlike capping/transformation)
    - Clean dataset for downstream analysis

Disadvantages:
    - **Loss of data** (reduces sample size)
    - May remove valid extreme events
    - Can introduce selection bias
    - Problematic for time series (creates gaps)
    - Cannot be used if sample size is already small

When to use (once implemented):
    - Large dataset where data loss is acceptable
    - Outliers are clearly data errors (not extreme events)
    - Sample size remains sufficient after removal
    - Statistical tests require clean distributions

When NOT to use:
    - **Currently: Never (not implemented)**
    - Small datasets (loss of statistical power)
    - Time series analysis (gaps problematic)
    - Outliers represent legitimate extreme events
    - Regulatory requirements mandate data retention

Alternative treatments:
    - **treat_outliers_cap**: Cap values at limits (preserves sample size)
    - **treat_outliers_transform**: Apply transformations (log, sqrt) to reduce skew
    - **Imputation**: Replace outliers with imputed values
    - **Robust methods**: Use algorithms insensitive to outliers

Deletion strategies:
    - Listwise deletion: Remove entire row if ANY column has outlier
    - Column-wise deletion: Remove only outlier values (creates NaN)
    - Conditional deletion: Remove only if multiple outliers in same row

Best practices (when implemented):
    - Document how many rows removed and why
    - Check if removed data has systematic patterns
    - Verify remaining sample size is sufficient
    - Report removal criteria and impact on results
    - Consider if removal introduces bias

Note: Use get_outliers_quantile(df, remove=True) for working implementation
of outlier removal via IQR method.

Related modules: get_outliers_quantile (detection + removal),
treat_outliers_cap (capping alternative), treat_outliers_transform
(transformation alternative).
"""

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _remove_outliers_logic(data: pd.Series, **kwargs) -> pd.Series:
    """Remove outliers from the Series."""
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return data[~kwargs.get("mask")]  # type: ignore[unreachable]


def remove_outliers(data: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(  # type: ignore[unreachable]
        data=data,
        method=_remove_outliers_logic,
        mask=mask,
    )
