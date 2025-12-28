import os
import requests
from datetime import datetime

WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")
WEBHOOK_BLACK_SWAN = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

COLORS = {
    "GREEN": 0x2ecc71,
    "YELLOW": 0xf1c40f,
    "RED": 0xe74c3c,
}

def send(webhook, title, description, color):
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

def notify(level, message):
    if level == "GREEN":
        send(WEBHOOK_GENERAL, "🟢 Guardian 狀態恢復穩定", message, COLORS["GREEN"])
    elif level == "YELLOW":
        send(WEBHOOK_GENERAL, "🟡 Guardian 風控警戒（L3）", message, COLORS["YELLOW"])
    elif level == "RED":
        send(WEBHOOK_BLACK_SWAN, "🔴 Guardian 黑天鵝公告（L4）", message, COLORS["RED"])
