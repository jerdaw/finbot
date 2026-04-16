# Research Documentation

This section collects the public research and methodology notes that support
Finbot's quantitative-analysis workflows across finance and health economics.

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

Foundational comparison of the project's original 10-strategy cohort on S&P 500 data. The live platform now includes additional strategies beyond this initial report.

**Key Findings:**
- Rebalancing outperforms buy-and-hold for multi-asset portfolios
- SMA crossovers effective in trending markets
- Transaction costs matter for frequent-trading strategies

[Read Full Report](strategy-backtesting.md)

### Health Economics Evidence

Scope, intended use, and current validation posture for Finbot's public health-
economics tooling.

**Key Takeaways:**
- Open and inspectable implementation of standard health-economics workflows
- Educational and research framing, not clinical decision support
- Clear public path from tutorial to methodology to notebook

[Read Evidence Overview](health-economics-evidence.md)

### Health Economics Methodology

Summary of the model structure, equations, standards alignment, and known
limitations behind the health-economics module.

**Key Takeaways:**
- Monte Carlo QALY simulation with discounted costs and outcomes
- ICER, NMB, CEAC, and optimizer workflows are documented publicly
- Public methodology page now matches the published tutorial path

[Read Methodology Summary](health-economics-methodology.md)

## Research Notebooks

Interactive Jupyter notebooks are maintained in the repository:

1. [Fund Simulation Demo](https://github.com/jerdaw/finbot/blob/main/notebooks/01_fund_simulation_demo.ipynb)
2. [DCA Optimization Results](https://github.com/jerdaw/finbot/blob/main/notebooks/02_dca_optimization_results.ipynb)
3. [Backtest Strategy Comparison](https://github.com/jerdaw/finbot/blob/main/notebooks/03_backtest_strategy_comparison.ipynb)
4. [Monte Carlo Risk Analysis](https://github.com/jerdaw/finbot/blob/main/notebooks/04_monte_carlo_risk_analysis.ipynb)
5. [Bond Ladder Analysis](https://github.com/jerdaw/finbot/blob/main/notebooks/05_bond_ladder_analysis.ipynb)
6. [Health Economics Demo](https://github.com/jerdaw/finbot/blob/main/notebooks/06_health_economics_demo.ipynb)

Supporting notebooks for cost models and corporate actions are also available
in the repository.

## Methodology

Research methods vary by domain, but the public materials generally use:

- historical market data from public sources,
- Finbot's simulation and backtesting services,
- probabilistic scenario analysis,
- and explicit limitations documentation.

## Limitations

- Historical data and scenario models are not future guarantees.
- Financial simulations rely on simplifying assumptions.
- Health-economics scenarios are educational and research-oriented, not
  patient-specific clinical guidance.
- Readers should review the evidence and methodology pages before treating any
  output as decision-grade analysis.

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
