# --- Quant-Orchestrator Root 強制注入（最終封頂版）---
import sys
from pathlib import Path

# ai_tw_post.py
# repos/Stock-Genius-System/scripts/ai_tw_post.py
# → Orchestrator root = parents[3]

ORCHESTRATOR_ROOT = Path(__file__).resolve().parents[3]

if not (ORCHESTRATOR_ROOT / "backtest_stats_builder.py").exists():
    raise RuntimeError(
        f"❌ Orchestrator Root 定位失敗：{ORCHESTRATOR_ROOT}"
    )

sys.path.insert(0, str(ORCHESTRATOR_ROOT))
# ----------------------------------------------------



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
