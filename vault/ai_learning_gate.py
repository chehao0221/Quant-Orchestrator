import os
import json
from datetime import datetime, timedelta

from vault_ai_judge import judge
from shared.guardian_state import get_guardian_level
from shared.runtime_config import (
    get_vault_root,
    get_learning_state_path,
    get_learning_policy,
)

# ==============================
# AI 學習治理閘門（最終封頂版）
# ==============================

# —— 動態載入治理參數（無硬編碼）——
POLICY = get_learning_policy()
MIN_SAMPLE_SIZE = POLICY["min_sample_size"]
COOLDOWN_DAYS = POLICY["cooldown_days"]
BLOCK_LEVEL = POLICY["guardian_block_level"]
MAX_CONFIDENCE = POLICY["max_confidence_allow"]
MIN_HITRATE = POLICY["min_hitrate_allow"]


def _load_learning_state():
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


def can_learn(
    market: str,
    sample_size: int,
    judge_result: dict,
    recent_hitrate: float,
) -> (bool, str):
    """
    AI 是否允許進入學習的唯一判斷入口
    """

    # 1️⃣ Guardian 風險層
    guardian_level = get_guardian_level()
    if guardian_level >= BLOCK_LEVEL:
        return False, f"Guardian L{guardian_level} 阻擋學習"

    # 2️⃣ 樣本數門檻
    if sample_size < MIN_SAMPLE_SIZE:
        return False, f"樣本不足 ({sample_size} < {MIN_SAMPLE_SIZE})"

    # 3️⃣ Judge veto 門
    if judge_result.get("veto"):
        return False, "Judge veto 阻擋學習"

    # 4️⃣ 信心過高但命中不足 → 互相約制
    confidence = judge_result.get("confidence", 0.0)
    if confidence >= MAX_CONFIDENCE and recent_hitrate < MIN_HITRATE:
        return False, "高信心但命中率下降，啟動自我抑制"

    # 5️⃣ 冷卻時間門
    state = _load_learning_state()
    last = state.get(market, {}).get("last_learned")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.now() - last_dt < timedelta(days=COOLDOWN_DAYS):
            return False, "學習冷卻中"

    return True, "允許學習"


def gated_update_ai_weights(
    market: str,
    bridge_messages: list,
    summary: dict,
    sample_size: int,
    recent_hitrate: float,
    update_ai_weights_func,
) -> bool:
    """
    系統內唯一允許 AI 權重更新的入口（不可旁路）
    """

    # 產生最終共識結果
    judge_result = judge(bridge_messages)

    allowed, _ = can_learn(
        market=market,
        sample_size=sample_size,
        judge_result=judge_result,
        recent_hitrate=recent_hitrate,
    )
    if not allowed:
        return False

    # 執行學習
    update_ai_weights_func(market, summary, judge_result)

    # 記錄學習時間（慢人格）
    state = _load_learning_state()
    state.setdefault(market, {})
    state[market]["last_learned"] = datetime.now().isoformat()
    _save_learning_state(state)

    return True
