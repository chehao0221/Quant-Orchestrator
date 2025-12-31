# ===== Orchestrator Root 注入（鐵律）=====
import sys
from pathlib import Path

ORCHESTRATOR_ROOT = Path(__file__).resolve().parents[3]
if str(ORCHESTRATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATOR_ROOT))

# ===== 正常 imports =====
from vault.backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message


def post_US_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="US", days=days)
    content = format_backtest_section(stats)

    send_market_message(
        webhook="DISCORD_WEBHOOK_US",
        fingerprint=f"US_BACKTEST_{days}D",
        content=content
    )


if __name__ == "__main__":
    post_US_backtest_report()
