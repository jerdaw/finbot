"""Efficient frontier helpers for long-only portfolio research."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class FrontierPortfolio:
    """A sampled portfolio on the efficient frontier surface."""

    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: dict[str, float]


@dataclass(frozen=True, slots=True)
class AssetFrontierStats:
    """Historical return and volatility summary for a frontier asset."""

    ticker: str
    annual_return: float
    annual_volatility: float


@dataclass(frozen=True, slots=True)
class EfficientFrontierResult:
    """Complete efficient frontier output for web and notebook consumers."""

    portfolios: tuple[FrontierPortfolio, ...]
    frontier: tuple[FrontierPortfolio, ...]
    max_sharpe: FrontierPortfolio
    min_volatility: FrontierPortfolio
    asset_stats: tuple[AssetFrontierStats, ...]
    correlation_matrix: dict[str, dict[str, float]]


def compute_efficient_frontier(
    price_histories: dict[str, pd.DataFrame],
    *,
    n_portfolios: int = 2500,
    risk_free_rate: float = 0.04,
    seed: int = 42,
) -> EfficientFrontierResult:
    """Sample long-only portfolios and extract an approximate efficient frontier."""

    if len(price_histories) < 2:
        raise ValueError("At least two assets are required for efficient frontier analysis")
    if n_portfolios < 10:
        raise ValueError("n_portfolios must be at least 10")

    closes = {ticker: _extract_close_series(df).rename(ticker) for ticker, df in price_histories.items()}
    returns_df = pd.concat(closes.values(), axis=1).pct_change().dropna()
    if len(returns_df) < 30:
        raise ValueError(f"Insufficient overlapping data: only {len(returns_df)} common return observations")

    tickers = [str(column) for column in returns_df.columns]
    returns_df.columns = tickers
    annual_returns = returns_df.mean() * 252.0
    annual_cov = returns_df.cov() * 252.0
    correlation = returns_df.corr().to_dict()
    annual_return_values = annual_returns.to_numpy(dtype=float)
    annual_cov_values = annual_cov.to_numpy(dtype=float)

    rng = np.random.default_rng(seed)
    weights = rng.dirichlet(np.ones(len(tickers)), size=n_portfolios)

    expected_returns = weights @ annual_return_values
    volatilities = np.sqrt(np.einsum("ij,jk,ik->i", weights, annual_cov_values, weights))
    sharpe_ratios = np.divide(
        expected_returns - risk_free_rate,
        volatilities,
        out=np.zeros_like(expected_returns),
        where=volatilities > 0,
    )

    portfolios = tuple(
        FrontierPortfolio(
            expected_return=float(expected_returns[index]),
            volatility=float(volatilities[index]),
            sharpe_ratio=float(sharpe_ratios[index]),
            weights={ticker: float(weights[index, asset_index]) for asset_index, ticker in enumerate(tickers)},
        )
        for index in range(n_portfolios)
    )

    frontier = _extract_frontier(portfolios)
    max_sharpe = max(portfolios, key=lambda portfolio: portfolio.sharpe_ratio)
    min_volatility = min(portfolios, key=lambda portfolio: portfolio.volatility)
    asset_stats = tuple(
        AssetFrontierStats(
            ticker=ticker,
            annual_return=float(annual_return_values[asset_index]),
            annual_volatility=float(annual_cov_values[asset_index, asset_index] ** 0.5),
        )
        for asset_index, ticker in enumerate(tickers)
    )

    return EfficientFrontierResult(
        portfolios=portfolios,
        frontier=frontier,
        max_sharpe=max_sharpe,
        min_volatility=min_volatility,
        asset_stats=asset_stats,
        correlation_matrix={
            str(row): {str(col): float(value) for col, value in values.items()} for row, values in correlation.items()
        },
    )


def _extract_close_series(df: pd.DataFrame) -> pd.Series:
    if "Adj Close" in df.columns:
        return df["Adj Close"].astype(float)
    if "Close" in df.columns:
        return df["Close"].astype(float)
    raise ValueError("Price history must contain 'Close' or 'Adj Close'")


def _extract_frontier(portfolios: tuple[FrontierPortfolio, ...]) -> tuple[FrontierPortfolio, ...]:
    ordered = sorted(portfolios, key=lambda portfolio: (portfolio.volatility, -portfolio.expected_return))
    frontier: list[FrontierPortfolio] = []
    best_return_so_far = float("-inf")

    for portfolio in ordered:
        if portfolio.expected_return > best_return_so_far:
            frontier.append(portfolio)
            best_return_so_far = portfolio.expected_return

    return tuple(frontier)
