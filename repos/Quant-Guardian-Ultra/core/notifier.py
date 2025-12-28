import os
import json
import requests
from datetime import datetime


class DiscordNotifier:
    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
        }

    def _color_code(self, color: str) -> int:
        # Discord embed color (decimal)
        return {
            "綠": 0x2ECC71,
            "黃": 0xF1C40F,
            "紅": 0xE74C3C,
        }.get(color, 0xF1C40F)

    def send(self, *, kind: str, title: str, message: str, color: str):
        webhook = self.webhooks.get(kind)

        if not webhook:
            print(f"[WARN] Discord Webhook 未設定（{kind}）")
            return

        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": self._color_code(color),
                    "footer": {
                        "text": f"Quant-Orchestrator • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                    },
                }
            ]
        }

        try:
            r = requests.post(
                webhook,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if r.status_code >= 400:
                print(f"[WARN] Discord 回傳錯誤 {r.status_code}")
        except Exception as e:
            print(f"[WARN] Discord 發送失敗：{e}")
