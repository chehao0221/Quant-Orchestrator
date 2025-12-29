from typing import TypedDict, List

class StockScore(TypedDict):
    symbol: str
    market: str            # "TW" / "US"
    date: str

    pred_ret: float
    confidence: float

    support: float
    resistance: float

    volume_rank: int

    is_top5: bool
    is_core: bool
    is_black_swan: bool

    core_score: float
    days_since_active: int
