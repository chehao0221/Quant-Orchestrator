from vault_root_guard import assert_vault_ready

assert_vault_ready(DISCORD_WEBHOOK_GENERAL)

# 美股 AI 最終預測與系統審計發送器（封頂版）
# 與 TW 完全對稱，僅市場不同

import os
from datetime import datetime

from system_state import load_guardian_state
from news_radar import collect_news_signal
from vault_ai_judge import judge
from ai_decision_audit_report import build_audit_report
from discord_system_notifier import send_system_message

DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")


def _data_ready_check(stock_pool: list, indicators: dict) -> bool:
    if not stock_pool:
        return False
    if not indicators:
        return False
    return True


def run_ai_us_post(
    stock_pool: list,
    indicators: dict,
    ai_council_messages: list
):
    """
    美股最終 AI 流程入口
    """

    guardian_state = load_guardian_state()
    guardian_level = guardian_state.get("level", -1)

    # 1️⃣ 基礎資料檢查（防止無資料卻給結論）
    if not _data_ready_check(stock_pool, indicators):
        audit = build_audit_report(
            market="US",
            guardian_state=guardian_state,
            judge_result={
                "confidence": 0.0,
                "veto": True,
                "reason": "資料不完整 / 未開市"
            },
            bridge_messages=ai_council_messages
        )

        send_system_message(
            DISCORD_WEBHOOK_GENERAL,
            audit["fingerprint"],
            audit["text"]
        )
        return None

    # 2️⃣ 新聞 / 消息權重
    news_signal = collect_news_signal(market="US")

    # 3️⃣ AI Judge
    judge_input = {
        "stocks": stock_pool,
        "indicators": indicators,
        "news": news_signal,
        "guardian_level": guardian_level
    }

    judge_result = judge(judge_input)

    # 4️⃣ AI 決策審計報告
    audit = build_audit_report(
        market="US",
        guardian_state=guardian_state,
        judge_result=judge_result,
        bridge_messages=ai_council_messages
    )

    # 5️⃣ Discord 系統 / 一般頻道（防重複）
    send_system_message(
        DISCORD_WEBHOOK_GENERAL,
        audit["fingerprint"],
        audit["text"]
    )

    return judge_result
