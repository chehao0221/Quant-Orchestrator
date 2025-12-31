# ai_learning_gate.py
# AI 學習治理閘門（最終封頂版｜可直接完整覆蓋）
# 職責：學習是否允許、抑制學歪、閉環紀錄
# ❌ 不寫死路徑 ❌ 不直接學習 ❌ 不產生市場結論

import os
import json
from datetime import datetime, timedelta
from typing import Tuple

from vault_ai_judge import update_ai_weights
from shared.guardian_state import get_guardian_level

# ===== 環境參數（不寫死路徑，鐵律）=====
VAULT_ROOT = os.environ.get("VAULT_ROOT")
if not VAULT_ROOT:
    raise RuntimeError("VAULT_ROOT 環境變數未設定")

# ===== 學習治理鐵律參數 =====
MIN_SAMPLE_SIZE = 30          # 樣本門檻
COOLDOWN_DAYS = 5             # 學習冷卻
BLOCK_LEVEL = 4               # Guardian ≥ L4 禁止學習
CONF_OVERHEAT = 0.7           # 信心過熱門檻
HITRATE_FLOOR = 0.45          # 命中率下限（低於即抑制）
MAX_SHRINK = 0.15             # 反向抑制最大幅度

# ===== 狀態檔（僅記錄，不做決策）=====
LEARNING_STATE_PATH = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "horizon",
    "learning_state.json"
)

# ---------------------------------------------------------------------

def _load_state() -> dict:
    if not os.path.exists(LEARNING_STATE_PATH):
        return {}
    with open(LEARNING_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(LEARNING_STATE_PATH), exist_ok=True)
    with open(LEARNING_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------

def can_learn(
    market: str,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float
) -> Tuple[bool, str]:
    """
    判斷是否允許學習（完整閉環）
    """

    # 1️⃣ Guardian 閘門
    guardian_level = get_guardian_level()
    if guardian_level >= BLOCK_LEVEL:
        return False, f"Guardian_L{guardian_level}_BLOCK"

    # 2️⃣ 樣本數閘門
    if sample_size < MIN_SAMPLE_SIZE:
        return False, "INSUFFICIENT_SAMPLE"

    # 3️⃣ 冷卻閘門
    state = _load_state()
    last = state.get(market, {}).get("last_learned")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.utcnow() - last_dt < timedelta(days=COOLDOWN_DAYS):
            return False, "COOLDOWN_ACTIVE"

    # 4️⃣ 信心過熱 × 命中率下滑 → 禁止正向學習
    if avg_confidence >= CONF_OVERHEAT and hit_rate < HITRATE_FLOOR:
        return False, "CONFIDENCE_OVERHEAT"

    return True, "ALLOW"


# ---------------------------------------------------------------------

def gated_update_ai_weights(
    market: str,
    summary: dict,
    sample_size: int,
    avg_confidence: float,
    hit_rate: float
) -> bool:
    """
    唯一合法學習入口（含反向抑制）
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

    if not allowed:
        # ⚠️ 信心過熱但命中差 → 反向抑制（降權）
        if reason == "CONFIDENCE_OVERHEAT":
            shrink = min(MAX_SHRINK, (CONF_OVERHEAT - hit_rate))
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
