# -*- coding: utf-8 -*-
"""
ai_us_post.py
最終封頂版（與 TW 完全同規格）
"""

import os
from datetime import datetime
from pathlib import Path

from guard_check import guardian_freeze_check
from news_radar import load_news_score
from safe_yfinance import is_us_market_open
from system_state import load_system_state, save_system_state

from vault_backtest_writer import write_day0_prediction
from vault_backtest_reader import read_day5_result
from vault_backtest_validator import validate_hit_rate

from performance_snapshot import snapshot_equity_curve
from performance_discord_report import send_discord_message

from ai_tw_post import (
    confidence_to_emoji,
    calculate_confidence,
    build_report_block,
)

MARKET = "US"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_US")
VAULT_ROOT = Path(r"E:\Quant-Vault")
REPORT_KEY = "US_AI_REPORT"


def main():
    now = datetime.now()

    if guardian_freeze_check():
        return

    state = load_system_state()
    last = state.get(REPORT_KEY)
    if last and datetime.fromisoformat(last).date() == now.date():
        return

    if not is_us_market_open():
        report = (
            "📊 美股 AI 進階預測報告\n"
            "============================\n\n"
            "📌 市場狀態：未開市 / 資料不足\n"
        )
        send_discord_message(WEBHOOK, report)
        state[REPORT_KEY] = now.isoformat()
        save_system_state(state)
        return

    news_score, market_penalty = load_news_score(market=MARKET)

    from forecast_observer import get_us_candidates
    top5, core_watch = get_us_candidates()

    top5_rows = []
    predictions = []

    for s in top5:
        conf = calculate_confidence(
            s["ai_score"], news_score, market_penalty
        )
        emoji = confidence_to_emoji(conf)
        top5_rows.append(
            f"{emoji} {s['symbol']}｜信心度 {conf:.1f}%｜{s['summary']}"
        )
        predictions.append({
            "symbol": s["symbol"],
            "confidence": conf,
            "market": MARKET,
            "date": now.date().isoformat()
        })

    core_rows = []
    for s in core_watch:
        conf = calculate_confidence(
            s["stability_score"], news_score, market_penalty
        )
        emoji = confidence_to_emoji(conf)
        core_rows.append(
            f"{emoji} {s['symbol']}｜穩定信心 {conf:.1f}%｜{s['note']}"
        )

    write_day0_prediction(VAULT_ROOT, MARKET, predictions)
    hit_rate = validate_hit_rate(read_day5_result(VAULT_ROOT, MARKET))

    report = (
        "📊 美股 AI 進階預測報告\n"
        "============================\n\n"
        f"🗓 日期：{now.date().isoformat()}\n\n"
        + build_report_block("【海選 Top 5】", top5_rows)
        + build_report_block("【核心監控】", core_rows)
        + f"📈 近 5 日命中率：{hit_rate:.1f}%\n\n"
        "⚠️ 本報告僅供研究與風險觀測，非任何投資建議。\n"
    )

    send_discord_message(WEBHOOK, report)
    snapshot_equity_curve(MARKET)

    state[REPORT_KEY] = now.isoformat()
    save_system_state(state)


if __name__ == "__main__":
    main()
