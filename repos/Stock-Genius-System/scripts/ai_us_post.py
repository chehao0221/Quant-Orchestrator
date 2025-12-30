"""
美股 AI 最終預測與系統審計發送器（封頂最終版）

與 ai_tw_post.py 完全對稱，僅市場不同
"""

import os
from datetime import datetime
from typing import List, Dict, Any

from system_state import load_guardian_state
from news_radar import collect_news_signal
from vault_ai_judge import judge
from vault_root_guard import assert_vault_ready
from ai_decision_audit_report import build_audit_report
from discord_system_notifier import send_system_message


# Discord（系統 / 一般頻道）
DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")


def _data_ready_check(stock_pool: List[dict], indicators: Dict[str, Any]) -> bool:
    if not stock_pool:
        return False
    if not indicators:
        return False
    return True


def run_ai_us_post(
    stock_pool: List[dict],
    indicators: Dict[str, Any],
    ai_council_messages: List[str]
) -> Dict[str, Any] | None:
    """
    美股 AI 主流程入口
    """

    # 🔒 Fail Fast：Vault 必須存在
    assert_vault_ready(DISCORD_WEBHOOK_GENERAL)

    guardian_state = load_guardian_state()
    guardian_level = guardian_state.get("level", -1)

    # 1️⃣ 防止無資料卻給結論
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
            webhook=DISCORD_WEBHOOK_GENERAL,
            fingerprint=audit["fingerprint"],
            content=audit["text"]
        )
        return None

    # 2️⃣ 新聞 / 消息面
    news_signal = collect_news_signal(market="US")

    # 3️⃣ AI Judge
    judge_input = {
        "stocks": stock_pool,
        "indicators": indicators,
        "news": news_signal,
        "guardian_level": guardian_level
    }

    judge_result = judge(judge_input)

    # 4️⃣ AI 決策審計
    audit = build_audit_report(
        market="US",
        guardian_state=guardian_state,
        judge_result=judge_result,
        bridge_messages=ai_council_messages
    )

    # 5️⃣ Discord（系統 / 一般頻道）
    send_system_message(
        webhook=DISCORD_WEBHOOK_GENERAL,
        fingerprint=audit["fingerprint"],
        content=audit["text"]
    )

    return judge_result
