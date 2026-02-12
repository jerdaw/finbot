"""Multi-asset Monte Carlo simulator with correlation matrices.

Generates correlated price paths for multiple assets using a multivariate
normal distribution derived from historical return statistics.  Useful for
portfolio-level risk analysis where asset co-movements matter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from tqdm import tqdm


def multi_asset_monte_carlo(
    price_data: dict[str, pd.DataFrame],
    sim_periods: int = 252,
    n_sims: int = 1000,
    weights: dict[str, float] | None = None,
    start_value: float = 10000.0,
) -> dict[str, pd.DataFrame | pd.Series | dict[str, pd.DataFrame]]:
    """Run correlated Monte Carlo simulation across multiple assets.

    Parameters
    ----------
    price_data : dict[str, pd.DataFrame]
        Mapping of asset name to DataFrame with "Close" or "Adj Close" column.
    sim_periods : int
        Number of forward periods to simulate (default 252 = ~1 year).
    n_sims : int
        Number of simulation trials (default 1000).
    weights : dict[str, float] | None
        Portfolio weights per asset.  If None, equal-weight is used.
        Values are normalized to sum to 1.
    start_value : float
        Starting portfolio value (default 10000).

    Returns
    -------
    dict with keys:
        "portfolio_trials" : pd.DataFrame  — shape (n_sims, sim_periods), portfolio value paths
        "asset_trials"     : dict[str, pd.DataFrame] — per-asset trial DataFrames
        "correlation"      : pd.DataFrame  — historical correlation matrix
        "weights"          : pd.Series     — normalized portfolio weights
    """
    assets = list(price_data.keys())
    n_assets = len(assets)

    if n_assets < 2:
        raise ValueError("multi_asset_monte_carlo requires at least 2 assets")

    # Extract close prices and compute daily returns
    returns_dict: dict[str, pd.Series] = {}
    for name, df in price_data.items():
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        returns_dict[name] = df[col].pct_change().dropna()

    # Align on common dates
    returns_df = pd.DataFrame(returns_dict).dropna()
    if len(returns_df) < 30:
        raise ValueError(f"Insufficient overlapping data: only {len(returns_df)} common dates")

    # Compute statistics
    mu = returns_df.mean().to_numpy()
    cov = returns_df.cov().to_numpy()
    corr_matrix = returns_df.corr()

    # Normalize weights
    if weights is None:
        w = np.ones(n_assets) / n_assets
    else:
        w_arr = np.array([weights.get(a, 0.0) for a in assets])
        w = w_arr / w_arr.sum()

    weight_series = pd.Series(w, index=assets)

    # Get start prices for each asset
    start_prices = {}
    for name, df in price_data.items():
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        start_prices[name] = float(df[col].iloc[-1])

    # Run simulations using multivariate normal
    asset_trials: dict[str, np.ndarray] = {a: np.zeros((n_sims, sim_periods)) for a in assets}
    portfolio_trials = np.zeros((n_sims, sim_periods))

    for trial in tqdm(range(n_sims), desc="Multi-asset Monte Carlo"):
        # Draw correlated returns: shape (sim_periods, n_assets)
        sim_returns = np.random.default_rng().multivariate_normal(mu, cov, size=sim_periods)

        for j, name in enumerate(assets):
            # Build price path
            daily_factors = 1 + sim_returns[:, j]
            daily_factors[0] = 1  # Start at current price
            prices = start_prices[name] * np.cumprod(daily_factors)
            asset_trials[name][trial] = prices

        # Portfolio value = weighted sum of each asset's growth
        for j, name in enumerate(assets):
            growth = asset_trials[name][trial] / start_prices[name]
            portfolio_trials[trial] += w[j] * start_value * growth

    # Convert to DataFrames
    portfolio_df = pd.DataFrame(portfolio_trials)
    portfolio_df.index.name = "Trials"
    portfolio_df.columns.name = "Periods"

    asset_dfs = {}
    for name in assets:
        adf = pd.DataFrame(asset_trials[name])
        adf.index.name = "Trials"
        adf.columns.name = "Periods"
        asset_dfs[name] = adf

    return {
        "portfolio_trials": portfolio_df,
        "asset_trials": asset_dfs,
        "correlation": corr_matrix,
        "weights": weight_series,
    }
