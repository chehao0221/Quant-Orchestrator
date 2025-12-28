import os
import requests
from datetime import datetime

LEVEL_ICON = {
    "L1": "🟢",
    "L3": "🟡",
    "L4": "🔴",
}

WEBHOOKS = {
    "tw": os.getenv("DISCORD_WEBHOOK_TW"),
    "us": os.getenv("DISCORD_WEBHOOK_US"),
}

def send_message(level: str, title: str, body: str, market: str):
    icon = LEVEL_ICON.get(level, "🟢")
    webhook = WEBHOOKS.get(market)

    if not webhook:
        print(f"[WARN] Discord Webhook 未設定（{market}）")
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    content = f"""{icon} **{title}**

{body}

---
⏱ {timestamp}
"""

    requests.post(
        webhook,
        json={"content": content},
        timeout=10
    )
