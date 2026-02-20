# E6 Comparative Benchmark Artifact

- Generated: 2026-02-20T04:41:18.331308+00:00
- Python: 3.14.2
- Platform: Linux-6.12.68-1-MANJARO-x86_64-with-glibc2.42

| Engine | Scenario | Scenario ID | Samples | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| backtrader | SPY 2019-2020 buy-and-hold | gs01 | 3 | native_backtrader | yes | high | 0.4622 | 1.22 | 0.558403 | 0.247812 | -0.335029 | 155840.34 |
| nautilus-pilot | SPY 2019-2020 buy-and-hold | gs01 | 3 | native_nautilus | yes | high | 0.2775 | 0.74 | 0.493563 | 0.222619 | -0.340598 | 149356.30 |
| backtrader | SPY/TLT 2010-2026 dual momentum | gs02 | 3 | native_backtrader | yes | high | 5.6195 | 3.60 | 1.000277 | 0.044082 | -0.272478 | 200027.71 |
| nautilus-pilot | SPY/TLT 2010-2026 dual momentum | gs02 | 3 | native_nautilus_full | no | low | 22.5765 | 5.65 | 0.896277 | 0.040549 | -0.340714 | 189627.74 |
| backtrader | SPY/QQQ/TLT 2010-2026 risk parity | gs03 | 3 | native_backtrader | yes | high | 8.6989 | 7.81 | 4.275048 | 0.109018 | -0.293194 | 527504.83 |
| nautilus-pilot | SPY/QQQ/TLT 2010-2026 risk parity | gs03 | 3 | native_nautilus_full | no | low | 18.3425 | 9.40 | 2.993284 | 0.089816 | -0.313036 | 399328.43 |

## Equivalence Notes

- `backtrader` `gs01`: Backtrader baseline for frozen GS-01 NoRebalance scenario.
- `nautilus-pilot` `gs01`: Single-symbol NoRebalance maps to one-time market buy and hold.
- `backtrader` `gs02`: Backtrader baseline for frozen GS-02 DualMomentum scenario.
- `nautilus-pilot` `gs02`: DualMomentum executed with native Nautilus strategy hooks; benchmark metrics are derived from native mark-to-market portfolio valuation sampled on synchronized multi-symbol daily bars. Tolerance-gated classification vs Backtrader baseline: roi_abs=0.104000<=0.080000, cagr_abs=0.003533<=0.012000, max_drawdown_abs=0.068236<=0.030000, ending_value_relative=0.051993<=0.080000; result=fail (roi_abs, max_drawdown_abs).
- `backtrader` `gs03`: Backtrader baseline for frozen GS-03 RiskParity scenario.
- `nautilus-pilot` `gs03`: RiskParity executed with native Nautilus strategy hooks; benchmark metrics are derived from native mark-to-market portfolio valuation sampled on synchronized multi-symbol daily bars. Tolerance-gated classification vs Backtrader baseline: roi_abs=1.281764<=0.100000, cagr_abs=0.019202<=0.015000, max_drawdown_abs=0.019842<=0.040000, ending_value_relative=0.242986<=0.100000; result=fail (roi_abs, cagr_abs, ending_value_relative).
