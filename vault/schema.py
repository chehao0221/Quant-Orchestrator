from typing import TypedDict, List, Literal
from datetime import datetime

Market = Literal["TW", "US"]

class StockHistory(TypedDict):
    symbol: str
    market: Market

    # 次數 / 表現
    appear_count: int
    hit_count: int
    avg_pred_ret: float

    # 時間
    first_seen: str
    last_seen: str
    last_hit: str | None

    # 權重
    base_weight: float        # 原始權重
    decay_weight: float       # 衰退後權重（AI 用）
    importance: Literal["CORE", "EXPLORER"]

class VaultState(TypedDict):
    version: int
    updated_at: str
    stocks: List[StockHistory]
