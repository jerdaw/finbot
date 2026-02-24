from __future__ import annotations

import backtrader as bt


class CommInfo_NoCommission(bt.CommInfoBase):  # noqa: N801 - Backtrader naming convention
    """Zero-commission scheme for backtesting without trading costs.

    Params:
        commission: Commission rate (0.0 -- no cost).
        commtype: Fixed commission type (COMM_FIXED).
        stocklike: Whether the instrument is stock-like (True).
    """

    params = {  # noqa: RUF012 - Backtrader pattern for class attributes
        "commission": 0.0,
        "mult": 1.0,
        "margin": None,
        "commtype": bt.CommInfoBase.COMM_FIXED,
        "stocklike": True,
        "percabs": False,
        "interest": 0.0,
        "interest_long": False,
        "leverage": 1.0,
    }


class CommInfo_WealthSimple(bt.CommInfoBase):  # noqa: N801 - Backtrader naming convention
    """WealthSimple-style percentage-based commission scheme.

    Charges a 1.5% commission on trade value, modelling WealthSimple's
    currency conversion spread on USD trades.

    Params:
        commission: Percentage commission rate (1.5%).
        commtype: Percentage commission type (COMM_PERC).
        stocklike: Whether the instrument is stock-like (True).
    """

    params = {  # noqa: RUF012 - Backtrader pattern for class attributes
        "commission": 1.5,
        "mult": 1.0,
        "margin": None,
        "commtype": bt.CommInfoBase.COMM_PERC,
        "stocklike": True,
        "percabs": False,
        "interest": 0.0,
        "interest_long": False,
        "leverage": 1.0,
    }


class CommInfo_QuestTrade(bt.CommInfoBase):  # noqa: N801 - Backtrader naming convention
    """Questrade-style commission scheme with asymmetric buy/sell costs.

    Buy orders are charged CAD 0.01 (ECN fee) while sell orders incur
    a fixed CAD 5 commission.

    Params:
        commission: Fixed sell-side commission (5).
        stocklike: Whether the instrument is stock-like (True).
        commtype: Fixed commission type (COMM_FIXED).
    """

    params = {  # noqa: RUF012 - Backtrader pattern for class attributes
        "commission": 5,
        "stocklike": True,
        "commtype": bt.CommInfoBase.COMM_FIXED,
    }

    def _getcommission(self, size: float, price: float, pseudoexec: bool) -> float:
        """Return asymmetric commission: 0.01 for buys, fixed rate for sells.

        Args:
            size: Number of shares (positive for buy, negative for sell).
            price: Execution price per share.
            pseudoexec: Whether this is a simulated execution for margin check.

        Returns:
            0.01 for buy orders, or the fixed commission param for sell orders.
        """
        return 0.01 if size > 0 else self.p.commission
