import numpy as np
import pandas as pd
from tqdm import tqdm

from finbot.services.simulation.monte_carlo.sim_types import sim_type_nd

_DEFAULT_EQUITY_START = pd.Timestamp(1900, 1, 1)


def monte_carlo_simulator(
    equity_data: pd.DataFrame,
    equity_start: pd.Timestamp = _DEFAULT_EQUITY_START,
    equity_end: pd.Timestamp | None = None,
    sim_periods: int = 252,
    n_sims: int = 10000,
    start_price: float | None = None,
) -> pd.DataFrame:
    if equity_end is None:
        equity_end = pd.Timestamp.now()
    equity_data = equity_data.truncate(before=equity_start, after=equity_end)

    closes = equity_data["Adj Close" if "Adj Close" in equity_data.columns else "Close"]
    changes = closes.pct_change()
    start_price = (
        closes.iloc[-(sim_periods if len(closes) >= sim_periods else 1)] if start_price is None else start_price
    )
    mu = changes.dropna().mean()
    sigma = changes.dropna().std()

    trials = np.array(
        [
            sim_type_nd(
                sim_periods=sim_periods,
                n_sims=n_sims,
                start_price=start_price,
                mu=mu,
                sigma=sigma,
                cov_matrix=None,
            )
            for _ in tqdm(range(n_sims), desc="Performing monte carlo simulation")
        ]
    )

    trials_df = pd.DataFrame(trials)
    trials_df.index.name = "Trials"
    trials_df.columns.name = "Periods"

    return trials_df
