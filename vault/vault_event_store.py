import os
import json
from datetime import datetime
from writer import safe_write

VAULT_ROOT = r"E:\Quant-Vault"


def write_event(event_type: str, payload: dict) -> bool:
    ts = datetime.utcnow().isoformat()
    record = {
        "timestamp": ts,
        "type": event_type,
        "payload": payload
    }

    path = os.path.join(
        VAULT_ROOT,
        "TEMP_CACHE",
        "events",
        f"{event_type}_{ts}.json"
    )

    return safe_write(path, json.dumps(record, ensure_ascii=False, indent=2))
