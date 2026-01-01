import hashlib
import json
from pathlib import Path

STATE_FILE = Path("TEMP_CACHE/notify_dedupe.json")

def should_send(channel: str, message: str) -> bool:
    h = hashlib.sha256(f"{channel}:{message}".encode()).hexdigest()

    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    else:
        state = {}

    if h in state:
        return False

    state[h] = True
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return True
