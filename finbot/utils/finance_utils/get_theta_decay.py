"""Theta decay calculation for leveraged positions.

Theta decay (also called volatility drag or leverage decay) refers to the erosion
of value in leveraged positions due to daily rebalancing and compounding effects.
This is particularly relevant for leveraged ETFs.

Note: This function is not yet fully verified and raises NotImplementedError.

Typical usage (when implemented):
    - Quantify cost of holding leveraged ETFs
    - Compare leveraged vs unleveraged strategies
    - Model expected decay under different volatility regimes
"""

import pandas as pd


def calculate_theta_decay(unlevered_series: pd.Series) -> pd.Series:
    """
    Calculate theta decay based on a series of unlevered values. Theta decay
    refers to the rate at which the value of an option or a portfolio with options
    decreases over time, assuming that all other variables remain constant.
    This function computes the relative difference in leveraged versus unlevered
    values' reaction to changes in the underlying asset's price.

    Parameters:
    unlevered_series (pd.Series): Series of unlevered values representing the
                                  underlying asset's price over time.

    Returns:
    pd.Series: Series representing the theta decay for each time point. The first
               value is set to None as it's undefined due to lack of prior data.
    """
    raise NotImplementedError("This function is not yet been verified.")  # TODO

    if not isinstance(unlevered_series, pd.Series):
        raise TypeError("Input must be a pandas Series.")

    changes = unlevered_series.pct_change()
    revert_1x = 1 / (1 + changes) - 1
    underlying_reverted = (1 + changes) * (1 + revert_1x)
    lvg_reverted = (1 + changes * 3) * (1 + revert_1x * 3)
    decay = (lvg_reverted - underlying_reverted) / underlying_reverted
    decay.iloc[0] = None  # Set first element to None as it's undefined
    return decay


if __name__ == "__main__":
    from constants.data_constants import DEMO_DATA

    print(calculate_theta_decay(DEMO_DATA["Close"]))
