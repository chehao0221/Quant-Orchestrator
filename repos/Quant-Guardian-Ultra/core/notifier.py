import requests
import os

class Notifier:
    def __init__(self):
        self.webhooks = {
            "tw": os.getenv("DISCORD_TW_STOCK"),
            "us": os.getenv("DISCORD_US_STOCK"),
            "swan": os.getenv("DISCORD_BLACK_SWAN"),
            "news": os.getenv("DISCORD_GENERAL_NEWS")
        }

    def send(self, channel_type, title, msg, color=0x3498db):
        url = self.webhooks.get(channel_type)
        if not url:
            return False

        payload = {
            "embeds": [{
                "title": title,
                "description": msg,
                "color": color,
                "footer": {"text": "Quant-Guardian-Ultra"}
            }]
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            return r.status_code == 204
        except Exception:
            return False
