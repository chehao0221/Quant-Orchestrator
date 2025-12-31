# ai_learning_gate.py
# AI 學習治理閘門（終極封頂版）
# 職責：
# - 控制是否允許學習
# - 防止信心過熱 / 學歪
# - 反向抑制（互相約制）
# - 與 Guardian 狀態閉環協作
# ❌ 不做市場判斷 ❌ 不發文 ❌ 不直接產生結論

import os
import json
from datetime import datetime, timedelta
from typing import Tuple

from vault.vault_ai_judge import update_ai_weights
from shared.guardian_state import (
    get_guardian_level,
    is_learning_blocked
)

# =================================================
# Vault Root（鐵律：實體 Vault）
# =================================================
VAULT_ROOT = r"E:\Quant-Vault"

# =================================================
# 學習治理鐵律參數
# =================================================
MIN_SAMPLE_SIZE = 30          # 樣本不足不學
COOLDOWN_DAYS = 5             # 學習冷卻
CONF_OVERHEAT = 0.7           # 平均信心過熱
HITRATE_FLOOR = 0.45          # 命中率下限
MAX_SHRINK = 0.15             # 最大反向抑制幅度

# =================================================
# 狀態紀錄（僅紀錄，不做判斷）
# =================================================
LEARNING_STATE_PATH = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "horizon",
    "learning_state.json"
)

# -------------------------------------------------

def _load_state() -> dict:
    if not os.path.exists(LEARNING_STATE_PATH):
        return {}
    with open(LEARNING_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(LEARNING_STATE_PATH), exist_ok=True)
    with open(LEARNING_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# -------------------------------------------------

def can_learn(
    market: str,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float
) -> Tuple[bool, str]:
    """
    判斷是否允許學習（含 Guardian / 過熱抑制）
    """

    # 1️⃣ Guardian 閘門（最高優先）
    if is_learning_blocked():
        return False, f"GUARDIAN_BLOCK_L{get_guardian_level()}"

    # 2️⃣ 樣本數不足
    if sample_size < MIN_SAMPLE_SIZE:
        return False, "INSUFFICIENT_SAMPLE"

    # 3️⃣ 冷卻時間
    state = _load_state()
    last = state.get(market, {}).get("last_learned")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.utcnow() - last_dt < timedelta(days=COOLDOWN_DAYS):
            return False, "COOLDOWN_ACTIVE"

    # 4️⃣ 信心過熱 × 命中率下滑
    if avg_confidence >= CONF_OVERHEAT and hit_rate < HITRATE_FLOOR:
        return False, "CONFIDENCE_OVERHEAT"

    return True, "ALLOW"

# -------------------------------------------------

def gated_update_ai_weights(
    market: str,
    summary: dict,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float
) -> bool:
    """
    唯一合法權重更新入口（含反向抑制）
    """

    allowed, reason = can_learn(
        market=market,
        sample_size=sample_size,
        avg_confidence=avg_confidence,
        hit_rate=hit_rate
    )

    state = _load_state()
    state.setdefault(market, {})
    state[market]["last_check"] = datetime.utcnow().isoformat()
    state[market]["last_reason"] = reason

    # ❌ 不允許學習
    if not allowed:
        if reason == "CONFIDENCE_OVERHEAT":
            # 反向抑制：全域降權（互相約制）
            shrink = min(MAX_SHRINK, CONF_OVERHEAT - hit_rate)
            update_ai_weights(
                market,
                {
                    "by_indicator": {
                        "__global__": {
                            "hit": 0,
                            "miss": int(shrink * 100)
                        }
                    }
                }
            )
            state[market]["last_action"] = "SHRINK"
        else:
            state[market]["last_action"] = "BLOCKED"

        _save_state(state)
        return False

    # ✅ 正向學習
    update_ai_weights(market, summary)
    state[market]["last_learned"] = datetime.utcnow().isoformat()
    state[market]["last_action"] = "LEARNED"
    _save_state(state)

    return True
