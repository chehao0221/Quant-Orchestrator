# 台股 AI 最終預測與系統審計發送器（封頂版）
# ❌ 不交易 ❌ 不寫 LOCKED_* ❌ 不做 Guardian 決策

import os
import sys
from datetime import datetime

# === 強制修正 Python Root（GitHub / 本機通用）===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT)

from utils.vault_root_guard import assert_vault_ready
from shared.ai_consensus_guard import apply_ai_mutual_restraint
from repos.Stock-Genius-System.scripts.guard_check import guardian_freeze_check
from repos.Stock-Genius-System.scripts.news_radar import load_news_score
from repos.Stock-Genius-System.scripts.safe_yfinance import get_market_snapshot
from repos.Stock-Genius-System.scripts.performance_discord_report import send_report

from config import (
    DISCORD_WEBHOOK_TW,
    DISCORD_WEBHOOK_GENERAL
)

MARKET = "TW"


def main():
    # === 系統安全鐵律 ===
    assert_vault_ready(DISCORD_WEBHOOK_GENERAL)

    if guardian_freeze_check():
        return

    market_data = get_market_snapshot(MARKET)
    if not market_data:
        send_report(
            webhook=DISCORD_WEBHOOK_TW,
            title="台股 AI 預測報告",
            content="資料不足 / 未開市"
        )
        return

    tech_score = market_data["tech_score"]
    news_score = load_news_score(MARKET)
    pattern_score = market_data["pattern_score"]

    ai_scores = {
        "tech_ai": tech_score,
        "news_ai": news_score,
        "pattern_ai": pattern_score
    }

    restraint = apply_ai_mutual_restraint(MARKET, ai_scores)

    final_score = sum(restraint["adjusted_scores"].values()) / len(ai_scores)

    report = {
        "market": MARKET,
        "timestamp": datetime.now().isoformat(),
        "confidence": round(final_score, 3),
        "mode": restraint["mode"]
    }

    send_report(
        webhook=DISCORD_WEBHOOK_TW,
        title="📊 台股 AI 進階預測報告",
        content=report
    )


if __name__ == "__main__":
    main()
