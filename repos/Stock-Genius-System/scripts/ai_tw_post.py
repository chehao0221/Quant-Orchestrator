# --- Orchestrator Root 注入（最強兼容版：自動尋找 Quant-Orchestrator 根目錄） ---
import sys
import os
from pathlib import Path

def setup_path():
    # 取得目前檔案的絕對路徑
    current_path = Path(__file__).resolve()
    
    # 向上尋找名為 "Quant-Orchestrator" 的資料夾作為根目錄
    # 這樣不論資料夾有多深，只要在專案內都能找到
    for parent in current_path.parents:
        if parent.name == "Quant-Orchestrator":
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    
    # 如果找不到(例如在地端沒改名)，則嘗試使用原本的 parents[3] 作為備案
    root = current_path.parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root

ORCH_ROOT = setup_path()
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
