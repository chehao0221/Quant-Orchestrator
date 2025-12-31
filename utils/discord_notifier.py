# Discord 發送唯一 I/O 入口（封頂最終版）
# 職責：所有 Discord 對外輸出
# ❌ 不決策 ❌ 不學習 ❌ 不寫 Vault（只讀狀態）
# ✅ 防重複發送（fingerprint）
# ✅ 環境變數管理 webhook

import json
import os
import time
import urllib.request
from typing import Optional

# 防重複狀態（僅暫存，不影響決策）
STATE_PATH = os.path.join(
    os.environ.get("VAULT_ROOT", ""),
    "TEMP_CACHE",
    "system_audit_state.json"
)

COOLDOWN_SECONDS = 90 * 60  # 90 分鐘


# --------------------------------------------------

def _load_state() -> dict:
    if not STATE_PATH or not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    if not STATE_PATH:
        return
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _get_webhook_url(env_key: str) -> Optional[str]:
    if not env_key or not isinstance(env_key, str):
        return None
    return os.environ.get(env_key)


def _post(webhook_url: str, content: str) -> bool:
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


# --------------------------------------------------
# 對外 API（唯一出口）
# --------------------------------------------------

def send_system_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    系統 / 總結訊息（含防重複）
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False

    now = int(time.time())
    state = _load_state()
    last = state.get(fingerprint)

    if last and now - last < COOLDOWN_SECONDS:
        return False

    ok = _post(url, content)
    if ok:
        state[fingerprint] = now
        _save_state(state)

    return ok


def send_market_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    市場訊息（TW / US / JP / CRYPTO）
    """
    return send_system_message(webhook, fingerprint, content)


def send_black_swan_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    黑天鵝專用訊息
    """
    return send_system_message(webhook, fingerprint, content)
