from ai_decision_audit_report import build_audit_report
from discord_system_notifier import send_system_message
from system_state import load_guardian_state
from vault_ai_judge import judge
from ai_council_bridge import AICouncilBridge
import os

DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")

def final_decision_and_audit(market, bridge: AICouncilBridge):
    guardian_state = load_guardian_state()
    judge_result = judge(bridge.collect())

    audit = build_audit_report(
        market=market,
        guardian_state=guardian_state,
        judge_result=judge_result,
        bridge_messages=bridge.collect()
    )

    send_system_message(
        DISCORD_WEBHOOK_GENERAL,
        audit["fingerprint"],
        audit["text"]
    )

    bridge.clear()
    return judge_result
