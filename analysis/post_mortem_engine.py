# post_mortem_engine.py
# AI 自我反思與責任歸因引擎（封頂最終版）
# 職責：
# - 分析回測失誤來源
# - 對指標 / AI 模組進行責任歸因
# - 產出「懲罰建議」供 Learning Gate 與 Weight Sync 使用
# ❌ 不直接改權重 ❌ 不產生市場結論

from typing import Dict, Any
from collections import defaultdict


# -------------------------------------------------
# 公開 API
# -------------------------------------------------

def build_post_mortem_report(
    backtest_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """
    將回測統計轉換為反思報告（責任歸因）
    """

    report = {
        "by_indicator": {},
        "global_penalty": 0,
        "reason": ""
    }

    by_indicator = backtest_summary.get("by_indicator", {})
    hit_rate = backtest_summary.get("hit_rate", 0.0)
    avg_conf = backtest_summary.get("avg_confidence", 0.0)

    total_penalty = 0
    reasons = []

    for ind, stat in by_indicator.items():
        hit = stat.get("hit", 0)
        miss = stat.get("miss", 0)
        total = hit + miss

        if total < 5:
            continue  # 樣本太少不歸因

        rate = hit / total
        penalty = 0

        # 命中率低於 45% → 明確失誤來源
        if rate < 0.45:
            penalty = int((0.45 - rate) * 100)
            reasons.append(f"{ind}_UNDERPERFORM")

        if penalty > 0:
            report["by_indicator"][ind] = {
                "hit": hit,
                "miss": miss,
                "penalty": penalty
            }
            total_penalty += penalty

    # 全域過熱檢查（高信心但命中差）
    if avg_conf >= 0.65 and hit_rate < 0.45:
        total_penalty += 15
        reasons.append("GLOBAL_CONFIDENCE_OVERHEAT")

    report["global_penalty"] = total_penalty
    report["reason"] = ",".join(reasons) if reasons else "NORMAL"

    return report
