# post_all_backtest_reports_and_sync.py
# 全市場回測 → 學習治理 → 權重同步（封頂最終版）
# 職責：
# - 產生 TW / US / JP / CRYPTO 回測摘要
# - 送出 Discord 報告
# - 將摘要送入 AI Learning Gate（受 Guardian 約束）
# - 觸發權重更新（或反向抑制）
# ❌ 不做原始判斷 ❌ 不硬寫路徑

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message
from vault.ai_learning_gate import gated_update_ai_weights

MARKETS = {
    "TW": "DISCORD_WEBHOOK_TW",
    "US": "DISCORD_WEBHOOK_US",
    "JP": "DISCORD_WEBHOOK_JP",
    "CRYPTO": "DISCORD_WEBHOOK_CRYPTO",
}

DAYS = 5


def run_all(days: int = DAYS) -> None:
    for market, webhook in MARKETS.items():
        # 1️⃣ 建立回測摘要（事實層）
        stats = build_backtest_summary(market=market, days=days)

        # 2️⃣ Discord 報告（顯示層，L3↑ 已在 formatter 控制）
        report = format_backtest_section(stats)
        send_market_message(
            webhook=webhook,
            fingerprint=f"{market}_BACKTEST_{days}D",
            content=report
        )

        # 3️⃣ Learning Gate（治理層）
        gated_update_ai_weights(
            market=market,
            summary={
                "by_indicator": stats.get("by_indicator", {})
            },
            sample_size=stats.get("sample_size", 0),
            avg_confidence=stats.get("avg_confidence", 0.0),
            hit_rate=stats.get("hit_rate", 0.0)
        )


if __name__ == "__main__":
    run_all()
