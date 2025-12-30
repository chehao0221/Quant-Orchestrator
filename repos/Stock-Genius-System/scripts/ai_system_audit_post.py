# AI 系統審計 Discord 發送器（不含股票）

import os
from notifier import send_discord_message
from guardian_state_reader import load_guardian_state
from ai_audit_report_builder import build_audit_report
from ai_performance_summary import summarize
from ai_learning_loop import load_weights
from vault_event_store import load_recent_backtests

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_GENERAL")

def main():
    weights = load_weights()
    guardian = load_guardian_state()

    backtests = load_recent_backtests(limit=10)
    perf = summarize(backtests)

    guardian_view = {
        "level": guardian["level"],
        "mode": guardian.get("mode", "NORMAL"),
        "bias": guardian.get("risk_bias", 0)
    }

    report = build_audit_report(weights, perf, guardian_view)
    send_discord_message(DISCORD_WEBHOOK, report)

if __name__ == "__main__":
    main()
