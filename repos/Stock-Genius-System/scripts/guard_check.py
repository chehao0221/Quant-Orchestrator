# repos/Stock-Genius-System/scripts/guard_check.py
# Guardian 狀態橋接檢查（完整版・最終封頂）
# 職責：讀取事實 JSON 並提供給 news_radar 等腳本布林判斷

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# === 路徑注入（確保能在子目錄執行） ===
VAULT_ROOT = r"E:\Quant-Vault"
GUARDIAN_STATE_PATH = os.path.join(
    VAULT_ROOT, "LOCKED_DECISION", "guardian", "guardian_state.json"
)

# === 預設參數 ===
DEFAULT_STATE = {
    "freeze": False,
    "level": "L0",
    "reason": None,
    "updated_at": None
}
FREEZE_MAX_AGE_MINUTES = 180  # 3 小時自動過期

# -------------------------------------------------
# 事實讀取層
# -------------------------------------------------

def _load_guardian_state() -> dict:
    if not os.path.exists(GUARDIAN_STATE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(GUARDIAN_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**DEFAULT_STATE, **data}
    except:
        return DEFAULT_STATE.copy()

def _is_freeze_expired(state: dict) -> bool:
    if not state.get("freeze"): return False
    ts = state.get("updated_at")
    if not ts: return False
    try:
        updated = datetime.fromisoformat(ts)
        return datetime.now() - updated > timedelta(minutes=FREEZE_MAX_AGE_MINUTES)
    except:
        return False

# -------------------------------------------------
# 核心入口 1：詳細字典版 (供未來擴充)
# -------------------------------------------------

def guardian_freeze_check() -> dict:
    state = _load_guardian_state()
    expired = _is_freeze_expired(state)
    
    return {
        "freeze": False if expired else bool(state.get("freeze")),
        "level": state.get("level", "L0"),
        "reason": "auto_released" if expired else state.get("reason"),
        "checked_at": datetime.now().isoformat()
    }

# -------------------------------------------------
# 核心入口 2：布林放行版 (解決 news_radar 報錯)
# -------------------------------------------------

def check_guardian(block_level: int = 5) -> bool:
    """
    回傳是否放行 (True = 安全跑 / False = 攔截停)
    - block_level: 觸發攔截的數字 (預設 5)
    - 轉換邏輯：L0->0, L1->1, ... L5->5
    """
    res = guardian_freeze_check()
    
    # 若 JSON 直接標記 freeze，直接攔截
    if res["freeze"]:
        return False

    # 解析 Level 數字
    try:
        level_num = int(res["level"].replace("L", ""))
    except:
        level_num = 0

    # 鐵律：目前等級必須「小於」攔截等級才放行
    # (例如：目前 L2 < 攔截門檻 L5 -> True 放行)
    return level_num < block_level

if __name__ == "__main__":
    print(f"Current Status: {guardian_freeze_check()}")
    print(f"Is Safe to Run? {check_guardian()}")
