import os
import json
from datetime import datetime
from typing import Dict, Any

VAULT_ROOT = r"E:\Quant-Vault"
EVENT_DIR = os.path.join(VAULT_ROOT, "LOG", "events")

os.makedirs(EVENT_DIR, exist_ok=True)

def record_event(
    event_type: str,
    payload: Dict[str, Any],
    fingerprint: str
):
    """
    系統唯一合法事件寫入器
    - 用於：AI 預測、黑天鵝、系統中止、回測
    """

    event = {
        "event_type": event_type,
        "fingerprint": fingerprint,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    }

    filename = f"{event_type}_{fingerprint}.json"
    path = os.path.join(EVENT_DIR, filename)

    # 防止重複事件覆寫
    if os.path.exists(path):
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)

    return True
