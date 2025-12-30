import os
import json
from datetime import datetime
from writer import safe_write

VAULT_ROOT = r"E:\Quant-Vault"


def write_black_swan_event(event: dict) -> bool:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    path = os.path.join(
        VAULT_ROOT,
        "LOCKED_RAW",
        "black_swan",
        f"event_{ts}.json"
    )

    return safe_write(path, json.dumps(event, ensure_ascii=False, indent=2))
