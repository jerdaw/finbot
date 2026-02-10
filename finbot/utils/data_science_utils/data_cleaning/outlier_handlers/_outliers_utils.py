from collections.abc import Callable

import pandas as pd


def _apply_detection_to_pandas(data: pd.Series | pd.DataFrame, method: Callable, **kwargs) -> pd.Series | pd.DataFrame:
    """
    Apply outlier detection method to pandas Series or DataFrame.

    Args:
        data (pd.Series | pd.DataFrame): The input data to apply outlier detection on.
        method (Callable): The outlier detection method to apply.
        **kwargs: Additional keyword arguments to pass to the outlier detection method.

    Returns:
        pd.Series | pd.DataFrame: The result of applying the outlier detection method to the input data.
    """

    def apply_method_if_numeric(data, method, **kwargs):
        if data.dtype.kind in "biufcm":
            return method(data=data, **kwargs)
        else:
            raise ValueError("Data must be numeric or convertible to numeric.")

    if isinstance(data, pd.Series):
        return apply_method_if_numeric(data, method, **kwargs)
    elif isinstance(data, pd.DataFrame):
        return data.apply(lambda col: apply_method_if_numeric(col, method, **kwargs))
    raise ValueError("Input data must be a pandas Series or DataFrame.")


def _apply_treatment_to_pandas(data: pd.Series | pd.DataFrame, method: Callable, **kwargs) -> pd.Series | pd.DataFrame:
    """
    Apply outlier treatment method to pandas Series or DataFrame.

    Args:
        data (pd.Series | pd.DataFrame): The input data to apply outlier treatment on.
        method (Callable): The outlier treatment method to apply.
        **kwargs: Additional keyword arguments to pass to the outlier treatment method.

    Returns:
        pd.Series | pd.DataFrame: The result of applying the outlier treatment method to the input data.
    """
    if isinstance(data, pd.Series):
        return method(data=data, **kwargs) if data.dtype.kind in "biufcm" else data
    if isinstance(data, pd.DataFrame):
        return data.apply(lambda col: method(data=col, **kwargs) if col.dtype.kind in "biufcm" else col)
    raise ValueError("Input data must be a pandas Series or DataFrame.")
