"""Inflation adjustment using CPI data from FRED.

Converts nominal dollar amounts to real (inflation-adjusted) values using the
Consumer Price Index for All Urban Consumers (CPIAUCSL) from FRED.

Essential for comparing dollar amounts across different time periods and
calculating real returns on investments.

Typical usage:
    - Adjust historical prices to current dollars
    - Calculate real returns (nominal returns - inflation)
    - Compare purchasing power across decades
"""

import datetime

import pandas as pd

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data


def get_inflation_adjusted_value(
    initial_value: float,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    cpi_data: pd.DataFrame | None = None,
) -> float:
    """
    Calculate the inflation-adjusted value of an amount of money using specific dates and retaining monthly CPI data.

    Args:
        initial_value (float): The initial amount of money.
        start_date (datetime.date): The start date for the inflation adjustment.
        end_date (datetime.date): The end date for the inflation adjustment.
        cpi_data (pd.DataFrame): DataFrame containing monthly CPI data.

    Returns:
        float: The inflation-adjusted value.
    """
    FRED_DATA_START_DATE = datetime.date(1947, 1, 1)  # noqa: N806 - Constant scoped to function

    if start_date is None:
        start_date = FRED_DATA_START_DATE

    if cpi_data is None:
        result = get_fred_data(symbols=["CPIAUCSL"], start_date=FRED_DATA_START_DATE)
        assert isinstance(result, pd.DataFrame)
        cpi_data = result

    min_date = cpi_data.index.min().date()
    max_date = cpi_data.index.max().date()

    if end_date is None:
        end_date = max_date

    # Ensure the CPI data dates is a superset of the data start and end years
    if min_date > start_date:
        raise ValueError(f"Start date {start_date} is before the first date in the CPI data {min_date}.")
    if max_date < end_date:
        raise ValueError(f"End date {end_date} is after the last date in the CPI data {max_date}.")

    # Find closest CPI values for the start and end dates
    start_cpi = cpi_data.loc[cpi_data.index <= pd.Timestamp(start_date)].iloc[-1]
    end_cpi = cpi_data.loc[cpi_data.index >= pd.Timestamp(end_date)].iloc[0]

    # Extracting scalar CPI values
    start_cpi_value = start_cpi["CPIAUCSL"].item()
    end_cpi_value = end_cpi["CPIAUCSL"].item()

    # Calculate inflation-adjusted value
    adjusted_value = initial_value * (end_cpi_value / start_cpi_value)

    return adjusted_value


# Example usage
latest_date = get_fred_data(symbols=["CPIAUCSL"]).index.max().date()
adjusted_value = get_inflation_adjusted_value(1, datetime.date(1947, 1, 1), latest_date)
print(f"The inflation-adjusted value is: {adjusted_value}")
