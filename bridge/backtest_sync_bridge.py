# backtest_sync_bridge.py
# 回測結果跨系統同步橋（封頂最終版）
# 職責：
# - 將 Quant-Orchestrator 的回測摘要同步給
#   Quant-Guardian-Ultra / Stock-Genius-System
# - 僅負責事件與資料轉發
# ❌ 不計算 ❌ 不排版 ❌ 不學習 ❌ 不決策

from typing import Dict, Any, List

# 下游系統同步接口（約定存在）
from guardian_ultra.sync import sync_backtest_stats as guardian_sync
from stock_genius.sync import sync_backtest_stats as genius_sync


# -------------------------------------------------
# 公開 API
# -------------------------------------------------

def sync_backtest_summary(
    market: str,
    days: int,
    summary: Dict[str, Any]
) -> None:
    """
    將回測摘要同步至所有關聯系統
    """

    payload = {
        "market": market,
        "days": days,
        "summary": summary,
    }

    # Guardian：風險 / 抑制 / 約制用
    guardian_sync(payload)

    # Stock-Genius：策略協調 / 組合調整用
    genius_sync(payload)


# -------------------------------------------------
# 批次工具（給 Orchestrator 使用）
# -------------------------------------------------

def sync_multi_markets(
    summaries: List[Dict[str, Any]]
) -> None:
    """
    summaries: [
        {
            "market": "TW",
            "days": 5,
            "summary": {...}
        },
        ...
    ]
    """

    for item in summaries:
        sync_backtest_summary(
            market=item["market"],
            days=item["days"],
            summary=item["summary"]
        )
