# 日股 AI 最終預測與系統審計發送器（封頂最終版）

from datetime import datetime
from vault_root_guard import assert_vault_ready
from orchestrator.orchestrator_ai import OrchestratorAI
from guardian_bridge import fetch_guardian_state
from vault_ai_judge import vault_feedback
from news_radar import analyze_news
from discord_system_notifier import send_system_message, send_market_message
from fingerprint impimport os
from datetime import datetime, time
import pytz

from vault_root_guard import assert_vault_ready
from system_state import has_sent, mark_sent
from guardian_state import read_guardian_level
from news_radar import load_news_weight
from performance_discord_report import send_stock_report

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_JP")
TZ = pytz.timezone("Asia/Tokyo")
MARKET = "JP"


def main():
    assert_vault_ready(DISCORD_WEBHOOK)

    now = datetime.now(TZ)

    # 日股：15:00 收盤 → +1h = 16:00
    if now.time() < time(16, 0):
        return

    fingerprint = f"{MARKET}_{now.date()}"
    if has_sent(fingerprint):
        return

    if not data_ready():
        send_stock_report(DISCORD_WEBHOOK, MARKET, "資料失敗 / 未開市")
        mark_sent(fingerprint)
        return

    guardian_level = read_guardian_level()
    news_weight = load_news_weight(MARKET)

    report = generate_report(MARKET, guardian_level, news_weight)

    send_stock_report(DISCORD_WEBHOOK, MARKET, report)
    mark_sent(fingerprint)


def data_ready():
    return True


def generate_report(market, guardian_level, news_weight):
    return f"{market} AI 進階預測報告\nGuardian={guardian_level}"


if __name__ == "__main__":
    main()
ort should_send

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
