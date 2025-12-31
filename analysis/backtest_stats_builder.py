# 回測結算統計產生器（最終封頂版）
# 職責：從歷史交易結果中萃取「學習治理所需統計」
# ❌ 不判斷 ❌ 不學習 ❌ 不接觸 Guardian
# ✅ 僅做事實統計（可重算、可驗證）

from typing import List, Dict


def build_learning_stats(trades: List[Dict]) -> Dict:
    """
    trades: [
        {
            "confidence": float,   # 當時信心度 0~1
            "hit": bool            # 是否命中
        },
        ...
    ]
    """

    sample_size = len(trades)
    if sample_size == 0:
        return {
            "sample_size": 0,
            "avg_confidence": 0.0,
            "hit_rate": 0.0
        }

    total_conf = 0.0
    hit_count = 0

    for t in trades:
        conf = float(t.get("confidence", 0.0))
        hit = bool(t.get("hit", False))

        total_conf += conf
        if hit:
            hit_count += 1

    avg_confidence = total_conf / sample_size
    hit_rate = hit_count / sample_size

    return {
        "sample_size": sample_size,
        "avg_confidence": round(avg_confidence, 4),
        "hit_rate": round(hit_rate, 4)
    }
