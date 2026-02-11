# Research Documentation

This section contains research findings and analysis from Finbot simulations and backtests.

## Published Research

### Leveraged ETF Simulation Accuracy

Analysis of how well the fund simulator tracks real ETF returns.

**Key Findings:**
- 2-5% tracking error for leveraged funds
- Suitable for historical backtesting and extension
- LIBOR approximation accounts for ~1% of error

[Read Full Report](leveraged-etf-simulation.md)

### DCA Optimization Findings

Optimal dollar-cost averaging strategies across multiple portfolios.

**Key Findings:**
- 60/40 SPY/TLT validated for non-leveraged portfolios
- 45/55 UPRO/TMF optimal for leveraged portfolios
- 5-year DCA duration balances risk and return

[Read Full Report](dca-optimization.md)

### Strategy Backtest Results

Comparison of 10 trading strategies on S&P 500 data.

**Key Findings:**
- Rebalancing outperforms buy-and-hold for multi-asset portfolios
- SMA crossovers effective in trending markets
- Transaction costs matter for frequent-trading strategies

[Read Full Report](strategy-backtesting.md)

## Research Notebooks

Interactive Jupyter notebooks with full analysis:

1. [Fund Simulation Demo](../../notebooks/01_fund_simulation_demo.ipynb)
2. [DCA Optimization Results](../../notebooks/02_dca_optimization_results.ipynb)
3. [Backtest Strategy Comparison](../../notebooks/03_backtest_strategy_comparison.ipynb)
4. [Monte Carlo Risk Analysis](../../notebooks/04_monte_carlo_risk_analysis.ipynb)
5. [Bond Ladder Analysis](../../notebooks/05_bond_ladder_analysis.ipynb)

## Methodology

All research uses:
- Historical data from Yahoo Finance and FRED
- Simulated data from Finbot's fund simulator
- Backtrader-based backtesting engine
- Quantstats for performance metrics

## Limitations

- Historical data (past performance ≠ future results)
- Simulation assumptions (constant expense ratios, LIBOR approximation)
- No transaction costs in some analyses
- Survivorship bias (analyzing successful ETFs)

## Citation

If you use Finbot's research in academic work:

```bibtex
@software{finbot2026,
  author = {Dawson, Jeremy},
  title = {Finbot: Financial Simulation and Backtesting Platform},
  year = {2026},
  url = {https://github.com/jerdaw/finbot}
}
```
