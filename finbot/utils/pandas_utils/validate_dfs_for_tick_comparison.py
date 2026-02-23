"""Validate DataFrames for tick-by-tick comparison.

Ensures multiple DataFrames are aligned for tick-by-tick comparison by
checking length consistency and index alignment. Essential for comparing
time series data point-by-point.

Configurable strictness:
    - all_lens_match: Require same number of rows
    - identical_indexes: Require exact index matching

Raises ValueErrors or warnings depending on configuration.

Typical usage:
    - Validate data before correlation analysis
    - Ensure price series alignment before comparison
    - Check data consistency before merging
    - Verify synchronized time series data
"""

import warnings

import pandas as pd


def validate_dfs_for_tick_comparison(
    *dfs: pd.DataFrame,
    all_lens_match: bool = True,
    identical_indexes: bool = True,
) -> bool:
    """
    Validates the given DataFrames for tick comparison.

    Args:
        *dfs: Variable number of DataFrames to be validated.
        all_lens_match (bool): Flag indicating whether the lengths of all DataFrames should match.
            If True and the lengths do not match, a ValueError is raised. If False, a warning is issued.
            Default is True.
        identical_indexes (bool): Flag indicating whether the indexes of all DataFrames should be identical.
            If True and the indexes are not identical, a ValueError is raised. If False, a warning is issued.
            Default is True.

    Raises:
        ValueError: If the DataFrames do not meet the validation criteria.

    Returns:
        bool: True if the DataFrames pass the validation, False otherwise.
    """
    raise NotImplementedError("This function is not yet verified.")

    # Check that the DFs have the same end timestamp
    if not all(df.index[-1] == dfs[0].index[-1] for df in dfs):  # type: ignore[unreachable]
        raise ValueError("DataFrames do not have a matching end date")

    # Check that the latest starting date in the DFs is present in all DFs
    latest_starting_date = max(df.index[0] for df in dfs)
    for df in dfs:
        if latest_starting_date not in df.index:
            raise ValueError("The latest starting date of the DFs is not present in all DataFrames")

    # Check that the comparable
    num_period_since_latest_starting_date = len(dfs[0].loc[latest_starting_date:])
    for df in dfs:
        if len(df.loc[latest_starting_date:]) != num_period_since_latest_starting_date:
            raise ValueError(
                "DataFrames do not have the same number of entries/length in their comparable range ("
                "i.e., after the latest starting date amongst the DataFrames)",
            )

    # Check the length of all DFs is the same
    if not identical_indexes and len({len(df) for df in dfs}) != 1:
        msg = "Lengths of DataFrames do not all match"
        if all_lens_match:
            raise ValueError(msg)
        warnings.warn(msg, stacklevel=2)

    # Check the dfs have identical indexes
    if len({tuple(df.index) for df in dfs}) != 1:
        msg = "DataFrames do not have identical indexes."
        if identical_indexes:
            raise ValueError(msg)
        warnings.warn(msg, stacklevel=2)

    return True


# if __name__ == "__main__":
#     from finbot.data_generation.simulators.fund_simulators.sim_specific_funds import sim_spy
#     from finbot.data_generation.simulators.index_simulators.sim_specific_stock_index import sim_sp500tr

#     from finbot.utils.data_collection_utils.yfinance.get_history import get_history

#     comps = (get_history("SPY"), get_history("VOO"), sim_spy(), sim_sp500tr())

#     print(validate_dfs_for_tick_comparison(*comps, all_lens_match=False, identical_indexes=False))
#     print(validate_dfs_for_tick_comparison(*comps))
