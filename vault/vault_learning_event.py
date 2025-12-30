# Quant-Orchestrator/vault/vault_learning_event.py
# 將回測結果轉為 AI 可吸收的學習事件（封頂最終版）

from typing import Dict
from datetime import datetime


def build_learning_event(backtest_result: Dict) -> Dict:
    """
    backtest_result 必須包含：
      - market
      - hit_rate (0~1)
      - avg_error
      - sample_size
    """

    if not backtest_result:
        return {}

    hit_rate = backtest_result.get("hit_rate", 0)
    sample = backtest_result.get("sample_size", 0)

    # 樣本太小，不學習（避免過擬合）
    if sample < 5:
        return {}

    # 轉換為學習訊號
    event = {
        "market": backtest_result.get("market"),
        "timestamp": datetime.utcnow().isoformat(),
        "signal": "positive" if hit_rate >= 0.6 else "negative",
        "strength": round(abs(hit_rate - 0.5) * 2, 2),  # 0~1
        "hit_rate": hit_rate,
        "sample_size": sample,
    }

    return event
