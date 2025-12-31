# ai_us_post.py
# US 市場 AI 發文整合器（最終封頂版）
# 職責：
# - 串接回測統計
# - 組合回測排版
# - 發送 Discord
# ❌ 不計算 ❌ 不學習 ❌ 不改資料

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message


def post_us_backtest_report(webhook_env: str):
    stats = build_backtest_summary(market="US", days=5)
    content = format_backtest_section(stats)

    send_market_message(
        webhook=webhook_env,
        fingerprint="US_BACKTEST_5D",
        content=content
    )
