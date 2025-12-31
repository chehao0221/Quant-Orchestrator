from vault.backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message

def post_tw_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="JP", days=days)
    content = format_backtest_section(stats)
    send_market_message(
        webhook="DISCORD_WEBHOOK_JP",
        fingerprint=f"JP_BACKTEST_{days}D",
        content=content
    )

if __name__ == "__main__":
    post_tw_backtest_report(days=5)
