from __future__ import annotations

import datetime as dt

NYSE_MARKET_OPEN_TIME = dt.time(9, 30, 0)
NYSE_MARKET_CLOSE_TIME = dt.time(16, 0, 0)
NYSE_PREMARKET_OPEN_TIME = dt.time(4, 0, 0)
NYSE_AFTERMARKET_CLOSE_TIME = dt.time(20, 0, 0)


ALIGNED_DAILY_DATETIME = NYSE_MARKET_CLOSE_TIME
