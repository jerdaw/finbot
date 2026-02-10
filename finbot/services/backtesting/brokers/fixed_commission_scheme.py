import backtrader as bt


class FixedCommissionScheme(bt.CommInfoBase):
    paras = (
        ("commission", 10),
        ("stocklike", True),
        ("commtype", bt.CommInfoBase.COMM_FIXED),
    )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission
