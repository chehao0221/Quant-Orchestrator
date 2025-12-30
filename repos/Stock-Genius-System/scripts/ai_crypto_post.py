# 虛擬貨幣 AI 最終預測與系統審計發送器（封頂版）

import os
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT)

from utils.vault_root_guard import assert_vault_ready
from shared.ai_consensus_guard import apply_ai_mutual_restraint
from repos.Stock-Genius-System.scripts.guard_check import guardian_freeze_check
from repos.Stock-Genius-System.scripts.news_radar import load_news_score
from repos.Stock-Genius-System.scripts.safe_yfinance import get_market_snapshot
from repos.Stock-Genius-System.scripts.performance_discord_report import send_report

from config import (
    DISCORD_WEBHOOK_CRYPTO,
    DISCORD_WEBHOOK_GENERAL
)

MARKET = "CRYPTO"


def main():
    assert_vault_ready(DISCORD_WEBHOOK_GENERAL)

    if guardian_freeze_check():
        return

    market_data = get_market_snapshot(MARKET)
    if not market_data:
        send_report(
            webhook=DISCORD_WEBHOOK_CRYPTO,
            title="虛擬貨幣 AI 預測報告",
            content="資料不足"
        )
        return

    ai_scores = {
        "tech_ai": market_data["tech_score"],
        "news_ai": load_news_score(MARKET),
        "pattern_ai": market_data["pattern_score"]
    }

    restraint = apply_ai_mutual_restraint(MARKET, ai_scores)
    final_score = sum(restraint["adjusted_scores"].values()) / len(ai_scores)

    send_report(
        webhook=DISCORD_WEBHOOK_CRYPTO,
        title="📊 虛擬貨幣 AI 進階預測報告",
        content={
            "market": MARKET,
            "confidence": round(final_score, 3),
            "mode": restraint["mode"],
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    main()
