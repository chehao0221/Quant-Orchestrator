"""
台股 AI 最終預測與系統審計發送器（封頂最終版）

職責：
- 僅負責：分析、AI 判斷、產生人類可讀審計報告、發送 Discord
- ❌ 不交易
- ❌ 不寫 LOCKED_*
- ❌ 不修改 Guardian 狀態
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
    """
    嚴格資料檢查：
    - 無資料 ≠ 給結論
    """
    if not stock_pool:
        return False
    if not indicators:
        return False
    return True


def run_ai_tw_post(
    stock_pool: List[dict],
    indicators: Dict[str, Any],
    ai_council_messages: List[str]
) -> Dict[str, Any] | None:
    """
    台股 AI 主流程入口
    """

    # 🔒 Fail Fast：Vault 必須存在
    assert_vault_ready(DISCORD_WEBHOOK_GENERAL)

    guardian_state = load_guardian_state()
    guardian_level = guardian_state.get("level", -1)

    # 1️⃣ 防止無資料卻給結論
    if not _data_ready_check(stock_pool, indicators):
        audit = build_audit_report(
            market="TW",
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

    # 2️⃣ 新聞 / 消息面（含時間衰退）
    news_signal = collect_news_signal(market="TW")

    # 3️⃣ AI Judge（只判斷「是否發送」與「信心度」）
    judge_input = {
        "stocks": stock_pool,
        "indicators": indicators,
        "news": news_signal,
        "guardian_level": guardian_level
    }

    judge_result = judge(judge_input)

    # 4️⃣ AI 決策審計（人類可讀）
    audit = build_audit_report(
        market="TW",
        guardian_state=guardian_state,
        judge_result=judge_result,
        bridge_messages=ai_council_messages
    )

    # 5️⃣ Discord（系統 / 一般頻道，含防重複）
    send_system_message(
        webhook=DISCORD_WEBHOOK_GENERAL,
        fingerprint=audit["fingerprint"],
        content=audit["text"]
    )

    return judge_result
