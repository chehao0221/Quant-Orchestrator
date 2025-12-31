# --- Orchestrator Root 注入（修正版：向上追溯至專案根目錄） ---
import sys
from pathlib import Path

# 這裡設定向上跳三層，直到回到 E:\QuantProject 根目錄
# 這樣 Python 才能找到 backtest_stats_builder 和 utils
ORCH_ROOT = Path(__file__).resolve().parents[3] 
if str(ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(ORCH_ROOT))
# ----------------------------

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
