# =========================================================
# 台股 AI 最終預測與系統審計發送器（封頂版）
# 僅負責：分析、判斷、產生報告、發送 Discord
# ❌ 不交易 ❌ 不寫 LOCKED_* ❌ 不碰 Guardian 決策
# =========================================================

import os
from datetime import datetime
from typing import List, Dict

from vault_root_guard import assert_vault_ready
from system_state import is_market_open
from guard_check import guardian_allows_post
from news_radar import get_news_weights
from forecast_observer import build_forecast_snapshot
from performance_snapshot import append_prediction_snapshot
from performance_discord_report import send_discord_report
from stock_weight_engine import calculate_stock_score
from vault_backtest_reader import get_recent_hit_rate

# ---------- Vault / 系統安全檢查 ----------
assert_vault_ready(os.getenv("DISCORD_WEBHOOK_TW"))

# ---------- 常數 ----------
MARKET = "TW"
MAX_TOP = 5
MAX_CORE = 7

# ---------- 核心流程 ----------
def main():
    if not is_market_open(MARKET):
        send_discord_report(
            webhook=os.getenv("DISCORD_WEBHOOK_TW"),
            content="📊 台股 AI 進階預測報告\n\n❌ 今日未開市"
        )
        return

    if not guardian_allows_post():
        return  # Guardian 僅阻擋發送，不影響計算

    hit_rate = get_recent_hit_rate(market=MARKET)
    news_weight = get_news_weights(market=MARKET)

    universe = build_forecast_snapshot(market=MARKET)
    scored: List[Dict] = []

    for stock in universe:
        score, confidence, meta = calculate_stock_score(
            stock=stock,
            market=MARKET,
            news_weight=news_weight,
            hit_rate=hit_rate
        )
        if confidence is None:
            continue  # 無資料不給結論（鐵律）

        scored.append({
            "stock": stock,
            "score": score,
            "confidence": confidence,
            "meta": meta
        })

    # ---------- 排序與選股 ----------
    scored.sort(key=lambda x: x["score"], reverse=True)
    top5 = scored[:MAX_TOP]
    core = scored[:MAX_CORE]

    # ---------- 報告 ----------
    report = build_report(top5, core)

    # ---------- 記錄 Day0 ----------
    append_prediction_snapshot(
        market=MARKET,
        predictions=top5,
        timestamp=datetime.utcnow()
    )

    send_discord_report(
        webhook=os.getenv("DISCORD_WEBHOOK_TW"),
        content=report
    )


def build_report(top5, core):
    lines = []
    lines.append("📊 台股 AI 進階預測報告")
    lines.append("────────────────────")

    lines.append("\n【海選 Top 5】")
    for item in top5:
        emoji = confidence_emoji(item["confidence"])
        lines.append(f"{emoji} {item['stock']}")

    lines.append("\n【核心監控】")
    for item in core:
        emoji = confidence_emoji(item["confidence"])
        lines.append(f"{emoji} {item['stock']}")

    return "\n".join(lines)


def confidence_emoji(conf):
    if conf > 0.6:
        return "🟢"
    if conf >= 0.3:
        return "🟡"
    return "🔴"


if __name__ == "__main__":
    main()
