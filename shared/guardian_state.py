# guardian_state.py
# Guardian 狀態唯一讀取介面（封頂最終版）
# 職責：
# - 提供 Guardian 目前風險等級（L0–L5）
# - 僅讀取狀態，不做任何決策、不發訊息、不寫 Vault
# - 供 Orchestrator / Learning Gate / 共識層使用

import os
import json
from typing import Optional

# Guardian 狀態來源（環境變數指定，不寫死路徑）
GUARDIAN_STATE_PATH = os.environ.get("GUARDIAN_STATE_PATH")


def get_guardian_level(default: int = 0) -> Optional[int]:
    """
    取得 Guardian 目前風險等級
    - 回傳 0–5
    - 若狀態不存在或讀取失敗，回傳 default
    """

    if not GUARDIAN_STATE_PATH:
        return default

    if not os.path.isfile(GUARDIAN_STATE_PATH):
        return default

    try:
        with open(GUARDIAN_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default

    level = data.get("level")
    if isinstance(level, int) and 0 <= level <= 5:
        return level

    return default
