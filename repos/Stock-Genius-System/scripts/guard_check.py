# repos/Stock-Genius-System/scripts/guard_check.py
# Guardian 狀態橋接檢查（完整版・最終封頂・相容修復）
# ❌ 不做股票分析 ❌ 不寫 Vault ❌ 不發 Discord
# ✅ 只讀 Guardian 狀態 ✅ 供 Orchestrator / Stock-Genius 查詢
# ✅ 支援布林值對接 (解決 news_radar.py ImportError)

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# === 確保路徑正確 ===
VAULT_ROOT = r"E:\Quant-Vault"
GUARDIAN_STATE_PATH = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "guardian",
    "guardian_state.json"
)

# === 預設 Guardian 安全狀態 ===
DEFAULT_STATE = {
    "freeze": False,
    "level": "L0",
    "reason": None,
    "updated_at": None
}

# === 冷卻保護 ===
FREEZE_MAX_AGE_MINUTES = 180 

# -------------------------------------------------
# 內部邏輯
# -------------------------------------------------

def _load_guardian_state() -> dict:
    if not os.path.exists(GUARDIAN_STATE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(GUARDIAN_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**DEFAULT_STATE, **data}
    except Exception:
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
# 對外 API (核心)
# -------------------------------------------------

def guardian_freeze_check() -> dict:
    """
    🔒 Guardian 狀態檢查（詳細字典入口）
    """
    state = _load_guardian_state()
    is_expired = _is_freeze_expired(state)
    
    freeze = False if is_expired else bool(state.get("freeze"))
    reason = "freeze_expired_auto_release" if is_expired else state.get("reason")

    return {
        "freeze": freeze,
        "level": state.get("level", "L0"),
        "reason": reason,
        "source": "guardian",
        "checked_at": datetime.now().isoformat()
    }

# -------------------------------------------------
# 膠水對接 (修復 ImportError)
# -------------------------------------------------

def check_guardian() -> bool:
    """
    ✅ 專供 news_radar.py 呼叫的相容性入口
    回傳 True = 安全執行 / False = 凍結攔截
    """
    res = guardian_freeze_check()
    # 邏輯轉換：如果 Guardian freeze(True)，則 check_guardian 應為 False
    return not res["freeze"]

if __name__ == "__main__":
    print(f"相容性測試 (check_guardian): {check_guardian()}")
    print(f"詳細狀態 (guardian_freeze_check): {guardian_freeze_check()}")
