# Quant-Orchestrator/tools/vault_ai_judge.py
import time
from pathlib import Path
from vault_policy import classify_stock_path

SECONDS_PER_DAY = 86400

# 你指定的參數
N_DAYS = 180
K_RECENT_TOP5 = 30
RECENT_READ_PROTECT_DAYS = 7
TOP5_HISTORY_PROTECT_TIMES = 3

def ai_should_delete(
    file_path: Path,
    *,
    last_read_ts: float | None,
    top5_count: int,
    is_market_event: bool,
):
    """
    全部成立才刪
    """

    category = classify_stock_path(file_path)

    # ❶ protected 區幾乎不刪
    if category == "protected":
        return False

    # ❷ 不是冷資料 → 不刪
    if category != "cold":
        return False

    now = time.time()

    # ❸ 超過 N 天未被讀取
    if last_read_ts and (now - last_read_ts) < N_DAYS * SECONDS_PER_DAY:
        return False

    # ❹ 最近 K 次 Top5 出現過
    if top5_count >= K_RECENT_TOP5:
        return False

    # ❺ 曾多次進 Top5（隱性保險）
    if top5_count >= TOP5_HISTORY_PROTECT_TIMES:
        return False

    # ❻ 市場異常資料 → 暫緩刪除
    if is_market_event:
        return False

    return True
