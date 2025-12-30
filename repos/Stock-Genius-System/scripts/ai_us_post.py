# 美股 AI 最終預測與系統審計發送器（封頂最終版）
# ❌ 不交易 ❌ 不寫 LOCKED_* ❌ 不碰 Guardian 決策

import os
import json
import hashlib
from datetime import datetime

from vault_root_guard import assert_vault_ready
from vault_executor import execute_snapshot, execute_event
from system_state import load_state, save_state
from notifier import send_discord_message
from news_radar import get_news_weight
from performance_snapshot import build_performance_snapshot

# ========= Vault / Discord 檢查 =========
assert_vault_ready(os.getenv("DISCORD_WEBHOOK_GENERAL"))

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_US")
MARKET = "US"


def ai_analyzer(data: dict) -> dict:
    if not data:
        return {"ok": False, "reason": "NO_DATA"}
    return {"ok": True, "score": data["score"]}


def ai_auditor(result: dict) -> dict:
    if not result.get("ok"):
        return {"ok": False}
    if result["score"] < 0.3:
        return {"ok": False}
    return {"ok": True}


def ai_arbiter(analysis: dict, audit: dict) -> dict:
    return {"final": analysis["ok"] and audit["ok"]}


def is_duplicate(content: str) -> bool:
    state = load_state()
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if state.get("last_us_hash") == h:
        return True
    state["last_us_hash"] = h
    save_state(state)
    return False


def main():
    market_data = build_performance_snapshot(MARKET)
    news_weight = get_news_weight(MARKET)

    combined_score = market_data.get("score", 0) * news_weight

    analysis = ai_analyzer({"score": combined_score})
    audit = ai_auditor(analysis)
    decision = ai_arbiter(analysis, audit)

    if not decision["final"]:
        execute_event(
            "us_ai_abort",
            {"time": datetime.utcnow().isoformat()}
        )
        return

    report_text = market_data["report_text"]

    if is_duplicate(report_text):
        return

    execute_snapshot(MARKET, report_text)
    send_discord_message(DISCORD_WEBHOOK, report_text)


if __name__ == "__main__":
    main()
