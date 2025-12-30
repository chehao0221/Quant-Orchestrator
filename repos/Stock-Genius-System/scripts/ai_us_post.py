import os
from datetime import datetime, time
import pytz

from vault_root_guard import assert_vault_ready
from system_state import has_sent, mark_sent
from guardian_state import read_guardian_level
from news_radar import load_news_weight
from performance_discord_report import send_stock_report

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_US")
TZ = pytz.timezone("America/New_York")
MARKET = "US"


def main():
    assert_vault_ready(DISCORD_WEBHOOK)

    now = datetime.now(TZ)

    # 美股：16:00 收盤 → +1h = 17:00
    if now.time() < time(17, 0):
        return

    fingerprint = f"{MARKET}_{now.date()}"
    if has_sent(fingerprint):
        return

    if not data_ready():
        send_stock_report(
            webhook=DISCORD_WEBHOOK,
            market=MARKET,
            content="資料失敗 / 未開市"
        )
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
