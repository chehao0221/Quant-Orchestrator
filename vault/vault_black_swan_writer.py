from pathlib import Path
import json
from datetime import datetime

def record_black_swan(event: dict):
    root = Path("E:/Quant-Vault/LOCKED_RAW/black_swan")
    root.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    path = root / f"{ts}.json"

    path.write_text(
        json.dumps(event, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
