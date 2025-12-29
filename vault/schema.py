from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

Market = Literal["TW", "US"]

@dataclass
class BacktestRecord:
    symbol: str
    market: Market
    date: str               # YYYY-MM-DD
    horizon: int            # 預測天數
    pred_return: float
    actual_return: float
    confidence: float
    model_version: str
    created_at: datetime
