# 日股 AI 最終預測與系統審計發送器（封頂最終版）

from datetime import datetime
from vault_root_guard import assert_vault_ready
from orchestrator.orchestrator_ai import OrchestratorAI
from guardian_bridge import fetch_guardian_state
from vault_ai_judge import vault_feedback
from news_radar import analyze_news
from discord_system_notifier import send_system_message, send_market_message
from fingerprint import should_send

DISCORD_GENERAL = "DISCORD_WEBHOOK_GENERAL"
DISCORD_MARKET = "DISCORD_WEBHOOK_JP"
MARKET = "JP"

assert_vault_ready(DISCORD_GENERAL)


def main():
    guardian = fetch_guardian_state()
    if guardian is None:
        return

    market_result = analyze_news(market=MARKET)
    if not market_result:
        return

    vault_result = vault_feedback(market=MARKET)

    orchestrator = OrchestratorAI()
    orchestrator.ingest("guardian", guardian)
    orchestrator.ingest("market", market_result)
    orchestrator.ingest("vault", vault_result)

    final = orchestrator.finalize()

    fingerprint = f"{MARKET}_{datetime.utcnow().date()}"
    if not should_send(fingerprint):
        return

    send_system_message(
        webhook=DISCORD_GENERAL,
        fingerprint=fingerprint,
        content=final
    )

    send_market_message(
        webhook=DISCORD_MARKET,
        fingerprint=fingerprint,
        content=final
    )


if __name__ == "__main__":
    main()
