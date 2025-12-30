# =========================================================
# AI Vault Retention Executor（封頂最終版）
#
# 職責：
# - 判斷資料是否進入「可刪除候選」
# - 僅刪除「冷資料」
# - 嚴格遵守 J / F / Guardian 冷卻規則
#
# ❌ 不交易
# ❌ 不碰 LOCKED_*
# ❌ 不直接聽 Guardian 指令
# ❌ 無資料 → 不行動
# =========================================================

import os
from datetime import datetime, timedelta
from typing import Dict, List

from vault_root_guard import assert_vault_ready
from guardian_state import get_guardian_level
from vault_event_store import list_vault_events, delete_vault_event
from vault_backtest_reader import get_recent_hit_rate
from stock_weight_engine import adaptive_lambda

# ---------------------------------------------------------
# 🔐 系統安全檢查
# ---------------------------------------------------------
assert_vault_ready(None)

# ---------------------------------------------------------
# ⚙️ 最終治理參數（封頂）
# ---------------------------------------------------------

MIN_UNUSED_DAYS = 90
MIN_EFFECTIVE_WEIGHT = 0.01
MIN_DECISION_SCORE = 0.7
REQUIRED_WEEKS_CONFIRM = 2

PROTECTED_TYPES = {
    "black_swan",
    "structural_event"
}

# ---------------------------------------------------------
# 核心入口
# ---------------------------------------------------------

def main():
    guardian_level = get_guardian_level()

    # 高風險期，直接禁止刪除（鐵律）
    if guardian_level >= 4:
        return

    hit_rate = get_recent_hit_rate()
    if hit_rate is None:
        return  # 無審計資料，不刪（鐵律）

    events = list_vault_events()
    if not events:
        return

    now = datetime.utcnow()
    deletion_candidates: List[Dict] = []

    for event in events:
        decision = evaluate_event(event, hit_rate, now)
        if decision["eligible"]:
            deletion_candidates.append(decision)

    # -----------------------------------------------------
    # 執行刪除（已二次確認）
    # -----------------------------------------------------
    for d in deletion_candidates:
        delete_vault_event(d["event_id"])


# ---------------------------------------------------------
# 🔍 單筆事件評估
# ---------------------------------------------------------

def evaluate_event(event: Dict, hit_rate: float, now: datetime) -> Dict:
    """
    回傳：
    {
        eligible: bool,
        event_id: str,
        reason: str
    }
    """

    event_id = event.get("id")
    event_type = event.get("type")

    if not event_id or not event_type:
        return _reject(event_id, "invalid_event")

    # ---------- LOCKED / 黑天鵝保護 ----------
    if event_type in PROTECTED_TYPES:
        return _reject(event_id, "protected_type")

    # ---------- 使用時間 ----------
    last_used = event.get("last_used_at")
    if not last_used:
        return _reject(event_id, "no_last_used")

    unused_days = (now - last_used).days
    if unused_days < MIN_UNUSED_DAYS:
        return _reject(event_id, "recently_used")

    # ---------- 權重衰退 ----------
    created_at = event.get("created_at")
    if not created_at:
        return _reject(event_id, "no_created_time")

    age_days = (now - created_at).days
    lambda_val = adaptive_lambda(hit_rate)
    effective_weight = pow(2.71828, -lambda_val * age_days)

    if effective_weight >= MIN_EFFECTIVE_WEIGHT:
        return _reject(event_id, "still_effective")

    # ---------- 歷史確認 ----------
    confirm_weeks = event.get("deletion_confirm_weeks", 0)
    confirm_weeks += 1

    event["deletion_confirm_weeks"] = confirm_weeks

    if confirm_weeks < REQUIRED_WEEKS_CONFIRM:
        return _reject(event_id, "confirming")

    # ---------- 最終分數 ----------
    decision_score = calculate_decision_score(
        unused_days,
        effective_weight,
        hit_rate
    )

    if decision_score < MIN_DECISION_SCORE:
        return _reject(event_id, "score_too_low")

    return {
        "eligible": True,
        "event_id": event_id,
        "reason": "cold_and_unused"
    }


# ---------------------------------------------------------
# 🧠 決策分數
# ---------------------------------------------------------

def calculate_decision_score(unused_days, effective_weight, hit_rate):
    """
    綜合分數 ∈ [0,1]
    """
    usage_factor = min(1.0, unused_days / 180)
    decay_factor = min(1.0, 1 - effective_weight)
    performance_factor = max(0.0, 1 - hit_rate)

    return (
        usage_factor * 0.4 +
        decay_factor * 0.4 +
        performance_factor * 0.2
    )


# ---------------------------------------------------------
# 🧯 Reject Helper
# ---------------------------------------------------------

def _reject(event_id, reason):
    return {
        "eligible": False,
        "event_id": event_id,
        "reason": reason
    }


if __name__ == "__main__":
    main()
