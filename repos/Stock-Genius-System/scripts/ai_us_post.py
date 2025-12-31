import sys
import os

# 自動定位專案根目錄 (Quant-Orchestrator)
# 取得目前檔案路徑的向上第三層 (scripts -> repos -> Stock-Genius-System -> Quant-Orchestrator)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 現在可以安全 import 了
from backtest_stats_builder import build_backtest_summary
# ai_us_post.py
from backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from discord_notifier import send_market_message

def post_us_backtest_report(days: int = 5):
    stats = build_backtest_summary(market="US", days=days)
    content = format_backtest_section(stats)
    send_market_message(
        webhook="DISCORD_WEBHOOK_US",
        fingerprint=f"US_BACKTEST_{days}D",
        content=content
    )

if __name__ == "__main__":
    post_us_backtest_report(days=5)
