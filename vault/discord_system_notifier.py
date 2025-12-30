# Discord 系統訊息發送器（含防重複）

import json
import os
import time
import requests

STATE_PATH = r"E:\Quant-Vault\TEMP_CACHE\system_audit_state.json"
COOLDOWN_SECONDS = 90 * 60  # 90 分鐘


def _load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def send_system_message(webhook_url: str, fingerprint: str, content: str):
    now = int(time.time())
    state = _load_state()

    last = state.get(fingerprint)
    if last and now - last < COOLDOWN_SECONDS:
        return False  # 重複訊息，阻止發送

    resp = requests.post(webhook_url, json={"content": content}, timeout=10)
    resp.raise_for_status()

    state[fingerprint] = now
    _save_state(state)
    return True
