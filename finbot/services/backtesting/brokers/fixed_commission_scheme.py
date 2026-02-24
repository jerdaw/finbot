from __future__ import annotations

import backtrader as bt


class FixedCommissionScheme(bt.CommInfoBase):
    """Fixed-dollar commission scheme for Backtrader.

    Charges a flat commission per trade regardless of order size.

    Params:
        commission: Fixed dollar amount charged per trade (default 10).
        stocklike: Whether the instrument is stock-like (default True).
        commtype: Commission type, fixed amount (COMM_FIXED).
    """

    paras = (
        ("commission", 10),
        ("stocklike", True),
        ("commtype", bt.CommInfoBase.COMM_FIXED),
    )

    def _getcommission(self, size: float, price: float, pseudoexec: bool) -> float:
        """Return the fixed commission amount.

        Args:
            size: Number of shares in the order.
            price: Execution price per share.
            pseudoexec: Whether this is a simulated execution for margin check.

        Returns:
            The fixed commission value from the params tuple.
        """
        return self.p.commission
