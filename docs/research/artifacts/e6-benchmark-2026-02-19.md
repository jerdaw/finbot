# E6 Comparative Benchmark Artifact

- Generated: 2026-02-19T18:54:55.095609+00:00
- Python: 3.14.2
- Platform: Linux-6.12.68-1-MANJARO-x86_64-with-glibc2.42

| Engine | Scenario | Scenario ID | Samples | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| backtrader | SPY/TLT 2010-2026 dual momentum | gs02 | 1 | native_backtrader | yes | high | 6.7242 | 4.15 | 1.000277 | 0.044082 | -0.272478 | 200027.71 |
| nautilus-pilot | SPY/TLT 2010-2026 dual momentum | gs02 | 1 | native_nautilus_proxy | yes | medium | 0.5702 | 1.24 | 0.896277 | 0.040549 | -0.340714 | 189627.72 |

## Equivalence Notes

- `backtrader` `gs02`: Backtrader baseline for frozen GS-02 DualMomentum scenario.
- `nautilus-pilot` `gs02`: DualMomentum signal/rebalance logic mirrored from Backtrader strategy with deterministic close-price fills and integer share sizing.
