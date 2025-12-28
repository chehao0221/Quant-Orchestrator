# core/notifier.py
import os
import requests
from risk_policy import resolve_risk, now_ts

DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")
DISCORD_WEBHOOK_BLACK_SWAN = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

def _send(embed: dict, webhook: str):
    if not webhook:
        return
    try:
        requests.post(
            webhook,
            json={"embeds": [embed]},
            timeout=10
        )
    except Exception as e:
        print(f"[Notifier] Discord send failed: {e}")

def notify_risk(level: int, reason: str):
    policy = resolve_risk(level)

    # L1–L2 → 完全不顯示
    if not policy["show"]:
        return

    if level == 3:
        title = "🟡 風險觀察（L3）"
        webhook = DISCORD_WEBHOOK_GENERAL
    else:
        title = "🔴 黑天鵝事件（L4+）"
        webhook = DISCORD_WEBHOOK_BLACK_SWAN

    embed = {
        "title": title,
        "description": reason,
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

    _send(embed, webhook)
