import sys
import os

# 1. 取得目前腳本的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 向上溯源至 Quant-Orchestrator 根目錄
# 結構：scripts (0) -> repos (1) -> Stock-Genius-System (2) -> Quant-Orchestrator (3)
base_dir = os.path.abspath(os.path.join(current_dir, "../../.."))

# 3. 確保根目錄與其子目錄在搜尋路徑中
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# 4. 如果您的工具放在 shared 資料夾，也一併加入
shared_dir = os.path.join(base_dir, "shared")
if shared_dir not in sys.path:
    sys.path.insert(0, shared_dir)

# 現在可以安全地進行 import
try:
    from backtest_stats_builder import build_backtest_summary
    from shared.report_backtest_formatter import format_backtest_section
except ImportError as e:
    print(f"❌ 路徑對接失敗。目前的 base_dir 是: {base_dir}")
    print(f"❌ 錯誤訊息: {e}")
    sys.exit(1)


# ai_tw_post.py
from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message

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
