import os
import requests
from datetime import datetime, timezone
from risk_policy import resolve_risk

DISCORD_WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")
DISCORD_WEBHOOK_BLACK_SWAN = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

def _send(embed, webhook):
    if not webhook:
        return
    try:
        requests.post(webhook, json={"embeds": [embed]}, timeout=10)
    except Exception as e:
        print(f"[Notifier] Discord error: {e}")

def notify_risk(level: int, reason: str):
    policy = resolve_risk(level)

    # L1–L2 → 完全靜默
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

        # ✅ 關鍵：交給 Discord 的發文時間（UTC，Discord 會自動轉）
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "fields": [
            {
                "name": "📊 系統行為",
                "value": policy["action"],
                "inline": False
            }
        ],
        "footer": {
            "text": "Quant Guardian · Risk Control"
        }
    }

    _send(embed, webhook)
