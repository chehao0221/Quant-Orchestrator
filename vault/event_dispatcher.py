import os
import requests
from .vault_event_store import exists_recent, write_event

WEBHOOK_GENERAL = os.getenv("DISCORD_WEBHOOK_GENERAL")
WEBHOOK_BLACK = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

def dispatch(event: dict):
    if exists_recent(event["id"]):
        return

    webhook = (
        WEBHOOK_BLACK
        if event["event_type"] == "BLACK_SWAN"
        else WEBHOOK_GENERAL
    )

    if not webhook:
        return

    msg = f"🚨 {event['title']}\n來源：{event['source']}"
    requests.post(webhook, json={"content": msg[:1900]}, timeout=10)

    write_event(event)
