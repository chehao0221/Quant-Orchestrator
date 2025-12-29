import json
from pathlib import Path
from datetime import datetime, timedelta

VAULT_DIR = Path("E:/Quant-Vault/LOCKED_RAW/black_swan")
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def _event_path(event_id: str) -> Path:
    return VAULT_DIR / f"{event_id}.json"

def exists_recent(event_id: str, minutes: int = 90) -> bool:
    path = _event_path(event_id)
    if not path.exists():
        return False

    data = json.loads(path.read_text(encoding="utf-8"))
    ts = datetime.fromisoformat(data["timestamp"])
    return datetime.utcnow() - ts < timedelta(minutes=minutes)

def write_event(payload: dict):
    path = _event_path(payload["id"])
    payload["timestamp"] = datetime.utcnow().isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
