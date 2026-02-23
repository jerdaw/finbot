# Testfol.io vs Portfolio Visualizer — Feature Analysis for Finbot

**Date:** 2026-02-18
**Purpose:** Competitive research to identify features from testfol.io and Portfolio Visualizer worth implementing in Finbot

---

## 1. Testfol.io — Complete Feature Inventory

### Core: Portfolio Backtester
- **Multi-portfolio comparison**: Up to 5 portfolios side-by-side
- **Allocation**: Tickers with +/- percentage allocations (integers), supports leveraged portfolios
- **Rebalancing**: Multiple frequency options including bi-monthly, 4-month with offset
- **Cashflows**: Multiple cashflow legs with individual start/end dates, percentage-of-portfolio withdrawals, inflation adjustment
- **Assets**: ETFs, mutual funds, CEFs, stocks, TIAA/CREF annuities, cash alternatives (CASHX, TBILL, EFFRX), FRED fixed-income series
- **Data**: Daily returns from Tiingo (vs PV's monthly Morningstar data)
- **Management fees**: Adjustable per-instrument (unique differentiator)

### Results & Metrics
- CAGR, TWRR, MWRR (XIRR), max drawdown, volatility, Sharpe, Sortino, Ulcer Index, UPI
- Rolling metrics (CAGR, volatility, Sharpe, Excess Return, Ulcer Index)
- Growth charts, drawdown visualizations, recovery metrics
- Monthly/annual returns tables (returns ignore cashflows, balances include them)
- Daily Returns tab, Telltale ratio charts
- DCA vs lump-sum comparison

### Asset Analyzer
- Up to 5 tickers: CAGR, volatility, Sharpe, Sortino, Ulcer Index, growth charts, correlations

### Withdrawal Analysis (SWR/PWR)
- Safe Withdrawal Rate (SWR) with survival rates and terminal multiples
- Perpetual Withdrawal Rate (PWR) preservation analysis
- Fixed periods: 5, 10, 15, 20, 25, 30, 35, 40 years
- Rolling-window customization

### Tactical Allocation
- Current Status tab showing current allocation and signal statuses
- Signals tab showing signal values over time

### Preset Portfolios
- 7 preset portfolios including 4 risk parity portfolios (Golden Butterfly, All-Weather, etc.)
- Clone function to copy and modify portfolios

### Sharing & Accounts
- Shareable URLs, TinyURL integration
- Free accounts with cloud-based portfolio saving
- Local browser storage (no login required for basic use)

---

## 2. Portfolio Visualizer — Complete Tool Inventory

### BACKTESTING (4 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Backtest Portfolio** | `/backtest-portfolio` | Construct portfolios of ETFs/funds/stocks, compare up to 3 vs benchmark, with periodic contributions/withdrawals and rebalancing (monthly/quarterly/semi-annual/annual + band-based) |
| **Backtest Asset Class Allocation** | `/backtest-asset-class-allocation` | Same but using broad asset class proxies instead of specific tickers |
| **Backtest Dynamic Allocation** | `/backtest-dynamic-allocation` | Backtest portfolios where asset weights changed over time (glidepaths) |
| **Tactical Allocation Models** | `/tactical-asset-allocation-model` | Test models: Moving Average, Dual Momentum, Adaptive Allocation, Volatility Targeting |

**Backtest Outputs**: Returns (CAGR, IRR), risk (Std Dev, Sharpe, Sortino), max drawdown, rolling returns, style analysis, annual returns table

### OPTIMIZATION (5 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Portfolio Optimization** | `/optimize-portfolio` | Mean-Variance, CVaR, Risk Parity, Kelly Criterion, Sortino, Omega, Tracking Error, Information Ratio, Min Drawdown |
| **Efficient Frontier** | `/efficient-frontier` | Historical efficient frontier with constraints |
| **Efficient Frontier Forecast** | `/efficient-frontier-forecast` | Forward-looking frontier with user-specified expected returns + historical correlations, Monte Carlo resampling |
| **Black-Litterman Model** | `/black-litterman-model` | Optimize based on investor views (absolute/relative) + market equilibrium |
| **Rolling Optimization** | `/rolling-optimization` | Time-varying optimal allocations with lookback windows |

### MONTE CARLO & PLANNING (3 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Monte Carlo Simulation** | `/monte-carlo-simulation` | 4 return models: Historical, Forecasted, Statistical, Parameterized. Withdrawal models. Bootstrap: single month or single year. |
| **Financial Goals** | `/financial-goals` | Goal-based planning with probability of success |
| **Asset Liability Modeling** | `/asset-liability-modeling` | Match assets to future liabilities (pensions, endowments) |

### FACTOR ANALYSIS (8 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Factor Regression** | `/factor-analysis` | CAPM, FF3, Carhart 4, FF5, q-factor. Plus: reversal, quality (QMJ), BAB factors |
| **Risk Factor Allocation** | `/risk-factor-allocation` | Optimize portfolio based on targeted factor exposures |
| **Match Factor Exposure** | `/match-factor-exposure` | Find asset combo that clones factor exposures of a target |
| **Principal Component Analysis** | `/principal-component-analysis` | Identify independent sources of risk driving portfolio variance |
| **Factor Statistics** | `/factor-statistics` | Factor correlations and risk premia over different periods |
| **Fund Factor Regressions** | `/etf-and-mutual-fund-factor-regressions` | Batch factor regressions for funds |
| **Fund Performance Attribution** | `/factor-performance-attribution` | Returns attribution via factor models |
| **Manager Performance** | (implied from search data) | Alpha analysis vs factor benchmarks |

### FUND ANALYSIS (3 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Fund Screener** | `/fund-screener` | Filter ETFs/funds by asset class, performance, risk metrics |
| **Fund Rankings** | `/fund-rankings` | Rank funds within category by specified criteria |
| **Fund Performance** | `/fund-performance` | Individual fund analysis vs benchmark |

### CORRELATION & STATISTICAL (4 tools)
| Tool | URL Path | Description |
|------|----------|-------------|
| **Asset Correlations** | `/asset-correlations` | Cross-asset correlations with rolling correlation charts |
| **Asset Class Correlations** | `/asset-class-correlations` | Broad asset class correlation matrix |
| **Asset Autocorrelation** | `/asset-autocorrelation` | Serial correlation analysis with configurable time lag |
| **Asset Cointegration** | `/asset-cointegration` | Augmented Dickey-Fuller cointegration testing |

---

## 3. Gap Analysis: What Finbot Has vs What to Add

### Already in Finbot
| Feature | Finbot Status | Notes |
|---------|--------------|-------|
| Portfolio backtesting | **12 strategies** | More strategies than PV; Finbot uses Backtrader engine |
| Monte Carlo simulation | **Single + multi-asset** | Has fan charts, percentile analysis |
| DCA optimization | **Grid search** | Unique to Finbot |
| Walk-forward analysis | **Rolling/anchored** | More sophisticated than PV |
| Regime detection | **Bull/Bear/Sideways/Vol** | Unique — neither platform has this |
| Risk parity strategy | **Yes** | Inverse-volatility weighting |
| Dual momentum strategy | **Yes** | Absolute + relative momentum |
| Experiment comparison | **Yes** | A/B testing backtest runs |
| Health economics | **Yes** | Completely unique to Finbot |

### High-Value Features to Add (Tier 1 — Frontend for existing backend)

| # | Feature | Source | Backend? | Effort |
|---|---------|--------|----------|--------|
| 1 | **Multi-asset portfolio builder** | Both | Partial (rebalance strategy exists) | Medium — need allocation % UI, add/remove assets |
| 2 | **Preset portfolio library** | Testfol.io | No — JSON config | Low — hardcoded portfolio presets (60/40, All-Weather, Golden Butterfly) |
| 3 | **SWR/PWR withdrawal analysis** | Testfol.io | No | Medium — requires Monte Carlo with withdrawal logic |
| 4 | **Bond Ladder Simulator page** | Finbot backend | Yes (`bond_ladder/`) | Low — new API endpoint + frontend |
| 5 | **Pareto Optimizer page** | Finbot backend | Yes (`pareto_optimizer.py`) | Low — new API endpoint + frontend |
| 6 | **Multi-Asset MC tab** | Finbot backend | Yes (`multi_asset_monte_carlo.py`) | Low — new API endpoint + frontend |

### High-Value Features to Add (Tier 2 — Moderate backend work)

| # | Feature | Source | Description |
|---|---------|--------|-------------|
| 7 | **Efficient Frontier** | PV | Mean-variance frontier visualization with constraint support |
| 8 | **Asset Correlation Matrix** | PV | Cross-asset correlation heatmap + rolling correlation |
| 9 | **Factor Regression** | PV | Fama-French 3/5 factor model regression for any ticker |
| 10 | **Rolling Returns Chart** | Both | Rolling N-month CAGR, Sharpe, volatility over time |
| 11 | **Periodic Contributions** | Both | Monthly/quarterly cash injections in backtest |
| 12 | **Calendar Year Returns Table** | Both | Year-by-year returns heatmap grid |
| 13 | **CSV/JSON Export** | Both | Download metrics, trades, time series |
| 14 | **Benchmark overlay** | Both | Compare strategy equity curve vs buy-and-hold |

### Lower Priority Features (Tier 3 — Significant effort)

| # | Feature | Source | Notes |
|---|---------|--------|-------|
| 15 | **Black-Litterman Model** | PV | Complex — requires view specification UI |
| 16 | **Tactical Allocation Models** | PV | Moving average / momentum switching models |
| 17 | **Fund Screener** | PV | Needs external data source integration |
| 18 | **Asset Cointegration / Autocorrelation** | PV | Statistical analysis tools |
| 19 | **Principal Component Analysis** | PV | Factor decomposition |
| 20 | **Dynamic Allocation (Glidepath)** | PV | Time-varying allocation backtest |

---

## 4. Recommended Implementation Priority

**Phase A — Quick wins (existing backend)**
1. Preset portfolio library (JSON config, clickable on backtesting page)
2. Bond Ladder Simulator page
3. Multi-Asset Monte Carlo tab
4. Pareto Optimizer page
5. CSV export (client-side from DataTable)

**Phase B — High-impact new features**
6. Multi-asset portfolio builder with allocation %
7. Asset Correlation Matrix page
8. Rolling returns/statistics charts
9. Calendar year returns heatmap
10. Benchmark overlay on equity curves

**Phase C — Differentiation features**
11. Efficient Frontier visualization
12. Periodic contributions in backtesting
13. SWR/PWR withdrawal analysis
14. Factor regression (Fama-French 3-factor)

---

## 5. Key Differentiators Finbot Already Has

Finbot has several features that **neither** testfol.io nor Portfolio Visualizer offer:
- **Engine-agnostic architecture** (Backtrader + NautilusTrader)
- **Walk-forward analysis** with train/test visualization
- **Market regime detection** (Bull/Bear/Sideways/High Vol/Low Vol)
- **Experiment tracking** with batch observability
- **Health Economics module** (QALY, cost-effectiveness, clinical scenarios)
- **Risk controls and execution simulation** (latency, checkpoints)
- **12 trading strategies** (vs PV's focus on allocation, not signal-based strategies)

These are significant differentiators worth highlighting in the UI.
