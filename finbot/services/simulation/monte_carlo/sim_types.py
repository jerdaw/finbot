from typing import Any

import numpy as np


def sim_type_nd(**kwargs: Any) -> np.ndarray:
    """Normal distribution Monte Carlo simulation."""
    sim_periods = kwargs["sim_periods"]
    start_price = kwargs["start_price"]
    mu = kwargs["mu"]
    sigma = kwargs["sigma"]

    daily_changes = np.random.normal(loc=mu + 1, scale=sigma, size=sim_periods)
    daily_changes[0] = 1
    cum_changes = np.cumprod(daily_changes)
    price_array = cum_changes * start_price
    return price_array
