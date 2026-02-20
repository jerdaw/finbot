"""Compound Growth Rate (CGR) calculation.

Calculates the compound annual growth rate (CAGR) or compound growth rate for any period.
Also known as geometric mean return or annualized return.

Typical usage:
    - Calculate investment returns over time
    - Compare performance across different time periods
    - Annualize returns from any frequency
"""


def get_cgr(start_val: float, end_val: float, periods: int | float) -> float:
    return (end_val / start_val) ** (1 / periods) - 1


if __name__ == "__main__":
    print(get_cgr(100, 110, 1))
