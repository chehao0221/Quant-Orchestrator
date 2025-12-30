import json
import os
from datetime import datetime, timedelta
from math import exp

VAULT_ROOT = r"E:\Quant-Vault"

# === 參數（鐵律級，只能微調數值，不改邏輯）===
CONF_HIGH_THRESHOLD = 0.65        # 高信心門檻
MIN_SAMPLES = 20                 # 最低樣本數
HALF_LIFE_DAYS = 30               # 時間衰退半衰期
MAX_COMPRESSION = 0.25            # 最大壓縮比例（最多降 25%）
AI_PENALTY_STEP = 0.05            # 單次 AI 權重下調上限


def _decay_weight(days: int) -> float:
    """時間衰退權重"""
    return exp(-days / HALF_LIFE_DAYS)


def _load_backtest_summary(market: str) -> dict:
    """
    從 Vault 彙總回測結果
    """
    path = os.path.join(
        VAULT_ROOT,
        "LOCKED_RAW",
        "backtest",
        market,
        "summary.json"
    )
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_confidence_divergence(market: str) -> dict:
    """
    判斷是否出現「信心過高但命中率下降」
    """
    summary = _load_backtest_summary(market)
    if not summary or summary.get("samples", 0) < MIN_SAMPLES:
        return {"active": False}

    avg_conf = summary.get("avg_confidence", 0)
    hit_rate = summary.get("hit_rate", 0)

    divergence = avg_conf - hit_rate

    active = (
        avg_conf > CONF_HIGH_THRESHOLD and
        divergence > 0.1
    )

    return {
        "active": active,
        "avg_confidence": avg_conf,
        "hit_rate": hit_rate,
        "divergence": divergence
    }


def compute_confidence_compression(divergence: float) -> float:
    """
    計算信心壓縮比例（0~MAX_COMPRESSION）
    """
    compression = min(divergence, MAX_COMPRESSION)
    return round(1.0 - compression, 3)


def apply_ai_mutual_restraint(market: str, ai_scores: dict) -> dict:
    """
    AI 互相約制主入口
    - 不 veto
    - 不刪股票
    - 不改規則
    - 只降躁、降權
    """
    eval_result = evaluate_confidence_divergence(market)
    if not eval_result.get("active"):
        return {
            "mode": "normal",
            "adjusted_scores": ai_scores,
            "note": "no_restraint"
        }

    compression = compute_confidence_compression(
        eval_result["divergence"]
    )

    adjusted = {}
    for ai, score in ai_scores.items():
        adjusted[ai] = round(score * compression, 4)

    return {
        "mode": "restrained",
        "compression": compression,
        "adjusted_scores": adjusted,
        "avg_confidence": eval_result["avg_confidence"],
        "hit_rate": eval_result["hit_rate"]
    }
