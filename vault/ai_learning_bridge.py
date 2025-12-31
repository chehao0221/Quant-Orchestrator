# AI 學習回饋橋接層
# 職責：將歷史結果轉為「可治理學習輸入」
# ❌ 不做判斷 ❌ 不做決策 ❌ 不改 Guardian

from typing import Dict

from ai_learning_gate import gated_update_ai_weights


def feed_learning_result(
    market: str,
    summary: Dict,
    stats: Dict
) -> bool:
    """
    將回測 / 結算結果送入學習治理層

    summary: 原本要給 update_ai_weights 的結構
    stats: {
        "sample_size": int,
        "avg_confidence": float,
        "hit_rate": float
    }
    """

    sample_size = int(stats.get("sample_size", 0))
    avg_confidence = float(stats.get("avg_confidence", 0.0))
    hit_rate = float(stats.get("hit_rate", 0.0))

    return gated_update_ai_weights(
        market=market,
        summary=summary,
        sample_size=sample_size,
        avg_confidence=avg_confidence,
        hit_rate=hit_rate
    )
