"""Shared helpers for estimating trade costs from executed backtest trades."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from finbot.core.contracts.costs import CostEvent, CostModel, CostSummary, CostType


def build_cost_summary_from_trades(
    trades: Iterable[Any],
    *,
    commission_model: CostModel,
    spread_model: CostModel,
    slippage_model: CostModel,
) -> CostSummary:
    """Estimate trade frictions using the configured cost models.

    The input trades are expected to expose ``timestamp``, ``symbol``, ``size``, and
    ``price`` attributes like the backtesting trade tracker does.
    """

    cost_events: list[CostEvent] = []
    total_commission = 0.0
    total_spread = 0.0
    total_slippage = 0.0

    for trade in trades:
        symbol = str(getattr(trade, "symbol", ""))
        quantity = abs(float(getattr(trade, "size", 0.0)))
        price = float(getattr(trade, "price", 0.0))
        timestamp = pd.Timestamp(getattr(trade, "timestamp", None))

        commission = commission_model.calculate_cost(
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=timestamp,
        )
        total_commission += commission
        if commission > 0:
            cost_events.append(
                CostEvent(
                    timestamp=timestamp,
                    symbol=symbol,
                    cost_type=CostType.COMMISSION,
                    amount=commission,
                    basis=commission_model.get_name(),
                )
            )

        spread = spread_model.calculate_cost(
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=timestamp,
        )
        total_spread += spread
        if spread > 0:
            cost_events.append(
                CostEvent(
                    timestamp=timestamp,
                    symbol=symbol,
                    cost_type=CostType.SPREAD,
                    amount=spread,
                    basis=spread_model.get_name(),
                )
            )

        slippage = slippage_model.calculate_cost(
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=timestamp,
        )
        total_slippage += slippage
        if slippage > 0:
            cost_events.append(
                CostEvent(
                    timestamp=timestamp,
                    symbol=symbol,
                    cost_type=CostType.SLIPPAGE,
                    amount=slippage,
                    basis=slippage_model.get_name(),
                )
            )

    return CostSummary(
        total_commission=total_commission,
        total_spread=total_spread,
        total_slippage=total_slippage,
        total_borrow=0.0,
        total_market_impact=0.0,
        cost_events=tuple(cost_events),
    )
