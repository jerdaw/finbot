# Dashboard

The Finbot dashboard provides an interactive Streamlit web interface for running simulations, backtests, optimizations, and health economics analyses.

## Overview

The dashboard offers:

- **6 specialized pages**: Overview, Simulations, Backtesting, Optimizer, Monte Carlo, Data Status, Health Economics
- **Interactive charts**: Plotly visualizations with zoom, pan, hover
- **Parameter controls**: Sliders, dropdowns, date pickers for easy configuration
- **Real-time results**: Instant updates when parameters change
- **Export functionality**: Download results as CSV or images

## Launching the Dashboard

### Command Line

```bash
# Launch dashboard
finbot dashboard

# Or directly with Streamlit
uv run streamlit run finbot/dashboard/app.py
```

**Default:** Opens browser at http://localhost:8501

### Docker

```bash
# Launch dashboard in Docker container
make docker-dashboard

# Or with docker-compose
docker-compose up dashboard
```

**Access:** http://localhost:8501

## Dashboard Module

Main dashboard entry point and app configuration:

::: finbot.dashboard.app
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Pages

### 1. Overview (Home)

**Location:** `finbot/dashboard/app.py` (main page)

**Features:**
- Project introduction and purpose
- Quick navigation to all pages
- System status indicators
- Recent activity summary

### 2. Simulations

**Location:** `finbot/dashboard/pages/1_simulations.py`

**Features:**
- Fund simulation interface (15 pre-configured funds)
- Index simulation (S&P 500, Nasdaq 100, Treasury indexes)
- Custom parameter adjustment
- Performance charts (price, returns, cumulative returns)
- Comparison with actual ETF data (tracking error)

**Interactive controls:**
- Fund/index selector (dropdown)
- Date range picker (start/end dates)
- Leverage ratio slider (for custom simulations)
- Expense ratio input
- Display toggles (log scale, show actual vs simulated)

**Charts:**
- Price history line chart
- Daily returns histogram
- Cumulative returns comparison
- Tracking error over time

### 3. Backtesting

**Location:** `finbot/dashboard/pages/2_backtesting.py`

**Features:**
- Strategy selection (12 strategies)
- Multi-asset backtesting
- Strategy parameter tuning
- Performance metrics display
- Trade log visualization

**Interactive controls:**
- Strategy selector (dropdown)
- Asset tickers (multi-select)
- Parameter inputs (strategy-specific)
- Date range picker
- Commission rate slider
- Starting cash input

**Metrics displayed:**
- CAGR, Sharpe, Sortino, Calmar ratios
- Max drawdown, volatility
- Win rate, profit factor
- Total trades, win/loss breakdown

**Charts:**
- Portfolio value over time
- Drawdown chart
- Monthly/yearly returns heatmap
- Trade markers on price chart

### 4. Optimizer

**Location:** `finbot/dashboard/pages/3_optimizer.py`

**Features:**
- DCA optimization interface
- Allocation ratio heatmaps
- Multi-metric optimization (Sharpe, Sortino, Calmar, CAGR)
- Efficient frontier visualization

**Interactive controls:**
- Asset tickers (multi-select)
- Optimization metric selector (Sharpe, Sortino, Calmar, CAGR)
- Investment amount slider
- Duration range (min/max years)
- Frequency selector (monthly, quarterly)

**Visualizations:**
- Heatmap: Allocation ratio vs. Sharpe ratio
- Scatter plot: Risk vs. return (efficient frontier)
- Bar chart: Top 10 allocation strategies
- Table: Full optimization results (sortable)

### 5. Monte Carlo

**Location:** `finbot/dashboard/pages/4_monte_carlo.py`

**Features:**
- Risk simulation interface
- Multi-asset Monte Carlo
- Percentile projections (5th, 50th, 95th)
- Distribution analysis

**Interactive controls:**
- Ticker selector
- Number of trials slider (1,000 - 50,000)
- Time horizon slider (1-50 years)
- Initial investment input
- Annual contribution input

**Charts:**
- Fan chart (percentile bands)
- Histogram of final values
- Probability of achieving target
- Distribution statistics table

### 6. Data Status

**Location:** `finbot/dashboard/pages/5_data_status.py`

**Features:**
- Real-time data freshness monitoring
- Data source health dashboard
- Refresh trigger buttons
- Staleness alerts

**Status indicators:**
- ✓ FRESH (green badge)
- ⚠ STALE (yellow badge)
- ✗ MISSING (red badge)

**Data sources tracked:**
- YFinance (1-day threshold)
- FRED (7-day threshold)
- Google Finance (7-day threshold)
- Alpha Vantage (7-day threshold)
- BLS (30-day threshold)
- Shiller (90-day threshold)
- Simulations (1-day threshold)

**Actions:**
- Refresh data source button (triggers update)
- View last update timestamp
- Check data file count
- Navigate to data directory

### 7. Health Economics

**Location:** `finbot/dashboard/pages/6_health_economics.py`

**Features:**
- QALY simulation interface
- Cost-effectiveness analysis (ICER, NMB, CEAC)
- Treatment optimization
- Clinical scenario selector

