# post_tw_report.py
from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message

def post_tw_backtest_report(days: int = 5) -> bool:
    stats = build_backtest_summary(market="TW", days=days)
    report = format_backtest_section(stats)
    return send_market_message(
        webhook="DISCORD_WEBHOOK_TW",
        fingerprint=f"TW_BACKTEST_{days}D",
        content=report
    )

if __name__ == "__main__":
    post_tw_backtest_report()
