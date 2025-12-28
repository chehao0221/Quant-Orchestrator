import os
import requests
from datetime import datetime

LEVEL_COLOR = {
    "L1": "🟢",
    "L2": "🟡",
    "L3": "🟡",
    "L4": "🔴",
    "L5": "🔴",
}

WEBHOOKS = {
    "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
    "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
    "us": os.getenv("DISCORD_WEBHOOK_US"),
    "tw": os.getenv("DISCORD_WEBHOOK_TW"),
}

class DiscordNotifier:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def _post(self, webhook, content):
        if not webhook:
            if self.debug:
                print("[WARN] Discord Webhook 未設定")
            return
        requests.post(webhook, json={"content": content}, timeout=10)

    def notify(self, level: str, title: str, message: str, channel: str):
        color = LEVEL_COLOR.get(level, "🟡")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        content = f"""{color} **{title}**

{message}

---
⏱ {timestamp}
"""

        self._post(WEBHOOKS.get(channel), content)

    # 專用快捷方法（避免 entrypoint 混亂）
    def guardian_l3(self, message: str):
        self.notify("L3", "Guardian 風控提醒", message, "general")

    def guardian_l4(self, message: str):
        self.notify("L4", "Guardian 黑天鵝警報", message, "black_swan")
