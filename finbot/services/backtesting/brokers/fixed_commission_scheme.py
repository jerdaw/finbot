from __future__ import annotations

import backtrader as bt


class FixedCommissionScheme(bt.CommInfoBase):
    paras = (
        ("commission", 10),
        ("stocklike", True),
        ("commtype", bt.CommInfoBase.COMM_FIXED),
    )

    def _getcommission(self, size: float, price: float, pseudoexec: bool) -> float:
        return self.p.commission
