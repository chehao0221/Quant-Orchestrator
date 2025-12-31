# backtest_stats_builder.py
# 回測統計彙整器（終極封頂縫合版）
# 職責：
# - 透過時間視窗精準讀取歷史預測（避免樣本擠壓與失真）
# - 統計樣本數、命中率、平均信心
# - 指標級歸因分析（供 AI Learning Gate 使用）
# - 信心分級統計（🟢🟡🔴，供 Discord 報告顯示）
# ❌ 不學習 ❌ 不發送 ❌ 不寫權重 ❌ 不做市場結論

import os
import json
from datetime import date, timedelta
from typing import Dict, Any, Iterator

# =================================================
# 環境（鐵律：不寫死路徑）
# =================================================

VAULT_ROOT = os.environ.get("VAULT_ROOT")
if not VAULT_ROOT:
    raise RuntimeError("VAULT_ROOT 環境變數未設定")


# =================================================
# 內部工具：時間窗回測檔案迭代器
# =================================================

def _iter_backtest_files(market: str, days: int) -> Iterator[str]:
    """
    只讀取指定天數內的回測檔案
    檔名格式預期：SYMBOL_YYYY-MM-DD.json
    """
    base = os.path.join(VAULT_ROOT, "LOCKED_RAW", "backtest", market)
    if not os.path.isdir(base):
        return iter(())

    cutoff = date.today() - timedelta(days=days)

    paths = []
    for fn in os.listdir(base):
        if not fn.endswith(".json"):
            continue
        try:
            _, d_str = fn.rsplit("_", 1)
            file_date = date.fromisoformat(d_str.replace(".json", ""))
        except Exception:
            continue

        if file_date >= cutoff:
            paths.append(os.path.join(base, fn))

    # 排序確保穩定性（新到舊）
    for p in sorted(paths, reverse=True):
        yield p


# =================================================
# 公開 API
# =================================================

def build_backtest_summary(market: str, days: int = 5) -> Dict[str, Any]:
    """
    彙整回測結果（供 Learning Gate / 報告使用）

    回傳結構：
    {
        "sample_size": int,
        "hit_count": int,
        "hit_rate": float,
        "avg_confidence": float,
        "by_indicator": {
            indicator: {"hit": int, "miss": int}
        },
        "by_confidence_band": {
            "high": {"hits": int, "total": int, "rate": float},
            "mid":  {"hits": int, "total": int, "rate": float},
            "low":  {"hits": int, "total": int, "rate": float}
        }
    }
    """

    results: Dict[str, Any] = {
        "sample_size": 0,
        "hit_count": 0,
        "confidence_sum": 0.0,
        "hit_rate": 0.0,
        "avg_confidence": 0.0,
        "by_indicator": {},
        "by_confidence_band": {
            "high": {"hits": 0, "total": 0, "rate": 0.0},  # >= 0.6
            "mid":  {"hits": 0, "total": 0, "rate": 0.0},  # 0.3–0.6
            "low":  {"hits": 0, "total": 0, "rate": 0.0},  # < 0.3
        }
    }

    for path in _iter_backtest_files(market, days):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        pred = data.get("pred")
        actual = data.get("actual")
        confidence = float(data.get("confidence", 0.0))
        indicators = data.get("indicators", ["__global__"])

        if pred is None or actual is None:
            continue

        # 基礎計數
        results["sample_size"] += 1
        results["confidence_sum"] += confidence

        is_hit = (pred == actual)
        if is_hit:
            results["hit_count"] += 1

        # 信心分級
        if confidence >= 0.6:
            band = "high"
        elif confidence >= 0.3:
            band = "mid"
        else:
            band = "low"

        results["by_confidence_band"][band]["total"] += 1
        if is_hit:
            results["by_confidence_band"][band]["hits"] += 1

        # 指標歸因
        for ind in indicators:
            results["by_indicator"].setdefault(ind, {"hit": 0, "miss": 0})
            if is_hit:
                results["by_indicator"][ind]["hit"] += 1
            else:
                results["by_indicator"][ind]["miss"] += 1

    # -------------------------------------------------
    # 最終比例計算
    # -------------------------------------------------

    total = results["sample_size"]
    if total > 0:
        results["hit_rate"] = round(results["hit_count"] / total, 4)
        results["avg_confidence"] = round(results["confidence_sum"] / total, 4)

        for band in results["by_confidence_band"].values():
            if band["total"] > 0:
                band["rate"] = round(band["hits"] / band["total"], 4)

    return results
