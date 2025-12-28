# Discord Notifier (Red / Yellow / Green)

import os
import json
import requests

WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")

COLOR_MAP = {
    "GREEN": 3066993,
    "YELLOW": 15105570,
    "RED": 15158332
}

class Notifier:
    def send(self, payload):
        if not payload:
            return

        data = {
            "embeds": [{
                "title": payload["title"],
                "description": payload["message"],
                "color": COLOR_MAP[payload["status"]],
                "fields": [
                    {"name": "風險等級", "value": payload["risk_level"], "inline": True},
                    {"name": "系統狀態", "value": payload["status"], "inline": True},
                ],
                "footer": {"text": "Quant-Orchestrator Guardian"},
            }]
        }

        if WEBHOOK_GENERAL:
            requests.post(WEBHOOK_GENERAL, json=data)
