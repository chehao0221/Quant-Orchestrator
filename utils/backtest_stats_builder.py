# backtest_stats_builder.py
# 回測統計建構器（最終封頂版）
# 職責：
# - 純統計、純事實
# - 不決策、不學習、不寫 Vault
# - 不知道市場、不知道 AI、不知道 Guardian
# - 作為「互相約制 / 自我反思 / 學習閘門」的唯一數據來源

from typing import Dict, List


def build_learning_stats(trades: List[Dict]) -> Dict:
    """
    將歷史交易結果轉換為學習所需的統計摘要

    trades: List[{
        "confidence": float,   # AI 當時信心值 (0~1)
        "hit": bool            # 是否命中
    }]
    """

    total = len(trades)
    if total == 0:
        return {
            "sample_size": 0,
            "avg_confidence": 0.0,
            "hit_rate": 0.0,
            "by_confidence_band": {}
        }

    hit_count = 0
    confidence_sum = 0.0

    # 信心分級統計（用於過熱判斷 / 約制）
    bands = {
        "high": {"min": 0.6, "hits": 0, "total": 0},
        "mid":  {"min": 0.3, "hits": 0, "total": 0},
        "low":  {"min": 0.0, "hits": 0, "total": 0},
    }

    for t in trades:
        conf = float(t.get("confidence", 0.0))
        hit = bool(t.get("hit", False))

        confidence_sum += conf
        if hit:
            hit_count += 1

        # 分桶（由高到低）
        if conf >= bands["high"]["min"]:
            band = "high"
        elif conf >= bands["mid"]["min"]:
            band = "mid"
        else:
            band = "low"

        bands[band]["total"] += 1
        if hit:
            bands[band]["hits"] += 1

    # 組合輸出（純事實）
    by_band = {}
    for k, v in bands.items():
        if v["total"] == 0:
            rate = 0.0
        else:
            rate = v["hits"] / v["total"]

        by_band[k] = {
            "sample": v["total"],
            "hit_rate": round(rate, 4)
        }

    return {
        "sample_size": total,
        "avg_confidence": round(confidence_sum / total, 4),
        "hit_rate": round(hit_count / total, 4),
        "by_confidence_band": by_band
    }
