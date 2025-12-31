# guardian_state.py
# Guardian 狀態管理器（封頂最終版）
# 職責：
# - 提供全系統統一的 Guardian 風險等級
# - 控制顯示 / 噪音抑制（L3 以下不對外顯示）
# - 作為所有學習 / 共識 / 發文的唯一風險來源
# ❌ 不分析市場 ❌ 不寫 Vault ❌ 不發 Discord

from typing import Dict

# =================================================
# Guardian 等級鐵律
# =================================================
# L0–L2：正常 / 輕微波動（不顯示）
# L3：警戒
# L4：高風險（阻斷學習）
# L5：系統級危機（全面封鎖）

_DISPLAY_THRESHOLD = 3      # L3 以下不顯示（你已確認）
_BLOCK_LEARNING_LEVEL = 4   # ≥ L4 禁止學習
_MAX_LEVEL = 5

# =================================================
# 內部狀態（由 Guardian 系統實際回填）
# =================================================

_GUARDIAN_STATE: Dict[str, int] = {
    "level": 0
}

# =================================================
# 對外 API
# =================================================

def set_guardian_level(level: int) -> None:
    """
    僅 Guardian 系統可呼叫
    """
    if level < 0:
        level = 0
    if level > _MAX_LEVEL:
        level = _MAX_LEVEL
    _GUARDIAN_STATE["level"] = level


def get_guardian_level() -> int:
    """
    全系統統一讀取入口
    """
    return int(_GUARDIAN_STATE.get("level", 0))


def is_learning_blocked() -> bool:
    """
    Learning Gate 專用
    """
    return get_guardian_level() >= _BLOCK_LEARNING_LEVEL


def should_display_status() -> bool:
    """
    UI / Discord / Report 使用
    """
    return get_guardian_level() >= _DISPLAY_THRESHOLD


def export_guardian_status() -> Dict[str, int]:
    """
    對外輸出（不含任何判斷）
    """
    level = get_guardian_level()
    return {
        "level": level,
        "display": level >= _DISPLAY_THRESHOLD,
        "learning_blocked": level >= _BLOCK_LEARNING_LEVEL
    }
