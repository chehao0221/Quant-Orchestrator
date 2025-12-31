# Quant-Orchestrator/scripts/post_all_backtest_reports.py
# 全市場 5 日回測準確率報告發送器（最終封頂版｜可直接完整覆蓋）
# 職責：
# - 一次產生 TW / US / JP / CRYPTO 回測報告
# - 僅做 orchestration
# ❌ 不計算 ❌ 不排版 ❌ 不學習 ❌ 不寫死路徑

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message


MARKETS = {
    "TW": "DISCORD_WEBHOOK_TW",
    "US": "DISCORD_WEBHOOK_US",
    "JP": "DISCORD_WEBHOOK_JP",
    "CRYPTO": "DISCORD_WEBHOOK_CRYPTO",
}


def post_all_backtest_reports(days: int = 5) -> None:
    for market, webhook in MARKETS.items():
        stats = build_backtest_summary(market=market, days=days)
        content = format_backtest_section(stats)

        send_market_message(
            webhook=webhook,
            fingerprint=f"{market}_BACKTEST_{days}D",
            content=content
        )


if __name__ == "__main__":
    post_all_backtest_reports(days=5)
