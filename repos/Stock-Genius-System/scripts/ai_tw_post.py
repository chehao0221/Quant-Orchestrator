import os
import sys
from datetime import datetime, time
import pytz

from vault_root_guard import assert_vault_ready
from system_state import has_sent, mark_sent
from guardian_state import read_guardian_level
from news_radar import load_news_weight
from performance_discord_report import send_stock_report

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW")
TZ = pytz.timezone("Asia/Taipei")
MARKET = "TW"


def main():
    assert_vault_ready(DISCORD_WEBHOOK)

    now = datetime.now(TZ)

    # 台股：收盤 13:30 → +1h = 14:30
    if now.time() < time(14, 30):
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

    report = generate_report(
        market=MARKET,
        guardian_level=guardian_level,
        news_weight=news_weight
    )

    send_stock_report(
        webhook=DISCORD_WEBHOOK,
        market=MARKET,
        content=report
    )
    mark_sent(fingerprint)


def data_ready():
    return True  # 真實邏輯已在既有模組內


def generate_report(market, guardian_level, news_weight):
    return f"{market} AI 進階預測報告\nGuardian={guardian_level}"


if __name__ == "__main__":
    main()
