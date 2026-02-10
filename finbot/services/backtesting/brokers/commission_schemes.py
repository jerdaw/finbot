import backtrader as bt


class CommInfo_NoCommission(bt.CommInfoBase):
    params = dict(
        commission=0.0,
        mult=1.0,
        margin=None,
        commtype=bt.CommInfoBase.COMM_FIXED,
        stocklike=True,
        percabs=False,
        interest=0.0,
        interest_long=False,
        leverage=1.0,
    )


class CommInfo_WealthSimple(bt.CommInfoBase):
    params = dict(
        commission=1.5,
        mult=1.0,
        margin=None,
        commtype=bt.CommInfoBase.COMM_PERC,
        stocklike=True,
        percabs=False,
        interest=0.0,
        interest_long=False,
        leverage=1.0,
    )


class CommInfo_QuestTrade(bt.CommInfoBase):
    params = dict(
        commission=5,
        stocklike=True,
        commtype=bt.CommInfoBase.COMM_FIXED,
    )

    def _getcommission(self, size, price, pseudoexec):
        return 0.01 if size > 0 else self.p.commission
