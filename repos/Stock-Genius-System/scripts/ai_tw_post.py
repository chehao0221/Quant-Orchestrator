# --- Orchestrator Root 注入（GitHub Actions / 本機 通殺版）---
import os
import sys
from pathlib import Path

# 1️⃣ GitHub Actions / 本機 workspace
root = os.environ.get("GITHUB_WORKSPACE")
if root:
    root_path = Path(root)
else:
    # fallback：本機直接往上找 Quant-Orchestrator
    root_path = Path(__file__).resolve()
    for p in root_path.parents:
        if (p / "backtest_stats_builder.py").exists():
            root_path = p
            break
    else:
        raise RuntimeError("❌ 無法定位 Quant-Orchestrator Root")

if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
# ------------------------------------------------------------



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
