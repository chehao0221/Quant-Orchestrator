# =========================================================
# Stock Weight Engine
# 核心職責：
# - 計算股票最終 AI 分數
# - 套用時間衰退（J）
# - 套用命中率回饋
# - 套用 Guardian 冷卻（僅降權）
# ❌ 不交易 ❌ 不刪資料 ❌ 不寫 LOCKED_*
# =========================================================

import math
from datetime import datetime

from vault_backtest_reader import get_recent_hit_rate
from guardian_state import get_guardian_level, get_guardian_last_trigger_time


# ---------------------------------------------------------
# 🔧 全域參數（K / J / F 最終值）
# ---------------------------------------------------------

# K：AI Panel 權重
WEIGHT_BACKTEST = 0.40
WEIGHT_TIME_DECAY = 0.25
WEIGHT_USAGE = 0.20
WEIGHT_GUARDIAN = 0.15  # 永遠不超過 0.2（鐵律）

# J：時間衰退（基準）
BASE_LAMBDA = 0.015
LAMBDA_MIN = 0.008
LAMBDA_MAX = 0.03

# L4 / L5 冷卻
L4_BASE = 0.6
L5_BASE = 0.8
L_COOLDOWN_MU = 0.12  # 冷卻係數


# ---------------------------------------------------------
# 核心入口
# ---------------------------------------------------------

def calculate_stock_score(stock, market, news_weight, hit_rate=None):
    """
    回傳：
    - score: float
    - confidence: float | None（無資料時）
    - meta: dict（審計用）
    """

    # ---------- 防呆 ----------
    if stock is None:
        return None, None, {}

    if hit_rate is None:
        hit_rate = get_recent_hit_rate(market)

    if hit_rate is None:
        # 無回測資料，不給結論（鐵律）
        return None, None, {}

    # ---------- 技術面 ----------
    tech_score = stock.get("tech_score")
    if tech_score is None:
        return None, None, {}

    # ---------- 新聞面 ----------
    news_score = news_weight.get(stock["symbol"], 0.0)

    # ---------- 命中率回饋 ----------
    backtest_factor = normalize_hit_rate(hit_rate)

    # ---------- 時間衰退（J） ----------
    last_active = stock.get("last_active_date")
    if last_active is None:
        return None, None, {}

    days = (datetime.utcnow() - last_active).days
    lambda_val = adaptive_lambda(hit_rate)
    time_decay = math.exp(-lambda_val * days)

    # ---------- Guardian 冷卻（僅降權） ----------
    guardian_factor = guardian_cooldown_factor()

    # ---------- 綜合計算 ----------
    raw_score = (
        tech_score * 0.6 +
        news_score * 0.4
    )

    final_score = raw_score
    final_score *= (1 + WEIGHT_BACKTEST * backtest_factor)
    final_score *= (1 + WEIGHT_TIME_DECAY * time_decay)
    final_score *= guardian_factor  # 只能 <= 1

    # ---------- 信心度 ----------
    confidence = clamp(final_score / 100.0)

    meta = {
        "tech": tech_score,
        "news": news_score,
        "hit_rate": hit_rate,
        "time_decay": time_decay,
        "guardian_factor": guardian_factor
    }

    return final_score, confidence, meta


# ---------------------------------------------------------
# 🔁 子模組
# ---------------------------------------------------------

def adaptive_lambda(hit_rate):
    """
    命中率越低，忘得越快
    """
    if hit_rate >= 0.6:
        return BASE_LAMBDA * 0.8
    if hit_rate <= 0.4:
        return BASE_LAMBDA * 1.3

    return BASE_LAMBDA


def guardian_cooldown_factor():
    """
    Guardian 只能「降權」，不能加速刪除
    """
    level = get_guardian_level()
    last_trigger = get_guardian_last_trigger_time()

    if level < 4 or last_trigger is None:
        return 1.0

    days = (datetime.utcnow() - last_trigger).days

    if level == 4:
        base = L4_BASE
    else:
        base = L5_BASE

    cooldown = base * math.exp(-L_COOLDOWN_MU * days)

    # 永遠不放大，只能 <= 1
    return min(1.0, max(0.1, cooldown))


def normalize_hit_rate(hit_rate):
    """
    將命中率轉為 -1 ~ +1
    """
    return max(-1.0, min(1.0, (hit_rate - 0.5) * 2))


def clamp(v, low=0.0, high=1.0):
    return max(low, min(high, v))