**Interactive controls:**
- Treatment parameters (cost, utility, mortality, duration)
- Control parameters (cost, utility, mortality, duration)
- Number of simulations slider (1,000 - 100,000)
- WTP threshold slider ($0 - $200,000)
- Clinical scenario selector (pre-configured scenarios)

**Clinical scenarios:**
- Type 2 Diabetes (Metformin vs. GLP-1)
- Hypertension (Standard vs. Intensive BP control)
- Hyperlipidemia (Statin vs. PCSK9 inhibitor)
- Custom (user-defined parameters)

**Charts:**
- Cost-effectiveness plane (scatter plot)
- CEAC (cost-effectiveness acceptability curve)
- Distribution histograms (cost, QALYs, ICER, NMB)
- Tornado diagram (sensitivity analysis)

**Metrics displayed:**
- ICER ($/QALY)
- NMB ($)
- Probability cost-effective (%)
- Incremental cost ($)
- Incremental QALYs

**Thresholds shown:**
- NICE: £20,000 - £30,000/QALY (~$25,000 - $37,500)
- CADTH: $30,000 - $60,000 CAD/QALY (~$37,500 - $75,000 USD)
- US: $50,000 - $150,000/QALY
- WHO: 1-3× GDP per capita

## Reusable Components

The dashboard includes reusable chart components:

**Location:** `finbot/dashboard/components/`

Common components:
- Price chart with volume
- Returns distribution histogram
- Cumulative returns line chart
- Drawdown area chart
- Correlation heatmap
- Performance metrics table
- Parameter control sidebar

## Customization

### Adding a New Page

1. Create file in `finbot/dashboard/pages/`:
   ```python
   # finbot/dashboard/pages/7_my_page.py
   import streamlit as st

   st.title("My Custom Page")
   st.write("Page content here")
   ```

2. Streamlit automatically adds to sidebar navigation

3. Use naming convention: `N_page_name.py` (N = order)

### Styling

The dashboard uses Streamlit's default Material Design theme with custom tweaks:

```python
# Custom CSS in app.py
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)
```

## Performance

Dashboard optimizations:

- **Caching**: `@st.cache_data` for expensive computations
- **Lazy loading**: Data loaded only when page accessed
- **Parquet storage**: Fast data reads from cached results
- **Incremental updates**: Rerun only changed components

## Examples

### Running a Backtest

1. Navigate to **Backtesting** page
2. Select strategy (e.g., "Rebalance")
3. Choose assets (e.g., SPY, TLT)
4. Set date range (e.g., 2010-01-01 to 2024-01-01)
5. Adjust parameters (e.g., rebalance_days: 30)
6. Click "Run Backtest"
7. Review results:
   - Portfolio value chart
   - Performance metrics
   - Trade log
8. Export results (Download CSV button)

### Optimizing DCA Allocation

1. Navigate to **Optimizer** page
2. Select assets (e.g., SPY, TLT)
3. Set investment amount (e.g., $1,000/month)
4. Choose optimization metric (e.g., Sharpe ratio)
5. Set duration range (e.g., 10-30 years)
6. Click "Optimize"
7. Review heatmap for optimal allocation
8. Export top strategies

### Running Monte Carlo Simulation

1. Navigate to **Monte Carlo** page
2. Select ticker (e.g., SPY)
3. Set number of trials (e.g., 10,000)
4. Set time horizon (e.g., 30 years)
5. Set initial investment (e.g., $100,000)
6. Set annual contribution (e.g., $10,000)
7. Click "Run Simulation"
8. Review fan chart and distribution
9. Check probability of achieving target

## Deployment

### Local Development

```bash
# Development mode (auto-reload)
uv run streamlit run finbot/dashboard/app.py --server.runOnSave true
```

### Production (Docker)

```bash
# Build and run with docker-compose
docker-compose up -d dashboard

# Access at http://localhost:8501
```

### Streamlit Cloud (Future)

1. Connect GitHub repo to Streamlit Cloud
2. Configure secrets (API keys)
3. Deploy from main branch
4. Access at https://finbot.streamlit.app

## Limitations

- **Single-user**: Not designed for multi-tenancy
- **No authentication**: Open access (use behind firewall)
- **In-memory state**: Session state resets on refresh
- **Limited concurrency**: One simulation at a time per session

## Troubleshooting

### Dashboard won't start

```bash
# Check Streamlit installation
uv run streamlit --version

# Check for port conflicts
lsof -i :8501

# Try different port
uv run streamlit run finbot/dashboard/app.py --server.port 8502
```

### Slow performance

```bash
# Clear Streamlit cache
uv run streamlit cache clear

# Reduce simulation complexity (fewer trials, shorter horizon)

# Check data file sizes (large parquet files slow loading)
```

### Page not updating

```bash
# Force rerun: Press 'R' in browser

# Check browser console for errors (F12 → Console tab)

# Restart dashboard: Ctrl+C, then relaunch
```

## See Also

- [CLI Reference](cli.md) - Command-line interface
- [Backtesting Strategies](services/backtesting/strategies.md) - Strategy documentation
- [DCA Optimizer](services/optimization/dca-optimizer.md) - Optimization API
- [Monte Carlo Simulator](services/simulation/monte-carlo.md) - Monte Carlo API
- [Health Economics](services/health-economics.md) - Health economics API
