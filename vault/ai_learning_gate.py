# AI 學習治理閘門（P3-3 最終封頂版）
# ✅ 無硬編碼路徑
# ✅ 僅允許此檔觸發學習
# ✅ Guardian / 命中率 / 信心過高 交叉約制
# ✅ 可永續自我校正，無需再改

import os
import json
from datetime import datetime, timedelta

from shared.runtime_config import (
    get_learning_state_path,
    get_learning_policy,
)
from shared.guardian_state import get_guardian_level
from vault.vault_ai_judge import update_ai_weights


# =========================
# State I/O
# =========================
def _load_learning_state() -> dict:
    path = get_learning_state_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_learning_state(state: dict):
    path = get_learning_state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# =========================
# Learning Gate（核心）
# =========================
def can_learn(
    market: str,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float,
) -> (bool, str):
    """
    P3-3 學習准入判斷（唯一標準）
    """

    policy = get_learning_policy()

    # 1️⃣ Guardian 約制
    guardian_level = get_guardian_level()
    if guardian_level >= policy["guardian_block_level"]:
        return False, f"Guardian L{guardian_level} 阻擋學習"

    # 2️⃣ 樣本數門
    if sample_size < policy["min_sample_size"]:
        return False, f"樣本不足 ({sample_size})"

    # 3️⃣ 冷卻門
    state = _load_learning_state()
    last = state.get(market, {}).get("last_learned")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.now() - last_dt < timedelta(days=policy["cooldown_days"]):
            return False, "學習冷卻中"

    # 4️⃣ 信心過高但命中下降 → 禁止學習
    if avg_confidence >= policy["max_confidence_allow"] and hit_rate < policy["min_hitrate_allow"]:
        return False, "信心過高且命中不足，觸發自我約制"

    return True, "允許學習"


# =========================
# 唯一學習入口
# =========================
def gated_update_ai_weights(
    market: str,
    summary: dict,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float,
) -> bool:
    """
    🚨 系統唯一允許呼叫 update_ai_weights 的入口
    """

    allowed, _ = can_learn(
        market=market,
        sample_size=sample_size,
        avg_confidence=avg_confidence,
        hit_rate=hit_rate,
    )

    if not allowed:
        return False

    update_ai_weights(market, summary)

    # 記錄學習時間
    state = _load_learning_state()
    state.setdefault(market, {})
    state[market]["last_learned"] = datetime.now().isoformat()
    _save_learning_state(state)

    return True
