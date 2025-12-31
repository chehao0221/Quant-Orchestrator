# ai_crypto_post.py
# CRYPTO 市場 AI 發文整合器（最終封頂版）

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message


def post_crypto_backtest_report(webhook_env: str):
    stats = build_backtest_summary(market="CRYPTO", days=5)
    content = format_backtest_section(stats)

    send_market_message(
        webhook=webhook_env,
        fingerprint="CRYPTO_BACKTEST_5D",
        content=content
    )
