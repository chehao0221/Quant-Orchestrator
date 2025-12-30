# Quant-Orchestrator/utils/fingerprint.py
# Discord 訊息去重唯一真源（封頂最終版）

import json
import os
import time
from typing import Dict

# 去重時間窗（秒）— 90 分鐘
DEDUP_WINDOW_SECONDS = 90 * 60

# 優先使用 Vault；若 Vault 未掛載，退回本地 TEMP（不影響主流程）
DEFAULT_STATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "shared"
)

FINGERPRINT_FILE = os.path.join(DEFAULT_STATE_DIR, "fingerprints.json")


def _load_state() -> Dict[str, float]:
    if not os.path.exists(FINGERPRINT_FILE):
        return {}
    try:
        with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 檔案毀損時，保守做法：全部視為未發送
        return {}


def _save_state(state: Dict[str, float]) -> None:
    os.makedirs(os.path.dirname(FINGERPRINT_FILE), exist_ok=True)
    with open(FINGERPRINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def should_send(fingerprint: str, now: float | None = None) -> bool:
    """
    判斷是否允許發送訊息
    - True  → 可以發
    - False → 90 分鐘內已發過，不可重複
    """

    if not fingerprint or not isinstance(fingerprint, str):
        # 無效 fingerprint，保守起見禁止發送
        return False

    current_time = now if now is not None else time.time()
    state = _load_state()

    last_sent = state.get(fingerprint)
    if last_sent is not None:
        if current_time - last_sent < DEDUP_WINDOW_SECONDS:
            return False

    # 記錄本次發送時間
    state[fingerprint] = current_time
    _save_state(state)
    return True
