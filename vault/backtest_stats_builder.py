# backtest_stats_builder.py
# 回測統計彙整器（封頂最終版）
# 職責：
# - 從 Vault 回測結果中產生「學習用統計摘要」
# - 給 ai_learning_gate 使用
# - 不學習、不寫權重、不做市場判斷

import os
import json
from typing import Dict, List

# -------------------------------------------------
# 環境
# -------------------------------------------------

VAULT_ROOT = os.environ.get("VAULT_ROOT")
if not VAULT_ROOT:
    raise RuntimeError("VAULT_ROOT 環境變數未設定")


# -------------------------------------------------
# 工具
# -------------------------------------------------

def _load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------
# 公開 API
# -------------------------------------------------

def build_backtest_summary(
    market: str,
    days: int = 5
) -> Dict:
    """
    market: TW / US / JP / CRYPTO
    days: 回測天數（預設 5）

    回傳結構：
    {
        "sample_size": int,
        "avg_confidence": float,
        "hit_rate": float,
        "by_indicator": {
            indicator: {"hit": int, "miss": int}
        }
    }
    """

    backtest_root = os.path.join(
        VAULT_ROOT,
        "LOCKED_RAW",
        "backtest",
        market
    )

    if not os.path.isdir(backtest_root):
        return {
            "sample_size": 0,
            "avg_confidence": 0.0,
            "hit_rate": 0.0,
            "by_indicator": {}
        }

    files: List[str] = sorted(
        [
            f for f in os.listdir(backtest_root)
            if f.endswith(".json")
        ],
        reverse=True
    )[:days * 50]  # 防止爆量

    total = 0
    hit = 0
    confidence_sum = 0.0
    by_indicator: Dict[str, Dict[str, int]] = {}

    for fname in files:
        try:
            data = _load_json(os.path.join(backtest_root, fname))
        except Exception:
            continue

        pred = data.get("pred")
        actual = data.get("actual")
        indicators = data.get("indicators", [])
        conf = float(data.get("confidence", 0.5))

        if pred is None or actual is None:
            continue

        total += 1
        confidence_sum += conf

        correct = pred == actual
        if correct:
            hit += 1

        for ind in indicators:
            by_indicator.setdefault(ind, {"hit": 0, "miss": 0})
            if correct:
                by_indicator[ind]["hit"] += 1
            else:
                by_indicator[ind]["miss"] += 1

    if total == 0:
        return {
            "sample_size": 0,
            "avg_confidence": 0.0,
            "hit_rate": 0.0,
            "by_indicator": {}
        }

    return {
        "sample_size": total,
        "avg_confidence": round(confidence_sum / total, 4),
        "hit_rate": round(hit / total, 4),
        "by_indicator": by_indicator
    }
