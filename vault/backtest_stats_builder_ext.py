# backtest_stats_builder_ext.py
# 回測統計擴充分析器（終極封頂版）
#
# 職責：
# - 嚴格以「時間視窗」讀取回測事實（避免樣本失真）
# - 提供 Discord 報告用統計
# - 提供 AI 共識 / 約制層使用
#
# ❌ 不更新權重
# ❌ 不做學習決策
# ❌ 不影響 Learning Gate

import os
import json
from datetime import date, timedelta
from typing import Dict, Any, Iterator

# -------------------------------------------------
# 環境（鐵律：不寫死）
# -------------------------------------------------

VAULT_ROOT = os.environ.get("VAULT_ROOT")
if not VAULT_ROOT:
    raise RuntimeError("VAULT_ROOT 環境變數未設定")

# -------------------------------------------------
# 內部工具：時間視窗精準讀取
# -------------------------------------------------

def _iter_backtest_files(market: str, days: int) -> Iterator[str]:
    base = os.path.join(VAULT_ROOT, "LOCKED_RAW", "backtest", market)
    if not os.path.isdir(base):
        return

    cutoff = date.today() - timedelta(days=days)

    for fn in os.listdir(base):
        if not fn.endswith(".json"):
            continue

        try:
            # 檔名格式：symbol_YYYY-MM-DD.json
            _, d = fn.rsplit("_", 1)
            file_date = date.fromisoformat(d.replace(".json", ""))
        except Exception:
            continue

        if file_date < cutoff:
            continue

        yield os.path.join(base, fn)

# -------------------------------------------------
# 公開 API
# -------------------------------------------------

def build_backtest_summary_ext(
    market: str,
    days: int = 5
) -> Dict[str, Any]:
    """
    擴充型回測統計（給報告 / AI 共識用）
    """

    result = {
        "sample_size": 0,
        "hit_count": 0,
        "hit_rate": 0.0,
        "avg_confidence": 0.0,

        # 🟢🟡🔴 專用
        "by_confidence_band": {
            "high": {"hits": 0, "total": 0, "rate": 0.0},  # >= 0.6
            "mid":  {"hits": 0, "total": 0, "rate": 0.0},  # 0.3–0.6
            "low":  {"hits": 0, "total": 0, "rate": 0.0},  # < 0.3
        },

        # 指標歸因（供 AI 約制 / 共識）
        "by_indicator": {}
    }

    confidence_sum = 0.0

    for path in _iter_backtest_files(market, days):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        pred = data.get("pred")
        actual = data.get("actual")
        conf = float(data.get("confidence", 0.0))
        indicators = data.get("indicators", ["__global__"])

        if pred is None or actual is None:
            continue

        result["sample_size"] += 1
        confidence_sum += conf

        is_hit = (pred == actual)
        if is_hit:
            result["hit_count"] += 1

        # ---------- 信心分級 ----------
        if conf >= 0.6:
            band = "high"
        elif conf >= 0.3:
            band = "mid"
        else:
            band = "low"

        band_ref = result["by_confidence_band"][band]
        band_ref["total"] += 1
        if is_hit:
            band_ref["hits"] += 1

        # ---------- 指標歸因 ----------
        for ind in indicators:
            result["by_indicator"].setdefault(ind, {"hit": 0, "miss": 0})
            if is_hit:
                result["by_indicator"][ind]["hit"] += 1
            else:
                result["by_indicator"][ind]["miss"] += 1

    total = result["sample_size"]
    if total > 0:
        result["hit_rate"] = round(result["hit_count"] / total, 4)
        result["avg_confidence"] = round(confidence_sum / total, 4)

        for band in result["by_confidence_band"].values():
            if band["total"] > 0:
                band["rate"] = round(band["hits"] / band["total"], 4)

    return result
