# Limitations and Known Issues

**Last Updated:** 2026-02-12

This document transparently describes the limitations, assumptions, and known issues of Finbot. Understanding these constraints is essential for proper interpretation of results and avoiding misuse.

---

## Table of Contents

1. [Survivorship Bias](#survivorship-bias)
2. [Simulation Assumptions](#simulation-assumptions)
3. [Data Limitations](#data-limitations)
4. [Overfitting and Multiple Testing](#overfitting-and-multiple-testing)
5. [Tax and Cost Considerations](#tax-and-cost-considerations)
6. [Technical Limitations](#technical-limitations)
7. [Model Risk](#model-risk)
8. [Known Issues](#known-issues)
9. [Future Improvements](#future-improvements)

---

## Survivorship Bias

### What It Is

Survivorship bias occurs when analysis only includes assets that "survived" to the present, excluding those that failed or were delisted. This systematically inflates historical performance.

### How It Affects Finbot

**Backtesting:**
- Only tests strategies on surviving ETFs and indexes
- Companies that went bankrupt or delisted are typically not in historical datasets
- Results may overestimate strategy performance by 1-3% annually (varies by asset class)

**Fund Simulations:**
- Simulates funds that exist today, not failed products
- Doesn't account for leveraged ETF closures (many 3x funds closed during 2008-2009)
- Historical tracking error estimates may be optimistic

**Mitigation:**
- Use conservative performance expectations
- Compare against broad market indexes (which rebalance automatically)
- Test strategies across multiple time periods including bear markets
- Add safety margin (2-3%) to expected returns in planning

### Impact

**High Impact:** Backtesting, performance estimates, strategy optimization
**Medium Impact:** Fund simulations (most use well-established products)
**Low Impact:** Bond ladder analysis (treasuries don't face survival risk)

---

## Simulation Assumptions

### Fund Simulator

**Assumptions:**
- **Constant expense ratios**: Fees don't change over time (reality: funds may adjust fees)
- **Perfect tracking minus costs**: Fund perfectly tracks leverage * underlying - expenses - borrowing
- **No liquidity constraints**: Can rebalance daily without market impact
- **LIBOR approximation**: Uses overnight rate approximation (actual borrowing costs vary)
- **No fund closures**: Simulates as if fund existed entire period
- **No extreme scenarios**: May underestimate losses during liquidity crises

**Impact on Results:**
- Tracking error typically within 0.5-1.5% annually for 2-3x funds
- May underestimate costs during high volatility periods
- Doesn't capture extraordinary events (flash crashes, circuit breakers)

### Bond Ladder Simulator

**Assumptions:**
- **No default risk**: Treasuries assumed risk-free (accurate for UST, not corporate bonds)
- **Perfect yield curve**: Smooth interpolation between maturities
- **No transaction costs**: Costless to roll bonds (reality: bid-ask spreads exist)
- **Immediate liquidity**: Can sell bonds at fair value instantly
- **No interest rate derivatives**: Doesn't model options or futures

**Impact on Results:**
- Results accurate for Treasury ladders
- Overstates performance for corporate bond ladders (default risk)
- Transaction costs typically 0.05-0.10% for treasuries, higher for corporates

### Monte Carlo Simulations

**Assumptions:**
- **Normal distribution**: Returns follow normal distribution (reality: fat tails exist)
- **Constant volatility**: Standard deviation doesn't change (reality: volatility clusters)
- **Independent returns**: Each period independent (reality: autocorrelation exists)
- **No regime changes**: Market behavior constant (reality: structural breaks occur)
- **Infinite liquidity**: Can execute any transaction (reality: market impact exists)

**Impact on Results:**
- Underestimates extreme outcomes (black swan events)
- May not capture crisis periods accurately
- Retirement sustainability estimates may be optimistic by 5-10%

**Mitigation:**
- Run scenarios with higher volatility assumptions (+20-30%)
- Include historical worst-case scenarios explicitly
- Use conservative withdrawal rates (3-3.5% vs 4%)

---

## Data Limitations

### Historical Data Coverage

**Limitations:**
- **ETF history limited**: Most leveraged ETFs only exist post-2006
- **Simulation before inception**: Pre-inception simulations are synthetic (not actual performance)
- **Index changes**: S&P 500 composition changes over time (survivorship bias)
- **Corporate actions**: Splits, dividends, mergers may have adjustment errors

**Affected Features:**
- Fund simulations before product launch dates
- Very long-term backtests (>40 years)
- Small-cap and international exposure (less history)

### Data Quality

**Known Issues:**
- **Yahoo Finance adjustments**: Dividend/split adjustments occasionally incorrect
- **FRED data revisions**: Economic data revised after initial release
- **Missing data**: Gaps in price histories require interpolation or forward-fill
- **Delayed updates**: Data typically 1 trading day delayed (not real-time)

**Mitigation:**
- Validate critical data against multiple sources
- Check for obvious errors (prices jumping 50%+ in one day)
- Use data from authoritative sources where possible (FRED for economic data)

### API Rate Limits

**Constraints:**
- Alpha Vantage: 25 requests/day (free tier)
- Yahoo Finance: Unofficial API (may change without notice)
- FRED: 120 requests/minute
- Google Finance: Service account rate limits

**Impact:**
- Full data refresh takes multiple days (not hours)
- Cannot run high-frequency updates
- Development/testing slower due to cache requirements

---

## Overfitting and Multiple Testing

### Strategy Optimization

**Risks:**
- **Parameter tuning**: Optimizing SMA periods, rebalance frequencies to historical data
- **Multiple testing**: Testing many strategies inflates chance of spurious results
- **Look-ahead bias**: Knowledge of historical events influencing strategy design
- **Data mining**: Finding patterns that don't generalize to future

**Example:**
Testing 100 strategies with p=0.05 threshold → expect 5 false positives even if none are truly effective.

**Mitigation in Finbot:**
- Provides 10 pre-defined strategies (not optimized for specific periods)
- Performance metrics calculated, but statistical significance not claimed
- Encourages out-of-sample testing (test on different time periods)
- Documentation emphasizes that past performance ≠ future results

### DCA Optimizer

**Overfitting Risk:** **HIGH**
- Grid search finds best historical parameters
- Results are guaranteed to be optimistic (selection bias)
- Optimal parameters likely different in future

**Proper Use:**
- Use as exploratory tool, not prescriptive
- Test robustness: do nearby parameters also work well?
- Consider transaction costs (rebalancing frequency)
- Apply safety margin to expected returns

---

## Tax and Cost Considerations

### Not Modeled

**Taxes:**
- Capital gains taxes (short-term, long-term)
- Dividend taxes
- Tax-loss harvesting opportunities
- Required minimum distributions (RMDs)
- State and local taxes
- Estate taxes

**Costs:**
- Bid-ask spreads (typically 0.01-0.05% for ETFs)
- Market impact (large orders moving prices)
- Account minimums (fractional shares assumed available)
- Advisory fees (if using financial advisor)
- Fund closures and liquidations

### Impact

**For Tax-Deferred Accounts:** Low impact (taxes deferred)
**For Taxable Accounts:** High impact (could reduce returns by 1-2% annually)
**For Active Strategies:** Very high impact (short-term gains taxed as income)

### Mitigation

- Add 1-2% annual cost assumption for taxable accounts
- Prefer tax-efficient strategies (buy-and-hold, tax-loss harvesting)
- Use tax-advantaged accounts for high-turnover strategies
- Consult tax professional for specific situation

---

## Technical Limitations

### Computation

**Constraints:**
- Single-threaded for most operations (no GPU acceleration)
- Memory-bound for large backtests (>20 years, >10 assets)
- Full simulation suite takes ~5-10 minutes on modern hardware

**Impact:**
- Not suitable for high-frequency trading research
- Large portfolio optimizations (>50 assets) may be slow
- Real-time applications not supported

### API Integration

**Limitations:**
- No real-time data feeds
- No order execution (paper trading only)
- No brokerage integration
- No options pricing

**Finbot Is Not:**
- A trading bot (no live execution)
- A brokerage platform
- A real-time data provider
- A portfolio management system

---

## Model Risk

### All Models Are Wrong

**Fundamental Issue:** All financial models are simplifications of reality.

**Specific Risks:**

1. **Regime Change Risk**
   - Models trained on 1980-2020 may not apply to 2025+
   - Interest rate environment changed dramatically (0% → 5%)
   - Market structure evolves (algorithmic trading, passive flows)

2. **Correlation Breakdown**
   - Historical correlations may not persist
   - Crisis periods show correlation → 1 (diversification fails)
   - "This time is different" sometimes true

3. **Black Swan Events**
   - COVID-19, 2008 financial crisis, 1987 crash not predictable
   - Models underestimate tail risk
   - "100-year events" happen more frequently than models suggest

### Proper Interpretation

**Good Uses:**
- Exploring scenarios ("what if...?")
- Understanding trade-offs (risk vs return)
- Comparing strategies relatively (A vs B)
- Educational purposes

**Bad Uses:**
- Predicting future returns precisely
- Guaranteeing investment outcomes
- Making high-stakes decisions without other input
- Treating simulation results as certainty

---

## Known Issues

### Bugs and Limitations

1. **Backtest Start Dates**
   - First ~30 days may have inaccurate results (indicators warming up)
   - **Workaround:** Discard first month of backtest results

2. **Bond Ladder Callable Bonds**
   - Doesn't model callable bonds (assumes non-callable treasuries)
   - **Workaround:** Use treasury-only analysis, add premium for callable risk

3. **Currency Risk**
   - International exposure not adjusted for FX fluctuations
   - **Workaround:** Use USD-denominated ETFs only

4. **Extreme Volatility**
   - Fund simulator may break down during volatility >100% annualized
   - **Workaround:** Review results manually, add safety checks

5. **Memory Usage**
   - Very long backtests (50+ years, 20+ assets) may consume >8GB RAM
   - **Workaround:** Reduce time period or number of assets

### Documentation Gaps

- Limited docstring coverage in some utility modules
- API documentation complete for services, partial for utilities
- No formal specification document

### Testing Gaps

- Integration tests limited (mostly unit tests)
- No stress testing suite
- No performance regression tests
- Edge case coverage incomplete

---

## Future Improvements

### Planned Enhancements

**Short-term (1-3 months):**
- Add tax-aware backtesting mode
- Expand integration test coverage
- Add slippage and market impact models
- Improve bond ladder callable bond handling

**Medium-term (3-6 months):**
- Add options pricing and analysis
- Real-time data integration (paper trading)
- Multi-currency support
- Improved Monte Carlo (GARCH models, copulas)

**Long-term (6-12 months):**
- Machine learning strategy framework
- Portfolio rebalancing optimizer (beyond DCA)
- Risk budgeting tools
- Scenario analysis framework

### Contributions Welcome

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to help address these limitations.

---

## Conclusion

**Key Takeaways:**

1. **Finbot is a research and educational tool**, not a production trading system
2. **All results are backward-looking** and may not predict future performance
3. **Models make simplifying assumptions** that may not hold in reality
4. **Use results as inputs to decisions**, not as the sole decision-maker
5. **Combine quantitative analysis with qualitative judgment**

**Responsible Use:**

- ✅ Exploring investment strategies and trade-offs
- ✅ Understanding historical performance patterns
- ✅ Educational and research purposes
- ✅ Generating hypotheses for further investigation
- ❌ Making investment decisions without additional due diligence
- ❌ Expecting simulated returns in real trading
- ❌ Using as sole basis for financial planning
- ❌ Treating backtested strategies as proven

**Disclaimer:**

Finbot is provided "as is" without warranty. The authors are not financial advisors and this software does not constitute financial advice. Past performance does not guarantee future results. Always consult with qualified financial professionals before making investment decisions.

---

**Questions or Issues?**

- Open an issue: [GitHub Issues](https://github.com/jerdaw/finbot/issues)
- Read the docs: [Documentation](../docs_site/index.md)
- See contributing guide: [CONTRIBUTING.md](../CONTRIBUTING.md)
