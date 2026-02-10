from typing import Literal

import pandas as pd

from config import logger


def _validate_params(datas: list[pd.DataFrame | pd.Series], method: Literal["pearson", "kendall", "spearman"]) -> None:
    if not isinstance(datas, list):
        raise ValueError("Input data must be a list of pandas DataFrame or Series.")

    if not datas:
        raise ValueError("Value Error: Input data list cannot be empty.")

    for item in datas:
        if not isinstance(item, pd.DataFrame | pd.Series):
            raise ValueError("All items in the list must be pandas DataFrame or Series objects.")

    valid_methods = {"pearson", "spearman", "kendall"}
    if method not in valid_methods:
        raise ValueError(f"Invalid correlation method: {method}. Valid methods are: {valid_methods}")

    if not all(datas[0].index.equals(item.index) for item in datas):
        raise ValueError("Value Error: All DataFrames/Series must have the same index for correlation calculation.")

    if len({len(data.columns) for data in datas if isinstance(data, pd.DataFrame)}) > 1:
        raise ValueError("All DataFrames/Series in the list must have the same number of columns.")

    if len(datas) == 1:
        logger.warning("Only one dataset provided. Correlation matrix will be a 1x1 DataFrame with correlation 1.0.")


def get_correlation(
    datas: list[pd.DataFrame | pd.Series],
    method: Literal["pearson", "kendall", "spearman"] = "pearson",
) -> pd.DataFrame:
    """
    Calculate the correlation between multiple datasets.

    Parameters:
    datas (List[pd.DataFrame | pd.Series]): A list of pandas DataFrames or Series containing the datasets.
    method (str, optional): The correlation method to use. Default is "pearson".
        Valid methods are:
        - "pearson": Standard correlation coefficient
        - "spearman": Spearman rank correlation
        - "kendall": Kendall Tau correlation coefficient

    Returns:
    pd.DataFrame: A DataFrame containing the correlation matrix.

    Raises:
    ValueError: If the input list is empty, contains invalid types, or an invalid correlation method is provided.
    """

    _validate_params(datas=datas, method=method)
    combined_data = pd.concat(datas, axis=1)
    return combined_data.corr(method=method)


if __name__ == "__main__":
    # Example usage:
    import numpy as np

    from constants.data_constants import DEMO_DATA

    CLOSE_DATA = DEMO_DATA["Close"].rename("Original")
    INV_DATA = (CLOSE_DATA * -1).rename("Inverse")
    RAND_DATA = pd.DataFrame(np.random.rand(len(DEMO_DATA)), index=DEMO_DATA.index).squeeze().rename("Random")

    print(CLOSE_DATA)
    print(INV_DATA)
    print(RAND_DATA)

    data = [CLOSE_DATA, RAND_DATA, INV_DATA]
    correlation_matrix = get_correlation(datas=data, method="spearman")
    print(correlation_matrix)
