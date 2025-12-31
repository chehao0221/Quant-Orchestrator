# ===== 強制診斷區（請勿刪）=====
import os
import sys
from pathlib import Path

print("===== DEBUG START =====")
print("CWD:", os.getcwd())
print("__file__:", __file__)

p = Path(__file__).resolve()
for i, parent in enumerate(p.parents):
    print(f"parent[{i}]:", parent)

print("FILES IN parent[3]:")
try:
    for f in p.parents[3].iterdir():
        print(" -", f.name)
except Exception as e:
    print("ERROR listing parent[3]:", e)

print("===== DEBUG END =====")

# ⚠️ 直接中斷，避免後面 import
raise SystemExit(99)

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
