# ai_crypto_post.py
# 虛擬貨幣 5 日回測準確率報告發送器（封頂穩定版）
# 職責：
# - 僅 orchestration
# ❌ 不計算 ❌ 不排版 ❌ 不學習

import os
import sys

# -------------------------------------------------
# Bootstrap：注入 Quant-Orchestrator Root
# -------------------------------------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# -------------------------------------------------
# Imports
# -------------------------------------------------
from vault.backtest_stats_builder import build_backtest_summary
from report_backtest_formatter import format_backtest_section
from utils.discord_notifier import send_market_message


def post_crypto_backtest_report(days: int = 5) -> None:
    stats = build_backtest_summary(market="CRYPTO", days=days)
    content = format_backtest_section(stats)

    send_market_message(
        webhook="DISCORD_WEBHOOK_CRYPTO",
        fingerprint=f"CRYPTO_BACKTEST_{days}D",
        content=content
    )


if __name__ == "__main__":
    post_crypto_backtest_report(days=5)
