# learning_orchestrator.py
# 學習編排中樞（P3-3 最終執行層）
# 職責：
# - 串接回測統計 → 學習閘門 → 權重更新
# - 不做市場判斷
# - 不直接寫 Vault 原始資料
# - 嚴格服從 Guardian 與 Learning Gate

from typing import Optional

from vault.backtest_stats_builder import build_backtest_summary
from vault.ai_learning_gate import gated_update_ai_weights


# -------------------------------------------------
# 公開 API（唯一入口）
# -------------------------------------------------

def run_learning_cycle(
    market: str,
    days: int = 5
) -> Optional[bool]:
    """
    market: TW / US / JP / CRYPTO
    days: 回測視窗天數

    回傳：
    - True  : 發生學習或抑制
    - False : 被阻擋
    - None  : 無資料
    """

    summary = build_backtest_summary(
        market=market,
        days=days
    )

    sample_size = summary.get("sample_size", 0)
    if sample_size == 0:
        return None

    avg_confidence = summary.get("avg_confidence", 0.0)
    hit_rate = summary.get("hit_rate", 0.0)

    return gated_update_ai_weights(
        market=market,
        summary=summary,
        sample_size=sample_size,
        avg_confidence=avg_confidence,
        hit_rate=hit_rate
    )
