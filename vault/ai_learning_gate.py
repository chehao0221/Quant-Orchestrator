import os
import json
from datetime import datetime, timedelta

from vault_ai_judge import update_ai_weights
from shared.guardian_state import get_guardian_level

VAULT_ROOT = r"E:\Quant-Vault"

# 學習治理參數（鐵律層）
MIN_SAMPLE_SIZE = 30              # 樣本太少不學
COOLDOWN_DAYS = 5                 # 防止頻繁學歪
BLOCK_LEVEL = 4                   # Guardian >= L4 禁止學習

LEARNING_STATE_PATH = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "horizon",
    "learning_state.json"
)

def _load_learning_state():
    if not os.path.exists(LEARNING_STATE_PATH):
        return {}
    with open(LEARNING_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_learning_state(state: dict):
    os.makedirs(os.path.dirname(LEARNING_STATE_PATH), exist_ok=True)
    with open(LEARNING_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def can_learn(market: str, sample_size: int) -> (bool, str):
    """
    判斷是否允許 AI 進行學習（P3-3 核心）
    """

    # 1️⃣ Guardian 風險門
    guardian_level = get_guardian_level()
    if guardian_level >= BLOCK_LEVEL:
        return False, f"Guardian L{guardian_level} 阻擋學習"

    # 2️⃣ 樣本數門
    if sample_size < MIN_SAMPLE_SIZE:
        return False, f"樣本不足 ({sample_size} < {MIN_SAMPLE_SIZE})"

    # 3️⃣ 冷卻時間門
    state = _load_learning_state()
    last = state.get(market, {}).get("last_learned")

    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.now() - last_dt < timedelta(days=COOLDOWN_DAYS):
            return False, "學習冷卻中"

    return True, "允許學習"

def gated_update_ai_weights(
    market: str,
    summary: dict,
    sample_size: int
) -> bool:
    """
    唯一允許呼叫 update_ai_weights 的入口
    """

    allowed, reason = can_learn(market, sample_size)
    if not allowed:
        return False

    update_ai_weights(market, summary)

    # 記錄學習時間（慢人格）
    state = _load_learning_state()
    state.setdefault(market, {})
    state[market]["last_learned"] = datetime.now().isoformat()
    _save_learning_state(state)

    return True
