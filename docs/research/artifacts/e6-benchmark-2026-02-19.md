# E6 Comparative Benchmark Artifact

- Generated: 2026-02-19T18:18:06.148620+00:00
- Python: 3.14.2
- Platform: Linux-6.12.68-1-MANJARO-x86_64-with-glibc2.42

| Engine | Scenario | Scenario ID | Samples | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| backtrader | SPY 2019-2020 buy-and-hold | gs01 | 3 | native_backtrader | yes | high | 0.4810 | 1.22 | 0.558403 | 0.247812 | -0.335029 | 155840.34 |
| nautilus-pilot | SPY 2019-2020 native run | gs01 | 3 | native_nautilus | yes | high | 0.2825 | 0.74 | 0.493563 | 0.222619 | -0.340598 | 149356.30 |

## Equivalence Notes

- `backtrader` `gs01`: Backtrader baseline for frozen GS-01 NoRebalance scenario.
- `nautilus-pilot` `gs01`: Single-symbol NoRebalance maps to one-time market buy and hold.
