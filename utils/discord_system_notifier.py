import json
import os
import time
import urllib.request
from typing import Dict, Optional

# ==============================
# 系統訊息狀態（只存指紋與時間）
# ==============================

_COOLDOWN_SECONDS = 90 * 60  # 90 分鐘


def _get_state_path() -> Optional[str]:
    """
    從環境變數取得 system audit 狀態儲存位置
    （避免任何硬編碼路徑）
    """
    return os.environ.get("SYSTEM_AUDIT_STATE_PATH")


def _load_state() -> Dict[str, int]:
    path = _get_state_path()
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state: Dict[str, int]) -> None:
    path = _get_state_path()
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ==============================
# Discord I/O（唯一實際送出）
# ==============================

def _post_to_discord(webhook_url: str, content: str) -> bool:
    payload = {"content": content}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

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


def _get_webhook_url(env_key: str) -> Optional[str]:
    if not env_key or not isinstance(env_key, str):
        return None
    return os.environ.get(env_key)


# ==============================
# 對外 API（含防重複鐵律）
# ==============================

def send_system_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    系統 / 總結 / 安全中止訊息
    - 防 90 分鐘重複
    - 不做任何語意判斷
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False

    now = int(time.time())
    state = _load_state()

    last = state.get(fingerprint)
    if last and now - last < _COOLDOWN_SECONDS:
        return False

    ok = _post_to_discord(url, content)
    if ok:
        state[fingerprint] = now
        _save_state(state)

    return ok


def send_market_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    市場訊息（TW / US / JP / CRYPTO）
    - 是否防重複由上層決定
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False
    return _post_to_discord(url, content)


def send_black_swan_message(webhook: str, fingerprint: str, content: str) -> bool:
    """
    黑天鵝事件訊息
    - 仍走同一 I/O
    """
    url = _get_webhook_url(webhook)
    if not url:
        return False
    return _post_to_discord(url, content)
