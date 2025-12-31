# -------------------------------------------------
# Compatibility Adapter（封頂穩定層）
# -------------------------------------------------
# 提供舊系統 / scripts 統一使用的 check_guardian 介面
# 不影響核心 Guardian 架構

from shared.guardian_state import get_guardian_level


def check_guardian(required_level: int = 1) -> bool:
    """
    回傳是否允許執行（True = 放行, False = 阻擋）
    """
    return get_guardian_level() >= required_level
# Guardian 狀態橋接檢查（完整版・最終封頂）

# ❌ 不做股票分析

# ❌ 不寫 Vault

# ❌ 不發 Discord

# ✅ 只讀 Guardian 狀態

# ✅ 供 Orchestrator / Stock-Genius 查詢

# ✅ 支援未來多 AI 共識 / 約制擴充



import os

import json

from datetime import datetime, timedelta



VAULT_ROOT = r"E:\Quant-Vault"

GUARDIAN_STATE_PATH = os.path.join(

    VAULT_ROOT,

    "LOCKED_DECISION",

    "guardian",

    "guardian_state.json"

)



# === 預設 Guardian 安全狀態（當檔案不存在時）===

DEFAULT_STATE = {

    "freeze": False,

    "level": "L0",

    "reason": None,

    "updated_at": None

}



# === 冷卻保護（防止狀態抖動）===

FREEZE_MAX_AGE_MINUTES = 180  # 超過 3 小時視為過期，自動解凍





def _load_guardian_state() -> dict:

    """

    只讀 Guardian 狀態檔

    """

    if not os.path.exists(GUARDIAN_STATE_PATH):

        return DEFAULT_STATE.copy()



    try:

        with open(GUARDIAN_STATE_PATH, "r", encoding="utf-8") as f:

            data = json.load(f)

            return {**DEFAULT_STATE, **data}

    except Exception:

        # 任何解析錯誤，回退安全狀態

        return DEFAULT_STATE.copy()





def _is_freeze_expired(state: dict) -> bool:

    """

    檢查 freeze 是否過期（防止永久鎖死）

    """

    if not state.get("freeze"):

        return False



    ts = state.get("updated_at")

    if not ts:

        return False



    try:

        updated = datetime.fromisoformat(ts)

    except Exception:

        return False



    return datetime.now() - updated > timedelta(minutes=FREEZE_MAX_AGE_MINUTES)





def guardian_freeze_check() -> dict:

    """

    🔒 Guardian 狀態檢查（對外唯一入口）



    回傳格式固定，不可擴權：

    {

        "freeze": bool,

        "level": str,

        "reason": str | None,

        "source": "guardian",

        "checked_at": ISO8601

    }

    """

    state = _load_guardian_state()



    # 若 freeze 過期，自動視為解除（不回寫，只影響判斷）

    if _is_freeze_expired(state):

        return {

            "freeze": False,

            "level": state.get("level", "L0"),

            "reason": "freeze_expired_auto_release",

            "source": "guardian",

            "checked_at": datetime.now().isoformat()

        }



    return {

        "freeze": bool(state.get("freeze")),

        "level": state.get("level", "L0"),

        "reason": state.get("reason"),
