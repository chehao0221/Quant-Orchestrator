# core/notifier.py
import os
import requests
from risk_policy import resolve_risk, now_ts

DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")
DISCORD_WEBHOOK_BLACK_SWAN = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

def send_discord(embed: dict, webhook: str):
    if not webhook:
        return
    requests.post(webhook, json={"embeds": [embed]}, timeout=10)

def notify_risk(level: int, reason: str):
    policy = resolve_risk(level)

    # L1–L2 → 完全不通知
    if not policy["show"]:
        return

    # L3 / L4+
    title = "🟡 風險觀察（L3）" if level == 3 else "🔴 黑天鵝事件（L4+）"
    desc = reason

    embed = {
        "title": title,
        "description": desc,
        "color": policy["color"],
        "fields": [
            {
                "name": "🕒 事件時間",
                "value": now_ts(),
                "inline": False
            },
            {
                "name": "📊 系統行為",
                "value": policy["action"],
                "inline": False
            }
        ],
        "footer": {
            "text": "Quant Guardian · Risk Control Layer"
        }
    }

    # L3 → GENERAL
    if level == 3:
        send_discord(embed, DISCORD_WEBHOOK_GENERAL)
        return

    # L4+ → BLACK_SWAN
    send_discord(embed, DISCORD_WEBHOOK_BLACK_SWAN)
