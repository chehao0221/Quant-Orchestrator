# -*- coding: utf-8 -*-
"""
ai_tw_post.py
最終封頂版（依 Quant-Orchestrator 鐵律）

- 僅負責：台股 AI 分析 + 報告生成 + Discord 發送
- 不交易、不改 Guardian、不越權 Vault
- 顯示格式：100% 鎖定使用者提供的「台股 AI 進階預測報告」範例
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from guard_check import guardian_freeze_check
from news_radar import load_news_score
from safe_yfinance import is_tw_market_open
from system_state import (
    load_system_state,
    save_system_state,
)

from vault_backtest_writer import write_day0_prediction
from vault_backtest_reader import read_day5_result
from vault_backtest_validator import validate_hit_rate

from performance_snapshot import snapshot_equity_curve
from performance_discord_report import send_discord_message


# =========================
# 基本設定（不可改意義）
# =========================

MARKET = "TW"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW")
VAULT_ROOT = Path(r"E:\Quant-Vault")

REPORT_KEY = "TW_AI_REPORT"
CONF_HIGH = 60
CONF_MID = 30


# =========================
# 共用工具（TW / US 對齊）
# =========================

def confidence_to_emoji(conf: float) -> str:
    if conf > CONF_HIGH:
        return "🟢"
    if conf >= CONF_MID:
        return "🟡"
    return "🔴"


def can_send_report(now: datetime, state: dict) -> bool:
    """
    去重規則（跨 workflow / 重跑）
    """
    last = state.get(REPORT_KEY)
    if not last:
        return True
    last_time = datetime.fromisoformat(last)
    return now.date() != last_time.date()


def mark_sent(state: dict, now: datetime):
    state[REPORT_KEY] = now.isoformat()


# =========================
# AI 核心邏輯（不交易）
# =========================

def calculate_confidence(base_score: float, news_score: float, market_penalty: float) -> float:
    """
    AI 判斷核心（可學習參數型）
    """
    score = base_score * 0.7 + news_score * 0.3
    score *= market_penalty
    return max(0, min(100, score))


def build_report_block(title: str, rows: List[str]) -> str:
    block = [title, "-" * 28]
    block.extend(rows)
    block.append("")
    return "\n".join(block)


# =========================
# 主流程
# =========================

def main():
    now = datetime.now()

    # 1️⃣ Guardian freeze 檢查
    if guardian_freeze_check():
        return

    # 2️⃣ 去重檢查
    state = load_system_state()
    if not can_send_report(now, state):
        return

    # 3️⃣ 市場狀態
    if not is_tw_market_open():
        report = (
            "📊 台股 AI 進階預測報告\n"
            "============================\n\n"
            "📌 市場狀態：未開市 / 資料不足\n\n"
            "⚠️ 本日未能取得完整市場資料，系統將於下一個有效交易日重新評估。\n"
        )
        send_discord_message(WEBHOOK, report)
        mark_sent(state, now)
        save_system_state(state)
        return

    # 4️⃣ 新聞權重
    news_score, market_penalty = load_news_score(market=MARKET)

    # 5️⃣ 取得候選股票（既有機制）
    from forecast_observer import get_tw_candidates
    top5, core_watch = get_tw_candidates()

    # 6️⃣ 計算信心度
    top5_rows = []
    predictions = []

    for s in top5:
        conf = calculate_confidence(
            base_score=s["ai_score"],
            news_score=news_score,
            market_penalty=market_penalty
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
            base_score=s["stability_score"],
            news_score=news_score,
            market_penalty=market_penalty
        )
        emoji = confidence_to_emoji(conf)
        core_rows.append(
            f"{emoji} {s['symbol']}｜穩定信心 {conf:.1f}%｜{s['note']}"
        )

    # 7️⃣ 回測（Day0 寫入 / Day5 讀取）
    write_day0_prediction(VAULT_ROOT, MARKET, predictions)
    hit_rate = validate_hit_rate(read_day5_result(VAULT_ROOT, MARKET))

    # 8️⃣ 報告組裝（格式鎖死）
    report = (
        "📊 台股 AI 進階預測報告\n"
        "============================\n\n"
        f"🗓 日期：{now.date().isoformat()}\n\n"
        + build_report_block("【海選 Top 5】", top5_rows)
        + build_report_block("【核心監控】", core_rows)
        + f"📈 近 5 日命中率：{hit_rate:.1f}%\n\n"
        "⚠️ 本報告僅供研究與風險觀測，非任何投資建議。\n"
    )

    # 9️⃣ 發送
    send_discord_message(WEBHOOK, report)

    # 🔟 狀態紀錄
    snapshot_equity_curve(MARKET)
    mark_sent(state, now)
    save_system_state(state)


if __name__ == "__main__":
    main()
