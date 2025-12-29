from typing import TypedDict, List, Optional


# ===============================
# 單一股票每日紀錄
# ===============================
class DailySignal(TypedDict):
    date: str                # YYYY-MM-DD
    symbol: str
    market: str              # TW / US
    pred: float
    confidence: float
    is_top5: bool
    is_core: bool


# ===============================
# 回測紀錄（5 日 rolling）
# ===============================
class BacktestRecord(TypedDict):
    date: str
    symbol: str
    pred_ret: float
    actual_ret: float
    hit: bool


# ===============================
# Core Watch 狀態
# ===============================
class CoreWatchItem(TypedDict):
    symbol: str
    market: str
    weight: float            # 衰退後權重
    last_active: str          # YYYY-MM-DD
    hit_count: int
    miss_count: int


# ===============================
# Vault 主結構
# ===============================
class VaultState(TypedDict):
    market: str
    last_update: str
    data_status: str         # OK / INCOMPLETE / FAILED / MARKET_CLOSED
    core_watch: List[CoreWatchItem]
    daily_signals: List[DailySignal]
    backtests: List[BacktestRecord]
