from typing import TypedDict, List, Optional
from datetime import datetime

# ==================================================
# 基礎股票預測結構
# ==================================================

class StockPrediction(TypedDict):
    symbol: str                 # 股票代碼
    market: str                 # TW / US
    date: str                   # YYYY-MM-DD
    price: float                # 收盤價
    pred_return: float          # 預估漲跌 %
    confidence: float           # 0.0 ~ 1.0
    support: float
    resistance: float
    model: str                  # 使用模型名稱
    created_at: str             # ISO timestamp


# ==================================================
# 回測紀錄（單筆）
# ==================================================

class BacktestRecord(TypedDict):
    symbol: str
    market: str
    date: str
    pred_return: float
    real_return: float
    hit: bool


# ==================================================
# 回測彙總（顯示用）
# ==================================================

class BacktestSummary(TypedDict):
    market: str
    window: int                 # 例如 5 日
    trades: int
    hit_rate: float
    avg_return: float
    max_drawdown: float
    generated_at: str


# ==================================================
# Vault 檔案 Metadata（給 AI 判斷刪除用）
# ==================================================

class VaultFileMeta(TypedDict):
    path: str
    market: Optional[str]
    symbol: Optional[str]
    created_at: str
    last_read_at: Optional[str]
    level: int                  # L0–L5
    is_core: bool
    is_top5: bool
    has_black_swan: bool
