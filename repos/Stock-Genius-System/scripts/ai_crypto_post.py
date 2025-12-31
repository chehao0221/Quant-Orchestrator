# --- Orchestrator Root 注入 ---
import sys
from pathlib import Path
ORCH_ROOT = Path(__file__).resolve().parents[0]
if str(ORCH_ROOT) not in sys.path: sys.path.insert(0, str(ORCH_ROOT))
# ----------------------------

from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message

def post_crypto_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="CRYPTO", days=days)
    content = format_backtest_section(stats)
    send_market_message(
        webhook="DISCORD_WEBHOOK_CRYPTO",
        fingerprint=f"CRYPTO_BACKTEST_{days}D",
        content=content
    )

if __name__ == "__main__":
    post_crypto_backtest_report(days=5)
