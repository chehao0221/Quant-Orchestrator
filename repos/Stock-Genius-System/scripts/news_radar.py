# ===== Guardian System Check =====
from guard_check import check_guardian
check_guardian()
# =================================

import os
import random
import requests
from news_buffer import add_news, clean_buffer

WEBHOOK = os.getenv("DISCORD_WEBHOOK_GENERAL")

FIXED_TW = ["2330.TW","2317.TW","2454.TW","2308.TW","2412.TW"]
FIXED_US = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA"]

def send_discord(msg):
    if not WEBHOOK:
        return
    requests.post(WEBHOOK, json={"content": msg}, timeout=10)

def main():
    clean_buffer()

    # 模擬抓到新聞（實務可換 API）
    market = random.choice(["TW", "US"])
    related = random.sample(FIXED_TW if market == "TW" else FIXED_US, 1)
    impact = round(random.uniform(0, 1), 2)
    sentiment = round(random.uniform(-1, 1), 2)

    add_news(market, related, impact, sentiment)

    # 只挑「重要 + 歷史前 5% + 固定股相關」
    if impact >= 0.85:
        send_discord(
            f"📢 重要市場消息（{market}）\n"
            f"相關標的：{','.join(related)}\n"
            f"影響評分：{impact}\n"
            f"情緒：{sentiment}"
        )

if __name__ == "__main__":
    main()
