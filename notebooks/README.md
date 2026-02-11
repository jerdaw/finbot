# Finbot Example Notebooks

This directory contains Jupyter notebooks demonstrating the key capabilities of the Finbot platform through practical examples and real-world analysis.

## Notebooks

### 1. Fund Simulation Demo
**File:** `01_fund_simulation_demo.ipynb`

Demonstrates the fund simulator by comparing simulated leveraged ETF performance against actual historical data. Shows how the simulator models:
- Leverage multipliers and expense ratios
- Borrowing costs (LIBOR approximation)
- Spread costs and fund-specific adjustments

**Funds Analyzed:** SPY (1x), SSO (2x), UPRO (3x), TQQQ (3x Nasdaq-100)

**Key Features:**
- Tracking accuracy calculations
- Normalized performance visualization
- Error metrics and validation

---

### 2. DCA Optimization Results
**File:** `02_dca_optimization_results.ipynb`

Runs the DCA (Dollar Cost Averaging) optimizer to find optimal allocation ratios across different assets. Performs grid search across:
- Asset allocation ratios (50/50 to 90/10)
- Investment durations (5-20 years)
- Purchase intervals (monthly, quarterly)

**Portfolios Analyzed:** SPY/TLT (60/40), UPRO/TMF (leveraged), SPY/TQQQ (growth)

**Key Features:**
- CAGR, Sharpe ratio, max drawdown, standard deviation calculations
- Optimization surface visualization
- Sensitivity analysis across time horizons
- Multi-portfolio comparison

---

### 3. Backtest Strategy Comparison
**File:** `03_backtest_strategy_comparison.ipynb`

Compares all 10 implemented backtesting strategies on the same historical dataset with comprehensive performance metrics.

**Strategies Tested:**
1. Rebalance (periodic portfolio rebalancing)
2. NoRebalance (buy and hold)
3. SMACrossover (single SMA timing)
4. SMACrossoverDouble (dual SMA)
5. SMACrossoverTriple (triple SMA)
6. MACDSingle (MACD-based entry/exit)
7. MACDDual (dual MACD indicators)
8. DipBuySMA (buy dips relative to SMA)
9. DipBuyStdev (buy dips using standard deviation)
10. SMARebalMix (mixed SMA timing + rebalancing)

**Key Features:**
- Performance metrics (Total Return, Sharpe, Sortino, Calmar, Max Drawdown, Win Rate)
- Risk-return scatter plots
- Strategy ranking by different metrics
- Visual comparison charts

---

### 4. Monte Carlo Risk Analysis
**File:** `04_monte_carlo_risk_analysis.ipynb`

Demonstrates Monte Carlo simulation for portfolio risk analysis and retirement planning using 10,000 simulated scenarios.

**Analysis Performed:**
- 30-year portfolio projections
- Value at Risk (VaR) calculations
- Probability distributions of outcomes
- Retirement withdrawal sustainability testing (4% rule, etc.)

**Key Features:**
- Fan chart visualization showing range of outcomes
- Percentile analysis (5th, 10th, 25th, 50th, 75th, 90th, 95th)
- Withdrawal rate success probability curves
- Sequence of returns risk analysis

---

### 5. Bond Ladder Analysis
**File:** `05_bond_ladder_analysis.ipynb`

Demonstrates bond ladder construction and analysis across different interest rate environments.

**Analysis Performed:**
- 10-year Treasury bond ladder construction
- Historical yield curve evolution
- Present value calculations
- Comparison with bond ETFs (TLT, IEF, SHY)

**Key Features:**
- Yield curve shape classification (steep, normal, flat, inverted)
- 10Y-1Y spread analysis over time
- Performance comparison: ladders vs ETFs
- Cost and tax efficiency considerations

---

## Running the Notebooks

### Prerequisites

1. Install dependencies:
```bash
uv sync
```

2. Set environment variables:
```bash
export DYNACONF_ENV=development
```

3. (Optional) For data collection features, set API keys:
```bash
export ALPHA_VANTAGE_API_KEY=your_key
export NASDAQ_DATA_LINK_API_KEY=your_key
export US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
```

### Launch Jupyter

```bash
uv run jupyter notebook notebooks/
```

Or use JupyterLab:
```bash
uv run jupyter lab notebooks/
```

### Running Cells

Most notebooks require historical data. If you haven't run the daily update pipeline yet:

```bash
uv run python scripts/update_daily.py
```

This will:
- Fetch historical price data
- Run fund simulations
- Build yield curves
- Cache all data in `finbot/data/` subdirectories

## Data Requirements

Each notebook uses different data sources:

| Notebook | Data Required | Source |
|----------|--------------|--------|
| Fund Simulation | Price histories (YF), Simulated funds | `scripts/update_daily.py` |
| DCA Optimization | Price histories (YF) | Yahoo Finance API |
| Backtest Comparison | Price histories (YF) | Yahoo Finance API |
| Monte Carlo | Price histories (YF) | Yahoo Finance API |
| Bond Ladder | FRED yield curve data | FRED API (Federal Reserve) |

## Notes

- All notebooks include markdown cells with methodology explanations and key findings
- Visualizations use Plotly for interactive charts
- Code cells are well-commented for educational purposes
- Each notebook can be run independently
- Results may vary based on the date range of available data

## Contributing

When adding new notebooks:
1. Follow the naming convention: `NN_descriptive_name.ipynb`
2. Include markdown sections: Overview, Analysis, Key Findings, Next Steps
3. Add entry to this README with one-line description
4. Ensure reproducibility (set random seeds, document data requirements)
5. Test notebook runs end-to-end before committing
