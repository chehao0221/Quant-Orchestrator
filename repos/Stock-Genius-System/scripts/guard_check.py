# repos/Stock-Genius-System/scripts/guard_check.py
# Guardian 等級檢查器（終極封頂最終版｜可直接完整覆蓋）
# 語意鐵律：
# - 數字越大 = 風險越高 = 限制越嚴格
# - 只有 current_level <= max_allowed_level 才「放行」
# - L5 = 最高危機，必定阻擋所有一般流程

from shared.guardian_state import get_guardian_level


def check_guardian(max_allowed_level: int = 1) -> bool:
    """
    Guardian Gate

    回傳：
    True  -> 放行
    False -> 阻擋

    範例：
    - Guardian L0 / L1 + max_allowed_level=1 -> True
    - Guardian L2↑    + max_allowed_level=1 -> False
    - Guardian L5     -> 永遠 False
    """
    current_level = get_guardian_level()

    # 核心鐵律判斷
    return current_level <= max_allowed_level
