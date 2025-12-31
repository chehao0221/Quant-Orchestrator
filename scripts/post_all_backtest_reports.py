# post_all_backtest_reports.py
# 全市場 5 日回測準確率報告發送器（終極封頂協調版）
# 職責：
# - 產生 TW / US / JP / CRYPTO 回測報告
# - 發送 Discord
# - 同步回測「事實層」至 Guardian / Genius
# ❌ 不計算 ❌ 不排版 ❌ 不學習 ❌ 不做決策

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message
from bridge.backtest_sync_bridge import sync_backtest_summary


MARKETS = {
    "TW": "DISCORD_WEBHOOK_TW",
    "US": "DISCORD_WEBHOOK_US",
    "JP": "DISCORD_WEBHOOK_JP",
    "CRYPTO": "DISCORD_WEBHOOK_CRYPTO",
}


def post_all_backtest_reports(days: int = 5) -> None:
    for market, webhook in MARKETS.items():
        stats = build_backtest_summary(market=market, days=days)

        # 1️⃣ Discord 報告
        report = format_backtest_section(stats)
        send_market_message(
            webhook=webhook,
            fingerprint=f"{market}_BACKTEST_{days}D",
            content=report
        )

        # 2️⃣ 三系統事實同步
        sync_backtest_summary(
            market=market,
            days=days,
            summary=stats
        )


if __name__ == "__main__":
    post_all_backtest_reports(days=5)
