# --- Orchestrator Root 自動定位（封頂最終版）---
import sys
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "backtest_stats_builder.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break
else:
    raise RuntimeError("❌ 找不到 backtest_stats_builder.py（Orchestrator Root 注入失敗）")
# ------------------------------------------------


from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message

def post_tw_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="TW", days=days)
    content = format_backtest_section(stats)
    send_market_message(
        webhook="DISCORD_WEBHOOK_TW",
        fingerprint=f"TW_BACKTEST_{days}D",
        content=content
    )

if __name__ == "__main__":
    post_tw_backtest_report(days=5)
