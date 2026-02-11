"""Investment event horizon calculation.

Determines when portfolio growth dominates new contributions. The "event horizon"
is the point where adding yearly contributions becomes insignificant compared to
compound growth on existing portfolio value.

This helps answer the question: "When does my money start working harder than I do?"

Typical usage:
    - Retirement planning and savings goal setting
    - Understanding the power of compound growth over time
    - Determining optimal contribution periods
    - Comparing different savings strategies

The calculation accounts for:
    - Initial portfolio value
    - Yearly contributions
    - Expected compound annual growth rate (CAGR)
    - Threshold for "significance" (default: inflation rate)
"""

import numpy as np
import pandas as pd


def calculate_event_horizon(
    cagr: float = 0.069,  # Average inflation adjusted us stock market return
    yearly_contribution: float = 5000,  # Average us investment per year
    initial_value: float = 15000,  # Some small-ish starting amount
    event_horizon_threshold: float = 0.035,  # Rough historical average inflation
    max_years: float | int = float("inf"),
) -> int | float:
    """
    Calculate the earliest year when the portfolio value reaches a certain threshold.
    The investment event horizon is the earliest year in which adding the yearly_contribution will no longer increase the portfolio value by more than the event_horizon_threshold.
    This assumes a constant yearly contribution and a constant compound annual growth rate.

    :param compound_annual_growth_rate: The yearly compounded growth rate.
    :param yearly_contribution: Annual contribution to the portfolio.
    :param initial_value: The initial value of the portfolio. Defaults to 100000.
    :param event_horizon_threshold: The threshold percentage to determine the event horizon. Defaults to 0.05.
    :param years_remaining: The total number of years considered for growth. Defaults to 35.
    :return: The earliest year when the portfolio is within the event horizon threshold.
    """
    if cagr < 0 or cagr > 1:
        raise ValueError("compound_annual_growth_rate must be between 0 and 1")
    if yearly_contribution < 0:
        raise ValueError("yearly_contribution must be non-negative")
    if initial_value < 0:
        raise ValueError("initial_value must be non-negative")
    if not (0 <= event_horizon_threshold <= 1):
        raise ValueError("event_horizon_threshold must be between 0 and 1")
    if max_years <= 0:
        raise ValueError("years_remaining must be a positive integer")

    initial_value = float(initial_value)
    yearly_contribution = float(yearly_contribution)
    cagr = float(cagr)

    if yearly_contribution == 0 and initial_value == 0:
        return np.NaN

    portfolio_value = initial_value
    year = 1
    while year <= max_years:
        new_value = portfolio_value * (1 + cagr) + yearly_contribution
        if (new_value - yearly_contribution != 0) and (
            new_value / (new_value - yearly_contribution) <= 1 + event_horizon_threshold
        ):
            return year
        portfolio_value = new_value
        year += 1

    return int(max_years)


def generate_horizon_grid(cagr: None | np.ndarray = None, contrib: None | range = None):
    # Testing the function with different CAGRs and contributions
    if cagr is None:
        cagr = np.linspace(0.0, 0.25, 26).round(2)
    if contrib is None:
        contrib = range(0, 155000, 5000)

    df = pd.DataFrame(
        [[calculate_event_horizon(cagr, contrib) for cagr in cagr] for contrib in contrib],
    )
    df.index = pd.Index(contrib)
    df.index.name = "Yearly Contributions"
    df.columns = pd.Index(cagr)
    df.columns.name = "Yearly CAGR"

    # confirm that all columns increase in value going down
    if any(df[col].diff().dropna().any() < 0 for col in df.columns):
        raise ValueError("Columns do not increase in value going down")

    # confirm that all rows decrease in value going right
    # if any(df.loc[row].diff().dropna().any() > 0 for row in df.index):
    #     raise ValueError("Rows do not decrease in value going right")

    return df.astype(int)


def plot_horizon_grid(df: pd.DataFrame | None = None):
    if df is None:
        df = generate_horizon_grid()

    import matplotlib.pyplot as plt
    import seaborn as sns

    _fig, ax = plt.subplots(figsize=(10, 10))
    ax = sns.heatmap(df, annot=True, fmt="d", cmap="viridis", linewidths=0.5, ax=ax)
    ax.set_title("Investment Event Horizon")
    ax.set_xlabel("Yearly Compound Annual Growth Rate")
    ax.set_ylabel("Yearly Contribution")
    plt.show()


if __name__ == "__main__":
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    print(generate_horizon_grid())
    plot_horizon_grid()
