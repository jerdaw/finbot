# Specific Funds

Finbot ships a registry of predefined fund simulations so contributors can work
with common leveraged-equity and treasury ETF surfaces without redefining each
configuration manually.

## Supported Families

- **S&P 500**: `SPY`, `SSO`, `UPRO`
- **Nasdaq-100**: `QQQ`, `QLD`, `TQQQ`
- **Long-term Treasuries**: `TLT`, `UBT`, `TMF`
- **Intermediate Treasuries**: `IEF`, `UST`, `TYD`
- **Short-term Treasuries**: `SHY`, `2X_STT`, `3X_STT`

## Recommended Entry Point

Use `simulate_fund()` for new code. The ticker-specific helpers remain for
compatibility, but the registry-backed entry point is the maintained path.

```python
from finbot.services.simulation.sim_specific_funds import simulate_fund

upro = simulate_fund("UPRO", force_update=True)
tmf = simulate_fund("TMF")
```

## API Reference

::: finbot.services.simulation.sim_specific_funds.simulate_fund
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## See Also

- [Fund Simulator](fund-simulator.md)
- [Leveraged ETF Simulation Research](../../../research/leveraged-etf-simulation.md)
- [Fund Simulation Notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/01_fund_simulation_demo.ipynb)
