import requests
import os
from datetime import datetime

class Notifier:
    def __init__(self):
        self.webhook_general = os.getenv("DISCORD_WEBHOOK_GENERAL")
        self.webhook_black = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

    def _send(self, webhook, title, description, color):
        if not webhook:
            return

        payload = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "footer": {
                    "text": f"Quant-Orchestrator • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                }
            }]
        }
        requests.post(webhook, json=payload, timeout=10)

    def notify(self, level, decision, changed):
        if not changed:
            return

        if decision.level >= 5:
            webhook = self.webhook_black
        else:
            webhook = self.webhook_general

        color_map = {
            "GREEN": 3066993,
            "YELLOW": 15105570,
            "RED": 15158332,
        }

        title = f"Guardian 風控狀態更新：L{decision.level}"
        desc = (
            f"市場狀態：{decision.description}\n"
            f"系統狀態：{'凍結中' if decision.freeze else '正常'}"
        )

        self._send(
            webhook,
            title,
            desc,
            color_map.get(decision.color, 0)
        )
