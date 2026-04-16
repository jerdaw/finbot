# Choosing a Backtest Engine

This public guide summarizes when to use Backtrader, NautilusTrader, or both
inside Finbot.

## Quick Decision Matrix

| Your Goal | Recommended Engine | Why |
| --- | --- | --- |
| Pure backtesting only | Backtrader | Mature, stable, and simpler to use |
| Planning for live trading | NautilusTrader | Live-trading support and more realistic fills |
| Quick prototyping | Backtrader | Faster setup and gentler learning curve |
| Cross-validation | Both | Compare behavior across engines |
| Gradual migration | Both | Keep Backtrader workflows while evaluating Nautilus |

## Finbot's Current Position

- Backtrader remains the default engine for familiar bar-based backtesting.
- NautilusTrader remains available for strategies that may eventually move
  toward live trading.
- Finbot's architecture supports an adapter-first hybrid model rather than a
  forced rewrite.

## Read The Full Guidance

- [Full repository guide](https://github.com/jerdaw/finbot/blob/main/docs/guides/choosing-backtest-engine.md)
- [ADR-011 decision record](https://github.com/jerdaw/finbot/blob/main/docs/adr/ADR-011-nautilus-decision.md)
- [Nautilus pilot evaluation](https://github.com/jerdaw/finbot/blob/main/docs/research/nautilus-pilot-evaluation.md)

## Scope Note

This page is a public wrapper for the longer repository guide so the published
docs navigation stays coherent.