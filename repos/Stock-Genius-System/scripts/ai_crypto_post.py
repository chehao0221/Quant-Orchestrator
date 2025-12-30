import os
from datetime import datetime, time
import pytz

from vault_root_guard import assert_vault_ready
from system_state import has_sent, mark_sent
from news_radar import load_news_weight
from performance_discord_report import send_stock_report

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_CRYPTO")
TZ = pytz.timezone("Asia/Taipei")
MARKET = "CRYPTO"


def main():
    assert_vault_ready(DISCORD_WEBHOOK)

    now = datetime.now(TZ)

    # ❗ 鐵律：只允許 12:00 之後
    if now.time() < time(12, 0):
        return

    fingerprint = f"{MARKET}_{now.date()}"
    if has_sent(fingerprint):
        return

    if not data_ready():
        send_stock_report(DISCORD_WEBHOOK, MARKET, "資料失敗")
        mark_sent(fingerprint)
        return

    news_weight = load_news_weight(MARKET)

    report = generate_report(MARKET, news_weight)

    send_stock_report(DISCORD_WEBHOOK, MARKET, report)
    mark_sent(fingerprint)


def data_ready():
    return True


def generate_report(market, news_weight):
    return f"{market} AI 進階預測報告\n觀測時間=12:00"


if __name__ == "__main__":
    main()
