# AI 自我學習與閉環核心
# 路徑：Quant-Orchestrator/vault/vault_ai_learning_loop.py

from vault_backtest_reader import load_backtest_results
from vault_ai_judge import update_ai_weights
from datetime import datetime, timedelta


MIN_SAMPLES = 20   # 避免樣本過少就亂學


def run_learning_loop(market: str):
    """
    真正的 AI 閉環：
    - 只讀 Vault
    - 不寫 LOCKED_RAW
    - 不碰 Guardian
    """

    results = load_backtest_results(market, days=30)
    if len(results) < MIN_SAMPLES:
        return False  # 資料不足，不學

    summary = {
        "hit": 0,
        "miss": 0,
        "by_indicator": {}
    }

    for r in results:
        if r["hit"]:
            summary["hit"] += 1
        else:
            summary["miss"] += 1

        for k, v in r["indicators"].items():
            summary["by_indicator"].setdefault(k, {"hit": 0, "miss": 0})
            if r["hit"]:
                summary["by_indicator"][k]["hit"] += 1
            else:
                summary["by_indicator"][k]["miss"] += 1

    update_ai_weights(market, summary)
    return True
