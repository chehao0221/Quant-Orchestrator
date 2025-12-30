# Quant-Orchestrator/utils/discord_notifier.py
# Discord 發送唯一 I/O 入口（封頂最終版）

import json
import os
import urllib.request
from typing import Optional


def _get_webhook_url(env_key: str) -> Optional[str]:
    """
    從環境變數取得 Discord webhook URL
    """
    if not env_key or not isinstance(env_key, str):
        return None
    return os.environ.get(env_key)


def _post_to_discord(webhook_url: str, content: str) -> bool:
    """
    實際送出 HTTP POST
    """
    payload = {"content": content}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


# ---------- 對外 API ----------

def send_system_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    發送系統 / 最終總結訊息
    webhook: 環境變數名稱（如 DISCORD_WEBHOOK_GENERAL）
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False
    return _post_to_discord(url, content)


def send_market_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    發送市場專屬訊息（TW / US / JP / CRYPTO）
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False
    return _post_to_discord(url, content)


def send_black_swan_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    發送黑天鵝事件訊息
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False
    return _post_to_discord(url, content)
