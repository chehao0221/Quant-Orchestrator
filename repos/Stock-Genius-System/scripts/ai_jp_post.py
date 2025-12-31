# ai_jp_post.py
# JP 市場 AI 發文整合器（最終封頂版）

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message


def post_jp_backtest_report(webhook_env: str):
    stats = build_backtest_summary(market="JP", days=5)
    content = format_backtest_section(stats)

    send_market_message(
        webhook=webhook_env,
        fingerprint="JP_BACKTEST_5D",
        content=content
    )
