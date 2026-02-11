"""Transform outliers using custom transformation functions.

Treats outliers by applying user-defined transformation functions to outlier
values only, leaving normal values unchanged. Allows flexible, domain-specific
outlier treatment beyond simple capping or removal.

**STATUS: NOT IMPLEMENTED** - This module raises NotImplementedError and has
not been confirmed to work as intended.

Typical usage (when implemented):
    ```python
    # Detect outliers first
    mask = get_outliers_quantile(df, iqr_multiplier=1.5)

    # Transform outliers using logarithm
    df_transformed = transform_outliers(df, transform_func=np.log1p)

    # Custom transformation (cap at median)
    transform_func = lambda s: pd.Series([df[s.name].median()] * len(s))
    df_transformed = transform_outliers(df, transform_func=transform_func)
    ```

Transformation-based treatment:
    - Applies transformation only to detected outliers
    - Leaves non-outlier values unchanged
    - Preserves sample size
    - Allows domain-specific treatment strategies

Parameters (when implemented):
    - data: DataFrame to treat
    - transform_func: Callable that transforms outlier Series
    - mask: Boolean mask identifying outliers
    - **kwargs: Additional parameters for transformation function

Common transformation strategies:
    - Logarithmic: np.log1p (compresses large values)
    - Square root: np.sqrt (reduces skew)
    - Box-Cox: scipy.stats.boxcox (normalizes distribution)
    - Rank-based: Convert to percentile ranks
    - Median replacement: Replace with column median
    - Mean replacement: Replace with column mean
    - Smoothing: Apply moving average to outliers

Advantages:
    - Flexible (arbitrary transformation functions)
    - Preserves sample size (no data loss)
    - Can be tailored to domain knowledge
    - Useful for ML preprocessing

Disadvantages:
    - Requires choosing appropriate transformation
    - May introduce non-linear artifacts
    - Interpretation becomes more complex
    - Different transformations for different columns can be confusing

Use cases (when implemented):
    - Reducing influence of extreme values
    - Normalizing skewed distributions
    - Preparing data for algorithms sensitive to outliers
    - Domain-specific treatments (e.g., financial data)

Transformation function requirements:
    - Input: pd.Series of outlier values
    - Output: pd.Series of transformed values (same length)
    - Must handle NaN values appropriately
    - Should not raise exceptions on edge cases

Example transformations:
    ```python
    # Log transformation (for positive data)
    transform_func = lambda s: np.log1p(s.abs())

    # Replace with column mean
    transform_func = lambda s: pd.Series([df[s.name].mean()] * len(s))

    # Apply Box-Cox
    from scipy.stats import boxcox

    transform_func = lambda s: pd.Series(boxcox(s)[0])

    # Rank transformation
    transform_func = lambda s: s.rank() / len(s)
    ```

Best practices (when implemented):
    - Test transformation on sample data first
    - Document transformation rationale
    - Visualize before/after distributions
    - Ensure transformation is appropriate for analysis goals
    - Consider reversibility if needed

Alternative approaches:
    - **treat_outliers_cap**: Simple capping (no transformation)
    - **treat_outliers_remove**: Complete removal
    - **Robust scaling**: Use robust scalers (median, IQR) instead of mean, std
    - **Imputation**: Treat outliers as missing and impute

Related modules: treat_outliers_cap (capping), treat_outliers_remove (removal),
get_outliers_quantile (detection), scalers_normalizers (whole-column
transformations).
"""

from collections.abc import Callable

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _transform_outliers_logic(
    data: pd.Series,
    mask: pd.Series,
    transform_func: Callable[[pd.Series], pd.Series],
    **kwargs,
) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return data.where(~mask, transform_func(data[mask]))  # type: ignore[unreachable]


def transform_outliers(data: pd.DataFrame, transform_func: Callable[[pd.Series], pd.Series], **kwargs) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(  # type: ignore[unreachable]
        data=data,
        method=_transform_outliers_logic,
        transform_func=transform_func,
        **kwargs,
    )
