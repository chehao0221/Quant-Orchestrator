# ai_us_post.py

# ===== Root 注入（鐵律）=====
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import bootstrap  # noqa

# ===== 正式程式 =====
from vault.backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message


def post_us_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="US", days=days)
    content = format_backtest_section(stats)
    send_market_message(
        webhook="DISCORD_WEBHOOK_US",
        fingerprint=f"US_BACKTEST_{days}D",
        content=content
    )


if __name__ == "__main__":
    post_us_backtest_report()
